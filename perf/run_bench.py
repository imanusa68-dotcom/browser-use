"""Benchmark runner for browser-use performance work.

Usage:
  python perf/run_bench.py --label baseline --runs 3 [--tasks search_extract,form_fill] [--profile fast]

Outputs:
  perf/results/<label>/spans_<task>_<run>.jsonl   -- per-span traces
  perf/results/<label>/summary.json               -- aggregated metrics
  perf/results/<label>/report.md                  -- human-readable report
"""

import argparse
import asyncio
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from perf.tasks import TASKS
from perf.tracer import Tracer, instrument

RESULTS = Path(__file__).parent / 'results'


def wilson_ci(successes: int, n: int, z: float = 1.96):
	if n == 0:
		return (0.0, 0.0)
	p = successes / n
	denom = 1 + z**2 / n
	center = (p + z**2 / (2 * n)) / denom
	margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
	return (max(0, center - margin), min(1, center + margin))


def build_agent(task_prompt: str, profile: str, tracer: Tracer, task_id: str = '', llm_kind: str = 'mock'):
	from browser_use import Agent
	from browser_use.browser import BrowserProfile

	if llm_kind == 'mock':
		from perf.mock_llm import MockScriptedLLM

		llm = MockScriptedLLM(task_id)
	else:
		from browser_use.llm.openai.chat import ChatOpenAI

		llm = ChatOpenAI(
			model=os.environ.get('BENCH_MODEL', 'gpt-5-mini'),
			base_url=os.environ.get('OPENAI_BASE_URL'),
			api_key=os.environ.get('OPENAI_API_KEY'),
			temperature=None,  # proxy may reject temperature for reasoning models
			seed=42,
		)

	bp_kwargs = dict(headless=True, disable_security=False, keep_alive=False)
	agent_kwargs = dict(use_judge=False, calculate_cost=True, enable_planning=True)

	if profile == 'fast':
		# knobs applied via env flags read by patched code; presets set here
		bp_kwargs.update(
			minimum_wait_page_load_time=float(os.environ.get('FAST_MIN_WAIT', '0.05')),
			wait_for_network_idle_page_load_time=float(os.environ.get('FAST_NET_IDLE', '0.1')),
			wait_between_actions=float(os.environ.get('FAST_BETWEEN', '0.0')),
			highlight_elements=False,
		)
		agent_kwargs.update(
			flash_mode=os.environ.get('FAST_FLASH', '0') == '1',
			use_thinking=os.environ.get('FAST_THINKING', '1') == '1',
			enable_planning=os.environ.get('FAST_PLANNING', '1') == '1',
			use_vision=os.environ.get('FAST_VISION', 'auto') if os.environ.get('FAST_VISION') in ('auto',) else (os.environ.get('FAST_VISION', '1') == '1'),
		)

	profile_obj = BrowserProfile(**bp_kwargs)
	agent = Agent(
		task=task_prompt,
		llm=llm,
		browser_profile=profile_obj,
		max_actions_per_step=5,
		**agent_kwargs,
	)
	return agent


async def run_one(task: dict, profile: str, label: str, run_idx: int, llm_kind: str = 'mock') -> dict:
	out_dir = RESULTS / label
	out_dir.mkdir(parents=True, exist_ok=True)
	tracer = Tracer(str(out_dir / f'spans_{task["id"]}_{run_idx}.jsonl'))
	tracer.task_id = task['id']
	instrument(tracer)

	agent = build_agent(task['prompt'], profile, tracer, task_id=task['id'], llm_kind=llm_kind)
	t0 = time.monotonic()
	err = None
	final_text = None
	n_steps = 0
	usage_summary = {}
	try:
		history = await asyncio.wait_for(agent.run(max_steps=12), timeout=420)
		final_text = history.final_result()
		n_steps = len(history.history)
		try:
			u = await agent.token_cost_service.get_usage_summary()
			usage_summary = {
				'prompt_tokens': u.total_prompt_tokens,
				'completion_tokens': u.total_completion_tokens,
				'cost': u.total_cost,
				'invocations': u.entry_count,
			}
		except Exception:
			pass
	except Exception as e:
		err = f'{type(e).__name__}: {e}'
	t_total = time.monotonic() - t0
	try:
		await agent.close()
	except Exception:
		pass
	tracer.flush()

	success = False
	if err is None:
		try:
			success = bool(task['check'](final_text, None))
		except Exception:
			success = False

	return {
		'task': task['id'],
		'run': run_idx,
		'success': success,
		'error': err,
		't_task_s': round(t_total, 2),
		'n_steps': n_steps,
		'final_text': (final_text or '')[:300],
		**usage_summary,
	}


