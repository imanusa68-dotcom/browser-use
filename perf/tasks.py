"""Benchmark task set with programmatic success checks (not 'agent said done')."""

BASE = 'http://127.0.0.1:8901'

# Each task: id, prompt, checker(final_result_text, agent_history) -> bool
TASKS = [
	{
		'id': 'search_extract',
		'prompt': f'Go to {BASE}/search , search for "Tools" and report how many results were found.',
		'check': lambda text, hist: '20' in (text or ''),
	},
	{
		'id': 'form_fill',
		'prompt': (
			f'Go to {BASE}/form and register with name "Alice Smith", email "alice@example.com", '
			f'country "Germany". Report the confirmation message.'
		),
		'check': lambda text, hist: 'alice smith' in (text or '').lower() and 'germany' in (text or '').lower(),
	},
	{
		'id': 'table_paginate',
		'prompt': (
			f'Go to {BASE}/table?page=1 . Find the price of "Product 25" (you may need to use pagination) and report it.'
		),
		'check': lambda text, hist: '85' in (text or ''),
	},
	{
		'id': 'login_flow',
		'prompt': (
			f'Go to {BASE}/login , sign in with username "admin" and password "secret123", then report the account balance.'
		),
		'check': lambda text, hist: '4521.77' in (text or '') or '4521' in (text or ''),
	},
	{
		'id': 'modal_dismiss',
		'prompt': f'Go to {BASE}/modal , accept the cookie banner, and report the launch code from the article.',
		'check': lambda text, hist: 'falcon-42' in (text or '').lower(),
	},
	{
		'id': 'heavy_dom',
		'prompt': f'Go to {BASE}/heavy and report the magic number shown at the top of the page.',
		'check': lambda text, hist: '7319' in (text or ''),
	},
]

SMOKE_IDS = ['search_extract', 'form_fill', 'heavy_dom']
