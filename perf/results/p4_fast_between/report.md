# Bench report: p4_fast_between (profile=baseline)

- Runs: 18, SR: 18/18 = 100.0% (Wilson CI [0.82, 1.00])
- T_task p50: 10.3s, mean: 10.5s
- N_steps mean: 3.0
- CDP cmds/run: 133.5, sleep ms/run: 30756.9

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 36 | 3887.8 | 5164.5 | 139107.0 |
| browser.screenshot | 36 | 152.2 | 457.2 | 6454.6 |
| browser.state_request | 54 | 170.7 | 527.1 | 13192.6 |
| cdp.cmd | 2403 | 3.3 | 102.6 | 39850.3 |
| dom.cdp_ax_tree | 54 | 14.4 | 341.9 | 4228.6 |
| dom.cdp_get_all_trees | 54 | 35.5 | 353.0 | 5625.1 |
| dom.get_dom_tree | 54 | 36.9 | 476.6 | 6565.4 |
| dom.get_serialized_dom_tree | 54 | 41.6 | 516.9 | 6773.4 |
| idle.sleep | 1508 | 13.6 | 2133.7 | 553625.1 |
| phase.execute_actions | 36 | 830.3 | 1659.2 | 21283.2 |
| phase.get_next_action | 36 | 2959.9 | 3301.2 | 106883.9 |
| phase.llm_call | 36 | 2959.5 | 3300.9 | 106872.1 |
| phase.multi_act | 54 | 293.0 | 1437.6 | 29390.4 |
| phase.prepare_context | 36 | 246.5 | 522.1 | 10744.1 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.71 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.56 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.06 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.8 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.25 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 11.12 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 13.61 | 4 | 19549 | 119 |  |
| table_paginate | 1 | Y | 13.99 | 4 | 19549 | 119 |  |
| table_paginate | 2 | Y | 14.14 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 10.04 | 3 | 12560 | 117 |  |
| login_flow | 1 | Y | 10.32 | 3 | 12560 | 117 |  |
| login_flow | 2 | Y | 10.2 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.85 | 3 | 12503 | 92 |  |
| modal_dismiss | 1 | Y | 9.5 | 3 | 12503 | 92 |  |
| modal_dismiss | 2 | Y | 9.4 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.33 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 7.79 | 2 | 6854 | 52 |  |
| heavy_dom | 2 | Y | 7.37 | 2 | 6853 | 52 |  |