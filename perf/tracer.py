"""
Lightweight JSONL span tracer for browser-use performance profiling.

Instruments hot-path functions via monkeypatching (zero code changes to
browser-use itself) and emits one JSON line per span:
  {"name", "t_start", "dur_ms", "task", "step", "attrs"}

Usage:
    from perf.tracer import Tracer, instrument
    tracer = Tracer("/path/to/spans.jsonl")
    instrument(tracer)
    ... run agent ...
    tracer.flush()
"""

import functools
import json
import time
from contextlib import contextmanager
from pathlib import Path


class Tracer:
	def __init__(self, out_path: str):
		self.out_path = Path(out_path)
		self.out_path.parent.mkdir(parents=True, exist_ok=True)
		self.spans: list[dict] = []
		self.task_id: str = ''
		self.current_step: int = 0
		self._t0 = time.monotonic()

	def emit(self, name: str, start: float, dur_ms: float, **attrs):
		self.spans.append(
			{
				'name': name,
				't_start': round(start - self._t0, 4),
				'dur_ms': round(dur_ms, 2),
				'task': self.task_id,
				'step': self.current_step,
				'attrs': attrs,
			}
		)

	@contextmanager
	def span(self, name: str, **attrs):
		s = time.monotonic()
		try:
			yield
		finally:
			self.emit(name, s, (time.monotonic() - s) * 1000, **attrs)

	def flush(self):
		with open(self.out_path, 'a') as f:
			for s in self.spans:
				f.write(json.dumps(s) + '\n')
		self.spans = []


def _wrap_async(tracer: Tracer, name: str, fn, attr_fn=None):
	@functools.wraps(fn)
	async def wrapper(*args, **kwargs):
		s = time.monotonic()
		ok = True
		try:
			return await fn(*args, **kwargs)
		except Exception:
			ok = False
			raise
		finally:
			attrs = {'ok': ok}
			if attr_fn:
				try:
					attrs.update(attr_fn(args, kwargs))
				except Exception:
					pass
			tracer.emit(name, s, (time.monotonic() - s) * 1000, **attrs)

	return wrapper


def instrument(tracer: Tracer):
	"""Monkeypatch hot-path functions in browser-use 0.13.8 with tracing spans."""
	import asyncio as _asyncio

	# ---- Agent step phases ----
	from browser_use.agent import service as agent_service

	Agent = agent_service.Agent

	_orig_step = Agent.step

	async def traced_step(self, step_info=None):
		tracer.current_step = self.state.n_steps
		s = time.monotonic()
		try:
			return await _orig_step(self, step_info)
		finally:
			tracer.emit('agent.step', s, (time.monotonic() - s) * 1000)

	Agent.step = traced_step

	Agent._prepare_context = _wrap_async(tracer, 'phase.prepare_context', Agent._prepare_context)
	Agent._get_next_action = _wrap_async(tracer, 'phase.get_next_action', Agent._get_next_action)
	Agent._execute_actions = _wrap_async(tracer, 'phase.execute_actions', Agent._execute_actions)
	Agent.multi_act = _wrap_async(
		tracer, 'phase.multi_act', Agent.multi_act, lambda a, k: {'n_actions': len(a[1] if len(a) > 1 else k.get('actions', []))}
	)

	# LLM call (per-model)
	_orig_gmo = Agent.get_model_output

	async def traced_gmo(self, input_messages):
		s = time.monotonic()
		try:
			return await _orig_gmo(self, input_messages)
		finally:
			# approximate prompt char size
			try:
				chars = sum(len(str(m.content)) for m in input_messages)
			except Exception:
				chars = -1
			tracer.emit('phase.llm_call', s, (time.monotonic() - s) * 1000, prompt_chars=chars, n_msgs=len(input_messages))

	Agent.get_model_output = traced_gmo

	# ---- DOM extraction ----
	from browser_use.dom import service as dom_service

	DomService = dom_service.DomService
	DomService.get_serialized_dom_tree = _wrap_async(tracer, 'dom.get_serialized_dom_tree', DomService.get_serialized_dom_tree)
	DomService.get_dom_tree = _wrap_async(tracer, 'dom.get_dom_tree', DomService.get_dom_tree)
	DomService._get_all_trees = _wrap_async(tracer, 'dom.cdp_get_all_trees', DomService._get_all_trees)
	DomService._get_ax_tree_for_all_frames = _wrap_async(tracer, 'dom.cdp_ax_tree', DomService._get_ax_tree_for_all_frames)

	# ---- DOM watchdog: state request incl. screenshot ----
	from browser_use.browser.watchdogs import dom_watchdog as dw

	DOMWatchdog = dw.DOMWatchdog
	DOMWatchdog.on_BrowserStateRequestEvent = _wrap_async(
		tracer, 'browser.state_request', DOMWatchdog.on_BrowserStateRequestEvent
	)
	if hasattr(DOMWatchdog, '_capture_clean_screenshot'):
		DOMWatchdog._capture_clean_screenshot = _wrap_async(
			tracer, 'browser.screenshot', DOMWatchdog._capture_clean_screenshot
		)

	# ---- CDP command counting (send_raw on CDPClient) ----
	try:
		from cdp_use.client import CDPClient

		_orig_send_raw = CDPClient.send_raw

		@functools.wraps(_orig_send_raw)
		async def traced_send_raw(self, method, params=None, session_id=None):
			s = time.monotonic()
			try:
				return await _orig_send_raw(self, method, params=params, session_id=session_id)
			finally:
				tracer.emit('cdp.cmd', s, (time.monotonic() - s) * 1000, method=method)

		CDPClient.send_raw = traced_send_raw
	except Exception as e:
		print(f'CDP instrumentation failed: {e}')

	# ---- asyncio.sleep accounting (idle time) ----
	_orig_sleep = _asyncio.sleep

	async def traced_sleep(delay, result=None):
		if delay and delay > 0.001:
			s = time.monotonic()
			try:
				return await _orig_sleep(delay, result)
			finally:
				tracer.emit('idle.sleep', s, (time.monotonic() - s) * 1000, requested_s=delay)
		return await _orig_sleep(delay, result)

	_asyncio.sleep = traced_sleep

	return tracer
