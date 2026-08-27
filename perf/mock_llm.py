"""Deterministic scripted LLM implementing browser-use BaseChatModel protocol.

Purpose: reproducible A/B benchmarking of the browser/framework side.
- Rule-based policy parses the <browser_state> user message (element lines like
  `[12]<input name=q />`) and emits valid AgentOutput actions.
- Synthetic latency model: TTFT + prompt_tokens/prefill_tps + out_tokens/decode_tps,
  so prompt-size optimizations show up in measured latency exactly like with a
  real provider.

Env knobs:
  MOCK_TTFT_MS      default 700   (network + queueing + first token)
  MOCK_PREFILL_TPS  default 4000  (prompt tokens/sec)
  MOCK_DECODE_TPS   default 80    (output tokens/sec)
"""

import asyncio
import os
import re
import time

from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage

ELEM_RE = re.compile(r'\[(\d+)\]<(\w+)([^>]*)>([^<\n]*)', re.M)


def _extract_text(messages: list[BaseMessage]) -> str:
	parts = []
	for m in messages:
		c = m.content
		if isinstance(c, str):
			parts.append(c)
		elif isinstance(c, list):
			for p in c:
				t = getattr(p, 'text', None)
				if t:
					parts.append(t)
	return '\n'.join(parts)


def _browser_state_section(full_text: str) -> str:
	"""Return only the LAST <browser_state>...</browser_state> section to avoid
	matching example element lines from the system prompt."""
	starts = [m.end() for m in re.finditer(r'<browser_state>', full_text)]
	if not starts:
		return full_text
	start = starts[-1]
	end = full_text.find('</browser_state>', start)
	return full_text[start : end if end != -1 else len(full_text)]


def _iter_elements(state: str):
	"""Yield (index, tag, searchable_text) where searchable_text includes the element
	line attrs/text plus any immediately-following indented text lines (label text)."""
	lines = state.splitlines()
	for i, line in enumerate(lines):
		m = re.match(r'\s*(?:\|[A-Z()a-z]+\|)?\*?\[(\d+)\]<(\w+)([^>]*)>([^<\n]*)', line)
		if not m:
			continue
		idx, tag, attrs, text = int(m.group(1)), m.group(2).lower(), m.group(3), m.group(4)
		extra = []
		for j in range(i + 1, min(i + 4, len(lines))):
			nxt = lines[j]
			if re.match(r'\s*(?:\|[A-Z()a-z]+\|)?\*?\[\d+\]<', nxt):
				break
			if nxt.strip():
				extra.append(nxt.strip())
		yield idx, tag, (attrs + ' ' + text + ' ' + ' '.join(extra)).lower()


def _find(state: str, tag: str, must: list[str] | None = None) -> int | None:
	"""Find selector index of first element with tag whose line (incl. label text) contains all `must` substrings."""
	for idx, t, searchable in _iter_elements(state):
		if t == tag.lower() and all(s.lower() in searchable for s in (must or [])):
			return idx
	return None


