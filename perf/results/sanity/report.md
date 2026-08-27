# Bench report: sanity (profile=baseline)

- Runs: 6, SR: 6/6 = 100.0% (Wilson CI [0.61, 1.00])
- T_task p50: 10.8s, mean: 10.6s
- N_steps mean: 3.0
- CDP cmds/run: 130.8, sleep ms/run: 31029.8

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 12 | 3979.8 | 5127.7 | 47182.2 |
| browser.screenshot | 12 | 127.2 | 167.8 | 1845.5 |
| browser.state_request | 18 | 135.9 | 521.2 | 3692.1 |
| cdp.cmd | 785 | 3.2 | 89.5 | 21178.5 |
| dom.cdp_ax_tree | 18 | 12.2 | 378.2 | 992.9 |
| dom.cdp_get_all_trees | 18 | 25.3 | 387.4 | 1267.0 |
| dom.get_dom_tree | 18 | 28.9 | 497.2 | 1552.5 |
| dom.get_serialized_dom_tree | 18 | 30.5 | 511.0 | 1604.6 |
| idle.sleep | 510 | 13.8 | 2125.0 | 186179.0 |
| phase.execute_actions | 12 | 846.3 | 1566.9 | 7689.6 |
| phase.get_next_action | 12 | 2959.4 | 3242.9 | 35618.6 |
| phase.llm_call | 12 | 2959.1 | 3242.7 | 35615.9 |
| phase.multi_act | 18 | 256.4 | 1566.8 | 10154.5 |
| phase.prepare_context | 12 | 289.9 | 551.6 | 3830.0 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.49 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.32 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 13.79 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 11.2 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.76 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.04 | 2 | 6854 | 52 |  |