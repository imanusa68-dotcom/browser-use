"""P5 targeted probe: measure the DOMWatchdog pre-snapshot stability wait on
fast vs slow pages, in legacy vs fast_network_idle arms.

For each page (/search fast static, /slow 2s server delay, /delayed_field
1.5s late render) we navigate, then request browser state N times and measure
the wall time of each BrowserStateRequestEvent. We also capture all
`perf.fallback:` log lines (ceiling activations) via a logging handler.

Success criteria checked here (per task instructions):
  (a) fast arm does not overwait on fast pages (state build not slower than legacy);
  (b) fast arm does not leave earlier than readiness on slow pages: after state
      build the page content must already contain the expected marker text;
  (c) network_idle_ceiling fallback fires where it should and is logged.

Usage:
  python perf/p5_targeted.py                       # legacy arm
  BROWSER_USE_FAST_NETWORK_IDLE=1 python perf/p5_targeted.py   # fast arm
"""

import asyncio
import logging
import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE = 'http://127.0.0.1:8901'

FALLBACK_LINES: list[str] = []


class FallbackCapture(logging.Handler):
	def emit(self, record):
		try:
			msg = record.getMessage()
			if 'perf.fallback' in msg or 'fast_network_idle' in msg:
				FALLBACK_LINES.append(msg)
		except Exception:
			pass


async def _navigate(session, url: str):
	from browser_use.browser.events import NavigateToUrlEvent

	event = session.event_bus.dispatch(NavigateToUrlEvent(url=url))
	await event
	await asyncio.sleep(0.2)


async def _state_time(session) -> float:
	from browser_use.browser.events import BrowserStateRequestEvent

	t0 = time.monotonic()
	event = session.event_bus.dispatch(BrowserStateRequestEvent(include_screenshot=False))
	await event.event_result(raise_if_none=True, raise_if_any=True)
	return (time.monotonic() - t0) * 1000


async def _evaluate(session, expression: str):
	cdp_session = await session.get_or_create_cdp_session(focus=True)
	res = await cdp_session.cdp_client.send.Runtime.evaluate(
		params={'expression': expression, 'returnByValue': True},
		session_id=cdp_session.session_id,
	)
	return res.get('result', {}).get('value')


async def main():
	handler = FallbackCapture(level=logging.DEBUG)
	logging.getLogger().addHandler(handler)
	# dom_watchdog logs at DEBUG through session-scoped loggers; force DEBUG on browser_use
	logging.getLogger('browser_use').setLevel(logging.DEBUG)

	from browser_use.browser import BrowserProfile, BrowserSession

	arm = 'fast' if os.environ.get('BROWSER_USE_FAST_NETWORK_IDLE', '') == '1' else 'legacy'
	profile = BrowserProfile(headless=True, keep_alive=False, minimum_wait_page_load_time=0.1)
	session = BrowserSession(browser_profile=profile)
	await session.start()

	report: dict[str, dict] = {}
	try:
		# --- fast static page: state build must not be slower than legacy ---
		await _navigate(session, f'{BASE}/search')
		times = [await _state_time(session) for _ in range(5)]
		report['search_fast_page'] = {'state_ms': [round(t) for t in times], 'p50': round(statistics.median(times))}

		# --- /slow: 2s server delay happens during navigation; after nav the page is
		# static. Check content marker is present right after every state build. ---
		await _navigate(session, f'{BASE}/slow')
		times = []
		markers = []
		for _ in range(3):
			times.append(await _state_time(session))
			markers.append(await _evaluate(session, "document.body.innerText.includes('ZEBRA-9')"))
		report['slow_page'] = {
			'state_ms': [round(t) for t in times],
			'p50': round(statistics.median(times)),
			'marker_present_after_each_build': markers,
		}

		# --- /delayed_field: field renders 1.5s after load. Build state immediately
		# after nav (field may legitimately be absent — that is the AGENT's retry
		# territory), then after the render completes the state must include it.
		# What P5 must NOT do: hang, or return with pending doc when legacy wouldn't. ---
		await _navigate(session, f'{BASE}/delayed_field')
		t_immediate = await _state_time(session)
		await asyncio.sleep(1.6)
		t_after = await _state_time(session)
		has_field = await _evaluate(session, "!!document.getElementById('code')")
		report['delayed_field'] = {
			'state_ms_immediately_after_nav': round(t_immediate),
			'state_ms_after_render': round(t_after),
			'field_present_after_render': has_field,
		}
		# --- pending-request branch: fire an in-flight fetch to /slow (2s server
		# delay) right before the state build. Legacy: blind 0.3s sleep. Fast:
		# polls; the request outlives the 0.5s ceiling -> network_idle_ceiling
		# fallback must fire and be logged; wall time ~0.5s (not worse than SR). ---
		await _navigate(session, f'{BASE}/search')
		cdp_session = await session.get_or_create_cdp_session(focus=True)
		await cdp_session.cdp_client.send.Runtime.evaluate(
			params={'expression': "fetch('/slow?bust=' + Math.random())"},
			session_id=cdp_session.session_id,
		)
		t_pending = await _state_time(session)
		report['pending_slow_fetch'] = {'state_ms_with_2s_inflight_fetch': round(t_pending)}

		# --- short in-flight fetch (~250ms via /table): fast arm should exit right
		# after quiet window instead of the full blind 0.3s. ---
		await cdp_session.cdp_client.send.Runtime.evaluate(
			params={'expression': "fetch('/table?page=1&bust=' + Math.random())"},
			session_id=cdp_session.session_id,
		)
		t_short = await _state_time(session)
		report['pending_short_fetch'] = {'state_ms_with_short_inflight_fetch': round(t_short)}
	finally:
		try:
			await session.kill()
		except Exception:
			pass

	print(f'\n===== P5 targeted report (arm={arm}) =====')
	for k, v in report.items():
		print(f'{k}: {v}')
	fallback_hits = [line for line in FALLBACK_LINES if 'network_idle' in line]
	print(f'network_idle log lines captured: {len(fallback_hits)}')
	for line in fallback_hits[:10]:
		print(f'  {line}')


if __name__ == '__main__':
	asyncio.run(main())
