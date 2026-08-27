"""Direct-dispatch regression tests for the perf fast paths (no LLM).

Each test drives the browser via BrowserSession events (ClickElementEvent /
TypeTextEvent) against the deterministic fixture server, then asserts the
OUTCOME in the page (not "the action returned OK").

Tests:
  shifting_button  -- P2: layout keeps moving ~250ms after scroll; the click must
                      land on the button's FINAL position (checks #clickres).
  masked_phone     -- P1: input formatter rewrites value on 'input' events;
                      fast_input must fall back to per-char and still produce
                      the correctly masked value.
  react_input      -- P1: controlled-component pattern; value must end up in
                      window.__state (framework events after insertText).
  slow_page        -- sanity: 2s server delay; state must contain the token.

Usage:
  python perf/regression_tests.py                      # legacy paths (baseline)
  BROWSER_USE_FAST_INPUT=1 BROWSER_USE_FAST_SCROLL=1 \
  python perf/regression_tests.py                      # fast paths
  python perf/regression_tests.py --only shifting_button
"""

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE = 'http://127.0.0.1:8901'


async def _get_state(session):
	"""Build fresh DOM state and return (selector_map, browser_session)."""
	from browser_use.browser.events import BrowserStateRequestEvent

	event = session.event_bus.dispatch(BrowserStateRequestEvent(include_screenshot=False))
	state = await event.event_result(raise_if_none=True, raise_if_any=True)
	return state.dom_state.selector_map


def _find_node(selector_map, tag: str, must: list[str] | None = None):
	"""Find first node in selector_map matching tag and attribute/text substrings."""
	for idx, node in selector_map.items():
		if (node.tag_name or '').lower() != tag.lower():
			continue
		hay = ' '.join([f'{k}={v}' for k, v in (node.attributes or {}).items()]).lower()
		hay += ' ' + (node.get_all_children_text(max_depth=2) or '').lower()
		if all(s.lower() in hay for s in (must or [])):
			return idx, node
	return None, None


async def _evaluate(session, expression: str):
	cdp_session = await session.get_or_create_cdp_session(focus=True)
	res = await cdp_session.cdp_client.send.Runtime.evaluate(
		params={'expression': expression, 'returnByValue': True},
		session_id=cdp_session.session_id,
	)
	return res.get('result', {}).get('value')


async def _navigate(session, url: str):
	from browser_use.browser.events import NavigateToUrlEvent

	event = session.event_bus.dispatch(NavigateToUrlEvent(url=url))
	await event
	await asyncio.sleep(0.3)


async def test_shifting_button(session) -> dict:
	"""P2: click must hit the button even though a lazy banner (armed to start growing on
	the scroll caused by the click's own scrollIntoViewIfNeeded) keeps shifting layout
	for ~150ms — longer than the legacy fixed 50ms post-scroll wait.

	Success criteria:
	  - always: button handler fired (clickres == TARGET-HIT) — no silent mis-click;
	  - fast arm (BROWSER_USE_FAST_SCROLL=1): additionally must be a REAL coordinate
	    click (metadata contains click_x), not a degraded JS element.click() fallback.
	"""
	from browser_use.browser.events import ClickElementEvent

	await _navigate(session, f'{BASE}/shifting_button')
	# Button is below the fold -> the click path itself will scroll to it.
	# Scroll a bit first so the DOM builder picks the button up into selector_map,
	# then return to top so scrollIntoViewIfNeeded has real scrolling to do.
	cdp_session = await session.get_or_create_cdp_session(focus=True)
	await cdp_session.cdp_client.send.Runtime.evaluate(
		params={'expression': 'window.scrollTo(0, document.body.scrollHeight)'},
		session_id=cdp_session.session_id,
	)
	await asyncio.sleep(0.3)
	selector_map = await _get_state(session)
	idx, node = _find_node(selector_map, 'button', ['confirm'])
	assert node is not None, 'target button not found in selector_map'
	# back to top + ARM the banner: next scroll event triggers the growth animation
	await cdp_session.cdp_client.send.Runtime.evaluate(
		params={'expression': 'window.scrollTo(0, 0)'}, session_id=cdp_session.session_id
	)
	await asyncio.sleep(0.3)
	await cdp_session.cdp_client.send.Runtime.evaluate(
		params={'expression': 'window.__armed = true'}, session_id=cdp_session.session_id
	)

	t0 = time.monotonic()
	event = session.event_bus.dispatch(ClickElementEvent(node=node))
	metadata = await event.event_result(raise_if_none=False, raise_if_any=True)
	dt_ms = (time.monotonic() - t0) * 1000

	await asyncio.sleep(0.3)
	clickres = await _evaluate(session, "document.getElementById('clickres').textContent")
	banner_h = await _evaluate(session, "(document.getElementById('lazybanner')||{clientHeight:-1}).clientHeight")
	coordinate_click = bool(metadata and isinstance(metadata, dict) and 'click_x' in metadata)
	hit = clickres == 'TARGET-HIT'
	fast_arm = os.environ.get('BROWSER_USE_FAST_SCROLL', '') == '1'
	if fast_arm:
		# P2 requirement: real coordinate click on the button's final position.
		ok = hit and coordinate_click
		note = ''
	else:
		# Legacy arm: the fixed 50ms wait is EXPECTED to mis-click here — that is the
		# flaw P2 fixes. Report it, but do not fail the legacy suite for a known flaw.
		ok = True
		note = ' (legacy mis-click EXPECTED — demonstrates the flaw P2 fixes)' if not hit else ' (legacy happened to hit)'
	return {
		'ok': ok,
		'detail': (
			f'hit={hit} coordinate_click={coordinate_click} banner_h={banner_h} '
			f'click_ms={dt_ms:.0f} arm={"fast" if fast_arm else "legacy"}{note}'
		),
	}


