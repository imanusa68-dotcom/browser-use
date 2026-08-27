# Bench report: p3_baseline (profile=baseline)

- Runs: 18, SR: 18/18 = 100.0% (Wilson CI [0.82, 1.00])
- T_task p50: 10.8s, mean: 10.8s
- N_steps mean: 3.0
- CDP cmds/run: 131.2, sleep ms/run: 31892.9

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 36 | 3908.4 | 5518.8 | 143141.1 |
| browser.screenshot | 36 | 160.3 | 529.6 | 8351.5 |
| browser.state_request | 54 | 176.8 | 624.0 | 14921.3 |
| cdp.cmd | 2362 | 3.3 | 123.2 | 81031.5 |
| dom.cdp_ax_tree | 54 | 11.3 | 417.8 | 4062.7 |
| dom.cdp_get_all_trees | 54 | 32.5 | 426.5 | 5165.9 |
| dom.get_dom_tree | 54 | 38.1 | 551.3 | 6169.4 |
| dom.get_serialized_dom_tree | 54 | 40.8 | 566.1 | 6340.2 |
| idle.sleep | 1550 | 17.0 | 2106.7 | 574072.9 |
| phase.execute_actions | 36 | 801.4 | 1897.0 | 23321.7 |
| phase.get_next_action | 36 | 2958.7 | 3300.8 | 106872.7 |
| phase.llm_call | 36 | 2958.4 | 3300.5 | 106860.8 |
| phase.multi_act | 54 | 363.0 | 1722.8 | 32074.1 |
| phase.prepare_context | 36 | 282.0 | 611.1 | 12761.5 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 10.83 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 10.69 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 10.72 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.91 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.29 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 12.11 | 3 | 12647 | 158 |  |
| table_paginate | 0 | Y | 13.69 | 4 | 19549 | 119 |  |
| table_paginate | 1 | Y | 14.27 | 4 | 19549 | 119 |  |
| table_paginate | 2 | Y | 14.3 | 4 | 19549 | 119 |  |
| login_flow | 0 | Y | 10.52 | 3 | 12560 | 117 |  |
| login_flow | 1 | Y | 11.19 | 3 | 12560 | 117 |  |
| login_flow | 2 | Y | 10.78 | 3 | 12560 | 117 |  |
| modal_dismiss | 0 | Y | 9.89 | 3 | 12503 | 92 |  |
| modal_dismiss | 1 | Y | 10.02 | 3 | 12503 | 92 |  |
| modal_dismiss | 2 | Y | 10.12 | 3 | 12503 | 92 |  |
| heavy_dom | 0 | Y | 7.24 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 7.73 | 2 | 6853 | 52 |  |
| heavy_dom | 2 | Y | 7.89 | 2 | 6854 | 52 |  |