class ScriptedPolicy:
	"""Per-task rule-based action policy. Returns list of action dicts."""

	def __init__(self, task_id: str):
		self.task_id = task_id
		self.phase = 0

	def decide(self, full_text: str) -> tuple[list[dict], str]:
		base = 'http://127.0.0.1:8901'
		t = _browser_state_section(full_text)
		low = t.lower()

		def done(msg):
			return [{'done': {'text': msg, 'success': True}}], msg

		if self.task_id == 'search_extract':
			if 'results found' in low:
				m = re.search(r'(\d+) results found', t)
				return done(f'{m.group(1)} results found for Tools.' if m else 'results found')
			if '/search' not in low or _find(t, 'input') is None:
				return [{'navigate': {'url': f'{base}/search'}}], 'navigate'
			inp = _find(t, 'input')
			btn = _find(t, 'button', ['search'])
			acts = []
			if inp is not None:
				acts.append({'input': {'index': inp, 'text': 'Tools', 'clear': True}})
			if btn is not None:
				acts.append({'click': {'index': btn}})
			return acts, 'search'

		if self.task_id == 'form_fill':
			if 'success: registered' in low:
				m = re.search(r'SUCCESS: registered ([^<\n]+)', t)
				return done(f'Confirmation: {m.group(1).strip() if m else "registered"}')
			name_i = _find(t, 'input', ['name=name']) or _find(t, 'input', ['name'])
			if name_i is None:
				return [{'navigate': {'url': f'{base}/form'}}], 'navigate'
			email_i = _find(t, 'input', ['email'])
			sel_i = _find(t, 'select')
			btn = _find(t, 'button', ['register'])
			acts = [
				{'input': {'index': name_i, 'text': 'Alice Smith', 'clear': True}},
			]
			if email_i is not None:
				acts.append({'input': {'index': email_i, 'text': 'alice@example.com', 'clear': True}})
			if sel_i is not None:
				acts.append({'select_dropdown': {'index': sel_i, 'text': 'Germany'}})
			if btn is not None:
				acts.append({'click': {'index': btn}})
			return acts, 'fill form'

		if self.task_id == 'table_paginate':
			if 'product 25' in low:
				return done('Product 25 costs $85.')
			nxt = _find(t, 'a', ['next'])
			if nxt is None:
				return [{'navigate': {'url': f'{base}/table?page=1'}}], 'navigate'
			return [{'click': {'index': nxt}}], 'next page'

		if self.task_id == 'login_flow':
			if 'balance' in low and '4521' in t:
				return done('Account balance is $4521.77.')
			user_i = _find(t, 'input', ['username'])
			if user_i is None:
				return [{'navigate': {'url': f'{base}/login'}}], 'navigate'
			pass_i = _find(t, 'input', ['password'])
			btn = _find(t, 'button', ['sign in']) or _find(t, 'button')
			acts = [{'input': {'index': user_i, 'text': 'admin', 'clear': True}}]
			if pass_i is not None:
				acts.append({'input': {'index': pass_i, 'text': 'secret123', 'clear': True}})
			if btn is not None:
				acts.append({'click': {'index': btn}})
			return acts, 'login'

		if self.task_id == 'modal_dismiss':
			if 'falcon-42' in low and 'accept cookies' not in low:
				return done('The launch code is FALCON-42.')
			btn = _find(t, 'button', ['accept'])
			if btn is not None:
				return [{'click': {'index': btn}}], 'accept cookies'
			if 'falcon-42' in low:
				return done('The launch code is FALCON-42.')
			return [{'navigate': {'url': f'{base}/modal'}}], 'navigate'

		if self.task_id == 'heavy_dom':
			m = re.search(r'Magic number: (\d+)', t)
			if m:
				return done(f'The magic number is {m.group(1)}.')
			return [{'navigate': {'url': f'{base}/heavy'}}], 'navigate'

		return done('unknown task')


class MockScriptedLLM:
	"""BaseChatModel-compatible deterministic LLM with synthetic latency."""

	_verified_api_keys = True
	model = 'mock-scripted'

	def __init__(self, task_id: str):
		self.policy = ScriptedPolicy(task_id)
		self.ttft = float(os.environ.get('MOCK_TTFT_MS', '700')) / 1000
		self.prefill_tps = float(os.environ.get('MOCK_PREFILL_TPS', '4000'))
		self.decode_tps = float(os.environ.get('MOCK_DECODE_TPS', '80'))
		self.calls = 0

	@property
	def provider(self) -> str:
		return 'mock'

	@property
	def name(self) -> str:
		return self.model

	@property
	def model_name(self) -> str:
		return self.model

	async def ainvoke(self, messages: list[BaseMessage], output_format=None, **kwargs):
		self.calls += 1
		text = _extract_text(messages)
		if os.environ.get('MOCK_DEBUG'):
			with open('/tmp/mock_debug.txt', 'a') as f:
				f.write(f'\n===== CALL {self.calls} =====\n{_browser_state_section(text)[:3000]}\n')
		prompt_tokens = max(1, len(text) // 4)

		actions, goal = self.policy.decide(text)

		out = {
			'thinking': None,
			'evaluation_previous_goal': 'ok',
			'memory': goal[:60],
			'next_goal': goal[:60],
			'action': actions,
		}
		import json as _json

		out_tokens = max(1, len(_json.dumps(out)) // 4)

		# Synthetic latency: TTFT + prefill + decode
		latency = self.ttft + prompt_tokens / self.prefill_tps + out_tokens / self.decode_tps
		t0 = time.monotonic()
		await asyncio.sleep(latency)

		usage = ChatInvokeUsage(
			prompt_tokens=prompt_tokens,
			prompt_cached_tokens=None,
			prompt_cache_creation_tokens=None,
			prompt_image_tokens=None,
			completion_tokens=out_tokens,
			total_tokens=prompt_tokens + out_tokens,
		)

		if output_format is None:
			return ChatInvokeCompletion(completion=_json.dumps(out), usage=usage)

		try:
			completion = output_format.model_validate(out)
		except Exception:
			# drop unknown action keys progressively (schema may differ)
			out['action'] = [{'done': {'text': 'fallback', 'success': False}}]
			completion = output_format.model_validate(out)
		return ChatInvokeCompletion(completion=completion, usage=usage)
