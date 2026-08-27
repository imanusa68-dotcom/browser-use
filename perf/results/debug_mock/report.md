# Bench report: debug_mock (profile=baseline)

- Runs: 6, SR: 4/6 = 66.7% (Wilson CI [0.30, 0.90])
- T_task p50: 9.1s, mean: 19.6s
- N_steps mean: 6.2
- CDP cmds/run: 330.2, sleep ms/run: 58858.0

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 31 | 2939.2 | 4427.1 | 101123.1 |
| browser.screenshot | 31 | 150.6 | 177.3 | 4865.2 |
| browser.state_request | 47 | 151.4 | 392.7 | 7221.8 |
| cdp.cmd | 1981 | 2.8 | 50.3 | 27158.2 |
| dom.cdp_ax_tree | 47 | 17.1 | 47.6 | 1672.0 |
| dom.cdp_get_all_trees | 47 | 31.9 | 198.5 | 2559.4 |
| dom.get_dom_tree | 47 | 36.9 | 199.5 | 3053.5 |
| dom.get_serialized_dom_tree | 47 | 40.0 | 200.0 | 3201.1 |
| idle.sleep | 974 | 5.5 | 1916.8 | 353148.0 |
| phase.execute_actions | 31 | 354.4 | 1627.3 | 22351.0 |
| phase.get_next_action | 31 | 2244.6 | 2549.9 | 70896.8 |
| phase.llm_call | 31 | 2244.3 | 2549.6 | 70889.0 |
| phase.multi_act | 37 | 334.8 | 1627.2 | 24500.1 |
| phase.prepare_context | 31 | 241.3 | 296.6 | 7759.8 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 8.75 | 3 | 12632 | 101 |  |
| form_fill | 0 | N | 45.61 | 13 | 77991 | 657 |  |
| table_paginate | 0 | N | 39.16 | 13 | 80057 | 468 |  |
| login_flow | 0 | Y | 9.46 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 8.05 | 3 | 12494 | 92 |  |
| heavy_dom | 0 | Y | 6.41 | 2 | 6853 | 52 |  |