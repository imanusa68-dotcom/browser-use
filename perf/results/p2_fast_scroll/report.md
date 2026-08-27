# Bench report: p2_fast_scroll (profile=baseline)

- Runs: 9, SR: 9/9 = 100.0% (Wilson CI [0.70, 1.00])
- T_task p50: 9.7s, mean: 9.2s
- N_steps mean: 2.7
- CDP cmds/run: 140.9, sleep ms/run: 26874.5

## Phase timings

| phase | n | p50 ms | p95 ms | total ms |
|---|---|---|---|---|
| agent.step | 15 | 3840.6 | 5521.8 | 61206.6 |
| browser.screenshot | 15 | 151.1 | 653.6 | 3682.2 |
| browser.state_request | 24 | 159.9 | 676.8 | 5487.2 |
| cdp.cmd | 1268 | 2.7 | 84.9 | 18296.8 |
| dom.cdp_ax_tree | 24 | 12.4 | 527.9 | 2725.3 |
| dom.cdp_get_all_trees | 24 | 29.0 | 537.0 | 2977.9 |
| dom.get_dom_tree | 24 | 30.4 | 637.0 | 3669.5 |
| dom.get_serialized_dom_tree | 24 | 31.0 | 650.7 | 3776.3 |
| idle.sleep | 732 | 5.5 | 1739.2 | 241870.6 |
| phase.execute_actions | 15 | 0.8 | 2040.2 | 9952.0 |
| phase.get_next_action | 15 | 3067.8 | 3300.8 | 46315.8 |
| phase.llm_call | 15 | 3067.5 | 3300.6 | 46312.3 |
| phase.multi_act | 24 | 141.6 | 2040.1 | 12560.2 |
| phase.prepare_context | 15 | 240.0 | 766.8 | 4784.0 |

## Per-run results

| task | run | ok | t(s) | steps | tokens_in | tokens_out | error |
|---|---|---|---|---|---|---|---|
| search_extract | 0 | Y | 9.7 | 3 | 12632 | 101 |  |
| search_extract | 1 | Y | 9.72 | 3 | 12632 | 101 |  |
| search_extract | 2 | Y | 9.6 | 3 | 12632 | 101 |  |
| form_fill | 0 | Y | 11.11 | 3 | 12647 | 158 |  |
| form_fill | 1 | Y | 11.31 | 3 | 12647 | 158 |  |
| form_fill | 2 | Y | 11.24 | 3 | 12647 | 158 |  |
| heavy_dom | 0 | Y | 6.68 | 2 | 6853 | 52 |  |
| heavy_dom | 1 | Y | 6.49 | 2 | 6854 | 52 |  |
| heavy_dom | 2 | Y | 6.59 | 2 | 6853 | 52 |  |