def analyze_spans(label: str) -> dict:
	"""Aggregate phase timings across all runs of a label."""
	out_dir = RESULTS / label
	phases: dict[str, list[float]] = {}
	cdp_counts: list[int] = []
	sleep_total: list[float] = []
	for f in out_dir.glob('spans_*.jsonl'):
		cdp_n = 0
		sleep_ms = 0.0
		for line in f.read_text().splitlines():
			s = json.loads(line)
			phases.setdefault(s['name'], []).append(s['dur_ms'])
			if s['name'] == 'cdp.cmd':
				cdp_n += 1
			if s['name'] == 'idle.sleep':
				sleep_ms += s['dur_ms']
		cdp_counts.append(cdp_n)
		sleep_total.append(sleep_ms)

	def pct(vals, p):
		if not vals:
			return 0
		vals = sorted(vals)
		k = min(len(vals) - 1, int(round(p / 100 * (len(vals) - 1))))
		return vals[k]

	agg = {}
	for name, vals in sorted(phases.items()):
		agg[name] = {
			'n': len(vals),
			'p50_ms': round(pct(vals, 50), 1),
			'p95_ms': round(pct(vals, 95), 1),
			'total_ms': round(sum(vals), 1),
		}
	agg['_cdp_cmds_per_run'] = round(statistics.mean(cdp_counts), 1) if cdp_counts else 0
	agg['_sleep_ms_per_run'] = round(statistics.mean(sleep_total), 1) if sleep_total else 0
	return agg


async def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('--label', required=True)
	ap.add_argument('--runs', type=int, default=3)
	ap.add_argument('--tasks', default='')
	ap.add_argument('--profile', default='baseline', choices=['baseline', 'fast'])
	ap.add_argument('--llm', default='mock', choices=['mock', 'openai'])
	args = ap.parse_args()

	task_ids = args.tasks.split(',') if args.tasks else [t['id'] for t in TASKS]
	tasks = [t for t in TASKS if t['id'] in task_ids]

	results = []
	for task in tasks:
		for r in range(args.runs):
			print(f'>>> {task["id"]} run {r + 1}/{args.runs}', flush=True)
			res = await run_one(task, args.profile, args.label, r, llm_kind=args.llm)
			print(f'    success={res["success"]} t={res["t_task_s"]}s steps={res["n_steps"]} err={res["error"]}', flush=True)
			results.append(res)

	out_dir = RESULTS / args.label
	span_agg = analyze_spans(args.label)

	succ = sum(1 for r in results if r['success'])
	n = len(results)
	lo, hi = wilson_ci(succ, n)
	times = [r['t_task_s'] for r in results if r['error'] is None]
	steps = [r['n_steps'] for r in results if r['error'] is None]
	summary = {
		'label': args.label,
		'profile': args.profile,
		'n_runs': n,
		'success_rate': round(succ / n, 3) if n else 0,
		'sr_wilson_ci': [round(lo, 3), round(hi, 3)],
		't_task_p50': round(statistics.median(times), 2) if times else None,
		't_task_mean': round(statistics.mean(times), 2) if times else None,
		'n_steps_mean': round(statistics.mean(steps), 2) if steps else None,
		'results': results,
		'span_aggregate': span_agg,
	}
	(out_dir / 'summary.json').write_text(json.dumps(summary, indent=2))

	# markdown report
	md = [f'# Bench report: {args.label} (profile={args.profile})', '']
	md.append(f'- Runs: {n}, SR: {succ}/{n} = {succ / n:.1%} (Wilson CI [{lo:.2f}, {hi:.2f}])')
	if times:
		md.append(f'- T_task p50: {statistics.median(times):.1f}s, mean: {statistics.mean(times):.1f}s')
		md.append(f'- N_steps mean: {statistics.mean(steps):.1f}')
	md.append(f'- CDP cmds/run: {span_agg.get("_cdp_cmds_per_run")}, sleep ms/run: {span_agg.get("_sleep_ms_per_run")}')
	md.append('\n## Phase timings\n')
	md.append('| phase | n | p50 ms | p95 ms | total ms |')
	md.append('|---|---|---|---|---|')
	for k, v in span_agg.items():
		if k.startswith('_'):
			continue
		md.append(f'| {k} | {v["n"]} | {v["p50_ms"]} | {v["p95_ms"]} | {v["total_ms"]} |')
	md.append('\n## Per-run results\n')
	md.append('| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |')
	md.append('|---|---|---|---|---|---|---|---|')
	for r in results:
		md.append(
			f'| {r["task"]} | {r["run"]} | {"Y" if r["success"] else "N"} | {r["t_task_s"]} | {r["n_steps"]} | '
			f'{r.get("prompt_tokens", "-")} | {r.get("completion_tokens", "-")} | {r["error"] or ""} |'
		)
	(out_dir / 'report.md').write_text('\n'.join(md))
	print(json.dumps({k: v for k, v in summary.items() if k not in ('results', 'span_aggregate')}, indent=2))


if __name__ == '__main__':
	asyncio.run(main())
