# Bench report: p_baseline (profile=baseline)

- Runs: 9, SR: 9/9 = 100.0% (Wilson CI [0.70, 1.00])
- T_task p50: 10.1s, mean: 9.6s
- N_steps mean: 2.7
- CDP cmds/run: 130.8, sleep ms/run: 28196.6

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 15 | 3742.1 | 5646.5 | 61399.1 |
| browser.screenshot | 15 | 154.2 | 498.9 | 3247.6 |
| browser.state_request | 24 | 176.4 | 966.5 | 7559.8 |
| cdp.cmd | 1177 | 2.9 | 127.4 | 22264.3 |
| dom.cdp_ax_tree | 24 | 15.0 | 708.4 | 3717.8 |
| dom.cdp_get_all_trees | 24 | 36.6 | 757.3 | 4315.6 |
| dom.get_dom_tree | 24 | 42.9 | 925.2 | 5149.7 |
| dom.get_serialized_dom_tree | 24 | 44.6 | 953.1 | 5269.0 |
| idle.sleep | 758 | 8.2 | 1794.5 | 253769.3 |
| phase.execute_actions | 15 | 0.9 | 1967.3 | 9750.2 |
| phase.get_next_action | 15 | 3067.8 | 3301.8 | 46315.7 |
| phase.llm_call | 15 | 3067.5 | 3301.6 | 46311.8 |
| phase.multi_act | 24 | 334.1 | 1967.2 | 14905.8 |
| phase.prepare_context | 15 | 268.1 | 620.0 | 5224.9 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.78 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 9.64 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.11 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.51 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.68 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 11.51 | 3 | 12647 | 158 |  |
| heavy_dom | 0 | Y | 7.1 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 7.09 | 2 | 6853 | 52 |  |
| heavy_dom | 2 | Y | 7.4 | 2 | 6854 | 52 |  |