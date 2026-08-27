# Bench report: p5_fast_network_idle (profile=baseline)

- Runs: 18, SR: 18/18 = 100.0% (Wilson CI [0.82, 1.00])
- T_task p50: 10.6s, mean: 10.7s
- N_steps mean: 3.0
- CDP cmds/run: 131.3, sleep ms/run: 31246.6

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 36 | 3890.5 | 5427.6 | 140970.6 |
| browser.screenshot | 36 | 139.7 | 524.7 | 6672.2 |
| browser.state_request | 54 | 146.4 | 563.7 | 12217.4 |
| cdp.cmd | 2363 | 3.2 | 110.3 | 89175.7 |
| dom.cdp_ax_tree | 54 | 13.8 | 389.4 | 3990.4 |
| dom.cdp_get_all_trees | 54 | 28.1 | 430.8 | 5137.7 |
| dom.get_dom_tree | 54 | 29.7 | 518.3 | 6092.9 |
| dom.get_serialized_dom_tree | 54 | 30.8 | 536.1 | 6279.5 |
| idle.sleep | 1547 | 16.8 | 2110.3 | 562437.9 |
| phase.execute_actions | 36 | 823.1 | 1830.0 | 22673.1 |
| phase.get_next_action | 36 | 2958.3 | 3300.9 | 106866.7 |
| phase.llm_call | 36 | 2958.1 | 3300.6 | 106855.8 |
| phase.multi_act | 54 | 252.4 | 1697.2 | 30796.9 |
| phase.prepare_context | 36 | 242.1 | 614.3 | 11185.0 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.4 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.73 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.32 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.5 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.44 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 11.32 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 13.58 | 4 | 19549 | 119 |  |
| table_paginate | 1 | Y | 14.29 | 4 | 19549 | 119 |  |
| table_paginate | 2 | Y | 14.31 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 10.5 | 3 | 12560 | 117 |  |
| login_flow | 1 | Y | 11.3 | 3 | 12560 | 117 |  |
| login_flow | 2 | Y | 10.68 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.59 | 3 | 12494 | 92 |  |
| modal_dismiss | 1 | Y | 9.52 | 3 | 12503 | 92 |  |
| modal_dismiss | 2 | Y | 9.75 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.83 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 7.26 | 2 | 6853 | 52 |  |
| heavy_dom | 2 | Y | 7.55 | 2 | 6853 | 52 |  |