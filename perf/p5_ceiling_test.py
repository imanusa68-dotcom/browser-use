"""Direct unit-style test of _wait_network_idle_fast (P5):
(1) permanently pending request -> must hit ceiling and log perf.fallback: network_idle_ceiling;
(2) request clearing after 150ms -> must exit via quiet window (<ceiling);
(3) long-lived websocket pending -> filtered by _is_long_lived_request, exit after quiet window.
Monkeypatches _get_pending_network_requests on the live DOMWatchdog instance.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

captured = []


class Cap(logging.Handler):
	def emit(self, r):
		m = r.getMessage()
		if 'network_idle' in m or 'perf.fallback' in m:
			captured.append(m)


async def main():
	logging.getLogger().addHandler(Cap(level=logging.DEBUG))
	logging.getLogger('browser_use').setLevel(logging.DEBUG)
	from browser_use.browser import BrowserProfile, BrowserSession
	from browser_use.browser.events import NavigateToUrlEvent
	from browser_use.browser.views import NetworkRequest

	s = BrowserSession(browser_profile=BrowserProfile(headless=True, keep_alive=False))
	await s.start()
	ev = s.event_bus.dispatch(NavigateToUrlEvent(url='http://127.0.0.1:8901/search'))
	await ev
	await asyncio.sleep(0.3)

	dw = s._dom_watchdog
	assert dw is not None, 'DOMWatchdog not found'

	fake_pending = [NetworkRequest(url='http://x/api', method='GET', loading_duration_ms=100, resource_type='fetch')]

	async def always_pending():
		return list(fake_pending)

	dw._get_pending_network_requests = always_pending
	t0 = time.monotonic()
	await dw._wait_network_idle_fast()
	dt1 = time.monotonic() - t0
	print(f'case1 permanently-pending: wall={dt1 * 1000:.0f}ms ceiling_logged={any("network_idle_ceiling" in m for m in captured)}')

	captured.clear()
	t_start = time.monotonic()

	async def clears():
		return list(fake_pending) if time.monotonic() - t_start < 0.15 else []

	dw._get_pending_network_requests = clears
	t0 = time.monotonic()
	await dw._wait_network_idle_fast()
	dt2 = time.monotonic() - t0
	print(
		f'case2 clears-at-150ms: wall={dt2 * 1000:.0f}ms (expect ~250-350ms) '
		f'ceiling_logged={any("network_idle_ceiling" in m for m in captured)}'
	)

	captured.clear()
	ws = [NetworkRequest(url='wss://x/live', method='GET', loading_duration_ms=5000, resource_type='websocket')]

	async def ws_pending():
		return list(ws)

	dw._get_pending_network_requests = ws_pending
	t0 = time.monotonic()
	await dw._wait_network_idle_fast()
	dt3 = time.monotonic() - t0
	print(
		f'case3 websocket-only: wall={dt3 * 1000:.0f}ms (expect ~100-160ms) '
		f'ceiling_logged={any("network_idle_ceiling" in m for m in captured)}'
	)

	await s.kill()


asyncio.run(main())
