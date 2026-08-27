# Bench report: p1_fast_input (profile=baseline)

- Runs: 9, SR: 9/9 = 100.0% (Wilson CI [0.70, 1.00])
- T_task p50: 10.3s, mean: 9.4s
- N_steps mean: 2.7
- CDP cmds/run: 99.9, sleep ms/run: 27483.1

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 15 | 3648.5 | 5106.1 | 59904.5 |
| browser.screenshot | 15 | 147.3 | 454.8 | 3012.6 |
| browser.state_request | 24 | 249.7 | 822.1 | 7676.1 |
| cdp.cmd | 899 | 3.8 | 131.7 | 27808.6 |
| dom.cdp_ax_tree | 24 | 18.1 | 428.1 | 2612.1 |
| dom.cdp_get_all_trees | 24 | 35.9 | 452.7 | 2955.5 |
| dom.get_dom_tree | 24 | 40.9 | 557.1 | 3669.6 |
| dom.get_serialized_dom_tree | 24 | 41.4 | 570.5 | 3770.1 |
| idle.sleep | 653 | 40.9 | 2103.8 | 247348.0 |
| phase.execute_actions | 15 | 1.0 | 1503.7 | 7963.9 |
| phase.get_next_action | 15 | 3068.2 | 3302.3 | 46319.1 |
| phase.llm_call | 15 | 3067.9 | 3302.0 | 46315.3 |
| phase.multi_act | 24 | 305.9 | 1503.6 | 12663.6 |
| phase.prepare_context | 15 | 293.2 | 552.2 | 5466.1 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.51 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.08 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.28 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 10.76 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.25 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 10.98 | 3 | 12647 | 158 |  |
| heavy_dom | 0 | Y | 6.99 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 6.93 | 2 | 6853 | 52 |  |
| heavy_dom | 2 | Y | 6.97 | 2 | 6854 | 52 |  |