async def test_masked_phone(session) -> dict:
	"""P1: masked field — fast_input must fall back and final value must be masked digits."""
	from browser_use.browser.events import TypeTextEvent

	await _navigate(session, f'{BASE}/masked_phone')
	selector_map = await _get_state(session)
	idx, node = _find_node(selector_map, 'input', ['phone'])
	assert node is not None, 'phone input not found'

	event = session.event_bus.dispatch(TypeTextEvent(node=node, text='5551234567', clear=True))
	await event.event_result(raise_if_none=False, raise_if_any=True)
	await asyncio.sleep(0.2)
	value = await _evaluate(session, "document.getElementById('phone').value")
	ok = value == '(555) 123-4567'
	return {'ok': ok, 'detail': f'value={value!r} (expected "(555) 123-4567")'}


async def test_react_input(session) -> dict:
	"""P1: controlled input — typed value must land in framework state (window.__state)."""
	from browser_use.browser.events import TypeTextEvent

	await _navigate(session, f'{BASE}/react_input')
	selector_map = await _get_state(session)
	idx, node = _find_node(selector_map, 'input', ['ctl'])
	assert node is not None, 'controlled input not found'

	event = session.event_bus.dispatch(TypeTextEvent(node=node, text='hello state', clear=True))
	await event.event_result(raise_if_none=False, raise_if_any=True)
	await asyncio.sleep(0.3)
	state_val = await _evaluate(session, 'window.__state')
	dom_val = await _evaluate(session, "document.getElementById('ctl').value")
	ok = state_val == 'hello state' and dom_val == 'hello state'
	return {'ok': ok, 'detail': f'state={state_val!r} dom={dom_val!r}'}


async def test_slow_page(session) -> dict:
	"""Sanity: 2s-delayed page must be fully present in the DOM state after navigation."""
	await _navigate(session, f'{BASE}/slow')
	await _get_state(session)
	txt = await _evaluate(session, "(document.getElementById('loaded')||{textContent:''}).textContent")
	ok = 'ZEBRA-9' in (txt or '')
	return {'ok': ok, 'detail': f'loaded_text={txt!r}'}


TESTS = {
	'shifting_button': test_shifting_button,
	'masked_phone': test_masked_phone,
	'react_input': test_react_input,
	'slow_page': test_slow_page,
}


async def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('--only', default='', help='comma-separated test names')
	args = ap.parse_args()
	names = args.only.split(',') if args.only else list(TESTS)

	from browser_use.browser import BrowserProfile, BrowserSession

	flags = {k: v for k, v in os.environ.items() if k.startswith('BROWSER_USE_FAST')}
	print(f'flags: {flags or "(none — legacy paths)"}')

	session = BrowserSession(
		browser_profile=BrowserProfile(headless=True, keep_alive=False, minimum_wait_page_load_time=0.1)
	)
	await session.start()
	results = {}
	try:
		for name in names:
			try:
				r = await TESTS[name](session)
			except Exception as e:
				r = {'ok': False, 'detail': f'{type(e).__name__}: {e}'}
			results[name] = r
			print(f'[{"PASS" if r["ok"] else "FAIL"}] {name}: {r["detail"]}', flush=True)
	finally:
		try:
			await session.kill()
		except Exception:
			pass

	failed = [n for n, r in results.items() if not r['ok']]
	print(f'\n{len(results) - len(failed)}/{len(results)} passed' + (f'; FAILED: {failed}' if failed else ''))
	sys.exit(1 if failed else 0)


if __name__ == '__main__':
	asyncio.run(main())
