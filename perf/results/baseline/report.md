# Bench report: baseline (profile=baseline)

- Runs: 18, SR: 18/18 = 100.0% (Wilson CI [0.82, 1.00])
- T_task p50: 10.8s, mean: 10.6s
- N_steps mean: 3.0
- CDP cmds/run: 131.1, sleep ms/run: 31144.6

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 36 | 3809.3 | 5530.2 | 140990.7 |
| browser.screenshot | 36 | 147.5 | 520.8 | 6347.9 |
| browser.state_request | 54 | 164.9 | 650.6 | 11817.0 |
| cdp.cmd | 2359 | 3.3 | 91.8 | 46443.2 |
| dom.cdp_ax_tree | 54 | 13.1 | 374.1 | 3433.0 |
| dom.cdp_get_all_trees | 54 | 30.3 | 382.9 | 4340.9 |
| dom.get_dom_tree | 54 | 32.3 | 551.4 | 5290.1 |
| dom.get_serialized_dom_tree | 54 | 33.4 | 575.9 | 5527.1 |
| idle.sleep | 1535 | 15.3 | 1928.3 | 560603.1 |
| phase.execute_actions | 36 | 836.1 | 1923.8 | 23114.3 |
| phase.get_next_action | 36 | 2959.8 | 3300.3 | 106885.9 |
| phase.llm_call | 36 | 2959.5 | 3300.2 | 106874.5 |
| phase.multi_act | 54 | 277.2 | 1727.7 | 31280.2 |
| phase.prepare_context | 36 | 252.1 | 642.8 | 10741.8 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.89 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.81 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.1 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.49 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.56 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 11.45 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 13.76 | 4 | 19549 | 119 |  |
| table_paginate | 1 | Y | 13.81 | 4 | 19549 | 119 |  |
| table_paginate | 2 | Y | 13.75 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 10.52 | 3 | 12560 | 117 |  |
| login_flow | 1 | Y | 10.72 | 3 | 12560 | 117 |  |
| login_flow | 2 | Y | 11.31 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.61 | 3 | 12503 | 92 |  |
| modal_dismiss | 1 | Y | 10.17 | 3 | 12503 | 92 |  |
| modal_dismiss | 2 | Y | 10.18 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.33 | 2 | 6854 | 52 |  |
| heavy_dom | 1 | Y | 7.15 | 2 | 6853 | 52 |  |
| heavy_dom | 2 | Y | 7.07 | 2 | 6853 | 52 |  |