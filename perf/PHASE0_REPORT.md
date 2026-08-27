# browser-use Performance Audit — Phase 0/1 Report

Version audited: **browser-use 0.13.8** (source in `browser-use-main/`, editable install).
Environment: Linux sandbox, Python 3.13, Playwright Chromium headless-shell 151, local
deterministic fixture server (`perf/fixtures/server.py`), scripted deterministic LLM
(`perf/mock_llm.py`) with a synthetic latency model (TTFT + prefill + decode) so that
prompt-size changes show up in wall-clock exactly like with a real provider.

## 1. Assumptions & version check (гипотезы из ТЗ vs реальный код)

| Hypothesized name | Real in 0.13.8 | Location |
|---|---|---|
| `minimum_wait_page_load_time` | ✅ exists, default **0.25s** | `browser/profile.py:680` |
| `wait_for_network_idle_page_load_time` | ✅ exists, default 0.5s (but the actual stability wait in DOMWatchdog is a hardcoded `sleep(0.3)` when requests pending) | `profile.py:681`, `watchdogs/dom_watchdog.py:288` |
| `maximum_wait_page_load_time` | ❌ removed in this version | — |
| `wait_between_actions` | ✅ exists, default 0.1s, applied in `Agent.multi_act` | `agent/service.py:2773` |
| `highlight_elements` | ✅ exists (+ new `dom_highlight_elements`) | `profile.py:686` |
| `viewport_expansion` | ❌ **does not exist** in DomService anymore (only a stale reference in `mcp/manifest.json`). DOM is built from `DOMSnapshot.captureSnapshot` + `Accessibility.getFullAXTree`, no JS `buildDomTree.js` | `dom/service.py` |
| `flash_mode` | ✅ exists (`AgentSettings.flash_mode`) — disables thinking/eval/next_goal fields | `agent/views.py:73` |
| `max_actions_per_step` | ✅ exists, default **5**; multi-action batching with invalidation guards (`terminates_sequence` flags + URL/focus-change runtime detection) is **already implemented** | `agent/service.py:2732` |
| Planner / judge extra LLM calls | ✅ `enable_planning=True`, `use_judge=True` by default; judge is a separate `judge_llm.ainvoke` | `agent/service.py:184,202,1587` |
| DOM via `Runtime.evaluate` returnByValue | ❌ not used for tree; uses `DOMSnapshot.captureSnapshot` (avg 20ms) + `Accessibility.getFullAXTree` (avg 40ms) — already efficient | `dom/service.py:379,571` |
| Screenshot | PNG, full-res, no quality knob | `watchdogs/screenshot_watchdog.py:65` |
| DOM+screenshot parallelism | ✅ **already parallel** (screenshot task created alongside DOM build) | `dom_watchdog.py:358-414` |
| Prompt caching prefix stability | system prompts exist per-mode (`system_prompts/*.md`, 22KB main); state message appended after — prefix mostly stable, but page_filtered_actions injected per-URL into state msg (OK, in tail) | `agent/prompts.py` |

## 2. Latency budget (baseline: 18 runs = 6 tasks × 3, mock LLM TTFT=700ms, SR=18/18=100%, Wilson CI [0.82,1.0])

Per-task wall p50 ≈ 10.7s, N_steps 2–4 (scripted optimal), step p50 = 3.81s, p95 = 5.53s.

| Phase | n | p50 ms | p95 ms | Σ (s) | % of Σstep (141s) |
|---|---|---|---|---|---|
| phase.llm_call | 36 | 2960 | 3300 | 106.9 | **75.8%** |
| phase.multi_act (action exec) | 54 | 277 | 1728 | 31.3 | 22.2% |
| phase.prepare_context (DOM+screenshot+prompt) | 36 | 252 | 643 | 10.7 | 7.6% |
| browser.screenshot (PNG) | 36 | 148 | 521 | 6.4 | 4.5% |
| dom.get_serialized_dom_tree | 54 | 33 | 576 | 5.5 | 3.9% |
| CDP commands (2359 total, ~131/run) | — | 3.3 | 92 | 46.4 | overlaps |

Idle (sleep) inside step path: small fixed sleeps (0.05–0.1s × dozens per action) total **~2.2s per task ≈ 20% of wall** on fixture pages. Huge `sleep(15/20/60)` entries are watchdog poll loops running in background (do not block steps, but 864×15s polls = CPU noise).

Top CDP by total time: `Target.setAutoAttach` 86ms avg ×133; `Runtime.runIfWaitingForDebugger` ×378 (23ms avg — N+1 pattern in session_manager); `Page.captureScreenshot` 137ms avg; `Page.enable` 42ms ×72.

## 3. Findings (numbered, with evidence)

1. **LLM call = 76% of step time.** Prompt is ~24.3KB (~6k tokens) for a trivial page; ~22KB of that is the static system prompt. → prompt-cache + flash/no-thinking modes are the primary lever.
2. **Fixed sleeps in the action hot path** (`default_action_watchdog.py`): click = `scrollIntoViewIfNeeded + sleep(0.05)` → `mouseMoved + sleep(0.05)` → `mousePressed + sleep(0.05)` → mouseReleased; typing = **3 CDP events + 6ms sleep per character** (form_fill: 4 actions → multi_act p95 1.73s, ~1s of it sleeps+keystrokes). Measured ≈2.2s/task.
3. **`wait_between_actions=0.1` default** adds 0.1s × (actions-1) per step in `multi_act` (agent/service.py:2773) — pure idle, config-only fix.
4. **Screenshot is PNG full-res, always captured** (`include_screenshot=True` hardcoded in `_prepare_context`, comment admits "even if use_vision=False"). 137ms avg CDP + base64 + payload. JPEG q70 typically 3–5× faster to encode/transfer.
5. **`Runtime.runIfWaitingForDebugger` fired 378× (21/run)** — N+1 in `session_manager.py:506` per attached target/frame; batched or conditional dispatch would cut ~0.5s/run.
6. **Watchdog poll loops** (`sleep(15/20/60)` × hundreds) — don't block steps but generate wakeups; event-driven or longer intervals are free wins.
7. **Judge + planner defaults**: `use_judge=True` adds a full extra LLM call at end-of-task; `enable_planning=True` enlarges output schema. Both are quality features — keep, but expose in FAST preset.
8. **Already good (no work needed):** DOM+screenshot parallel; DOMSnapshot-based extraction (33ms p50 even on 800-node page — heavy_dom p95 576ms only on first load); multi-action batching with invalidation; loop detection.

## 4. Optimization plan (priority = win / (risk × effort))

| ID | Optimization | Expected win | Risk | Flag | Status |
|---|---|---|---|---|---|
| O1 | FAST preset via existing config: `wait_between_actions=0`, `minimum_wait_page_load_time=0.05`, `highlight_elements=False`, `use_judge=False` | −0.5–1.5 s/task | Low (config-only, revertible) | preset | designed, needs A/B run |
| O2 | Fast-input mode: `Input.insertText` + framework events instead of per-char keystrokes, fallback to per-char on readback mismatch (mask/formatter sites) | −0.3–1 s per input action | Med (masked inputs) — fallback keeps SR | `BROWSER_USE_FAST_INPUT=1` | patch drafted (see §5) |
| O3 | Remove/shrink fixed 50ms sleeps in click path (event-driven: wait only after scrollIntoView if rect changed) | −150 ms/click | Low | `BROWSER_USE_FAST_CLICK=1` | drafted |
| O4 | Screenshot JPEG quality=70 + skip capture when `use_vision=False` (make `include_screenshot` follow settings) | −100–400 ms/step + big vision-token cut | Low (vision SR must be re-benched) | `screenshot_format` in profile | drafted |
| O5 | Batch `runIfWaitingForDebugger` dispatch / skip for same-origin subframes | −0.4 s/run | Low | internal | drafted |
| O6 | flash_mode + no-thinking system prompt (2.4KB vs 22KB) for simple tasks; adaptive escalation to full mode on first failure | −30–60% prompt tokens, −TTFT with provider cache | Med — must be validated per-benchmark | `flash_mode` (exists) | needs SR A/B |
| O7 | Trajectory replay cache per (domain, task-template) | 5–20× on repeats | High (staleness) | opt-in | design only |

## 5. Drafted patches (not merged — each requires one isolated A/B run first, per the one-change-one-measurement rule)

**O2 fast input** (`default_action_watchdog.py::_input_text_element_node_impl`): after focus, replace the per-char loop with:
```python
if os.environ.get('BROWSER_USE_FAST_INPUT') == '1' and not _is_contenteditable:
    await cdp_session.cdp_client.send.Input.insertText(
        params={'text': text}, session_id=cdp_session.session_id)
    await self._trigger_framework_events(object_id=object_id, cdp_session=cdp_session)
    # readback (existing Step 5); on mismatch -> fall through to per-char loop
```
**O4 screenshot**: in `screenshot_watchdog.py:65` `{'format': 'jpeg', 'quality': 70}` behind `browser_profile.screenshot_format`; in `agent/service.py:1090` `include_screenshot=self.settings.use_vision is not False`.

## 6. Benchmark & guardrails (delivered, working)

- `perf/tracer.py` — monkeypatch JSONL span tracer (step → phase → CDP cmd → sleep), zero changes to library code.
- `perf/fixtures/server.py` — deterministic local site (search/forms/table+pagination/login/modal/heavy-DOM/slow).
- `perf/mock_llm.py` — scripted `BaseChatModel` with synthetic TTFT/prefill/decode latency → reproducible A/B of the framework side, SR checked by asserts, not by "agent said done".
- `perf/run_bench.py` — runner: N runs/task, Wilson CI, phase aggregation, markdown+JSON reports. CI gate = `--tasks search_extract,form_fill,heavy_dom --runs 2`.
- Baseline artifacts: `perf/results/baseline/` (18 runs, SR 100%, spans, report.md).

## 7. Results so far

Baseline established and reproducible (σ(T_task) < 0.5s per task).

**O1 (FAST config-only preset) — measured A/B** (same 3 tasks: search_extract, form_fill, heavy_dom; 3 runs each, mock LLM TTFT=700ms):

| Metric | baseline | O1 fast | Δ |
|---|---|---|---|
| SR | 9/9 (100%) | 9/9 (100%) | 0 (non-inferior) |
| T_task p50 | 10.81 s | 10.18 s | −5.8% |
| T_task mean | 9.76 s | 9.61 s | −1.5% |
| sleep ms/run | 31 145 | 27 976 | −10% |

Verdict: **accept** (SR unchanged, small but consistent win; risk zero, config-only).
Effect is modest because 76% of step time is the (fixed-latency) mock LLM call — with a
real provider O1 combines with O6 (flash prompt → smaller prefill) for a larger relative win.
O2–O7 remain drafted but **not applied** per the one-change-one-measurement rule.

## 8. Proposed presets (to be validated)

- **FAST**: O1+O2+O3+O4, flash_mode, use_judge=False, use_vision='auto' — target T_step_p50 < 1.5s at 700ms TTFT.
- **BALANCED** (default): O3+O5 only (riskless), judge on.
- **ACCURATE**: current defaults + use_thinking, vision always.
- Adaptive escalation: start FAST, on first action error or loop-detector hit switch task to ACCURATE.

## 9. Risks & follow-ups

- Mock LLM measures framework latency, not model reasoning: N_steps/SR effects of O6 (flash prompts) must be re-run with a real provider (`--llm openai`, needs valid proxy token — 401 in this sandbox).
- Masked/react-controlled inputs may reject `insertText` — fallback path is mandatory (already in O2 design).
- Live-site smoke set (Amazon/LinkedIn-class heavy pages) not yet run; DOMSnapshot p95 may grow superlinearly there.
- Monitor in prod: t_llm/t_step ratio, mis-click rate, insertText-fallback rate, screenshot bytes/step.

## 10. TL;DR

1. 76% of step time is the LLM call; prompt is ~24KB of which 22KB is a static system prompt — cache the prefix, use flash/no-thinking for simple steps.
2. ~2.2s/task (≈20% wall on fast pages) is fixed `asyncio.sleep` in click/type paths — replace with `Input.insertText` and event-driven waits (flagged, with fallback).
3. `wait_between_actions=0.1` and PNG screenshots are free config wins.
4. DOM extraction is NOT the bottleneck in 0.13.8 (33ms p50, DOMSnapshot-based) — old buildDomTree assumptions are obsolete.
5. Multi-action batching + invalidation already exists and works; use it (it's why scripted runs finish in 2–4 steps).
6. N+1 `runIfWaitingForDebugger` (21/run × 23ms) is a small clean win.
7. Harness (fixtures + scripted LLM + Wilson CI) is in `perf/` and gives deterministic SR=100% baseline — every optimization now gets a one-flag A/B with quality guardrails.

---

## Phase 2 (P1–P6, «слепые паузы») — статус на 2026-08-27

### Выполнено

**P1 fast_input — реализовано и измерено (A/B, изолированное изменение).**
- Флаг: `BrowserProfile.fast_input=False` (opt-in) или env `BROWSER_USE_FAST_INPUT=1`.
- Реализация (`default_action_watchdog.py::_input_text_element_node_impl`):
  один `Input.insertText` вместо посимвольного цикла (3 CDP-события + 6мс пауз на символ)
  → существующий `_trigger_framework_events` (input/change для React/Vue/Angular)
  → **один rAF-тик с потолком 100мс** (`_raf_tick`) вместо `sleep(0.05)` перед readback
  → readback ВСЕГДА; мismatch или исключение ⇒ лог `perf.fallback:` + очистка поля +
  **автоматический откат на нетронутый посимвольный путь в том же действии**.
- Автоисключения (fast_input не применяется): contenteditable / role=textbox вне
  input|textarea; input с pattern/data-mask/inputmask-классами; inputmode=numeric на text;
  все типы вне text/search/email/url/tel/password/number; текст с '\n' (Enter-семантика).
- Для sensitive-полей значение readback в лог не пишется.

**A/B результат P1** (3 задачи × 3 прогона, mock LLM TTFT=700ms, свежий baseline в той же среде):

| Метрика | p_baseline | p1_fast_input | Δ |
|---|---|---|---|
| SR | 9/9 = 100% | 9/9 = 100% | 0 (non-inferior, маржа −2 п.п. соблюдена) |
| T_task p50 | 10.11 s | 10.28 s | шум (±0.5s между прогонами) |
| T_task mean | 9.65 s | 9.42 s | −2.4% |
| sleep ms/run (все, вкл. фоновые poll'ы watchdog'ов) | 28 197 | 27 483 | −714 мс/прогон |
| fallback_rate | — | 0/9 прогонов (fixture-поля без масок) | OK |

Вердикт: **принято как opt-in** (SR не деградировал, слепые паузы ввода убраны,
выигрыш на wall-clock скрыт фиксированной latency mock-LLM — с реальным провайдером
эффект аддитивен к O1/O6). heavy_dom стабильно быстрее (6.93–6.99s vs 7.09–7.40s baseline).

**Хелперы под P2 (реализованы, ещё не включены в click-путь):**
- `_raf_tick(cdp_session, timeout_ms)` — ожидание одного requestAnimationFrame с потолком;
- `_wait_element_rect_stable(backend_node_id, cdp_session, ceiling_ms=300)` — двойной замер
  rect через rAF, |Δ|<1px ⇒ стабильно; потолок 300мс ⇒ последний замер (де-факто старое поведение).

**Флаги конфига добавлены в BrowserProfile (все default=False):**
`fast_input`, `fast_scroll_stability` (P2), `fast_click` + `click_press_duration_ms=20` (P3),
`fast_between_actions` (P4), `fast_network_idle` (P5) — с комментариями, что каждый защищает.

**Регрессионные фикстуры добавлены** (`perf/fixtures/server.py`):
- `/delayed_field` — поле появляется через 1.5s (setTimeout-рендер) — тест P4;
- `/masked_phone` — маска (XXX) XXX-XXXX на input-событии — тест отката P1;
- `/shifting_button` — lazy-баннер сдвигает кнопку через 300мс после скролла — тест P2;
- `/react_input` — controlled-input: значение живёт в state, ре-рендер из state — тест framework events;
- `/slow` (2s) — уже был.

### Осталось (по одному изменению за прогон, план в ТЗ актуален)

- **P2**: воткнуть `_wait_element_rect_stable` вместо `scrollIntoViewIfNeeded + sleep(0.05)`
  в `_click_element_node_impl` (строка ~771 orig) и в input-путь (sleep(0.01) ~1786) за флагом
  `fast_scroll_stability`; прогнать `/shifting_button`-регрессию + бенч.
- **P3**: за `fast_click`: пауза после mouseMoved → 0 (после P2), pressed→released →
  `click_press_duration_ms` (20мс), после released → удалить (дальше URL/focus-check в multi_act).
- **P4**: в `agent/service.py:2773` за `fast_between_actions`: probe
  (readyState==='complete' && in-flight==0 && нет мутаций за rAF через одноразовый
  MutationObserver-счётчик) → чисто ⇒ немедленно; грязно ⇒ poll 25мс, потолок wait_between_actions*5.
  Регрессия `/delayed_field` обязана проходить.
- **P5**: `dom_watchdog.py:288` за `fast_network_idle`: poll `_get_pending_network_requests`
  каждые 50мс, quiet-period 100мс, потолок `wait_for_network_idle_page_load_time`,
  фильтр вечных запросов (WS/SSE/аналитика — фильтр в JS уже частично есть).
- **P6**: аудит строк 553, 897–1212, 2393–2457 (комментарий «что защищает» → удалить/заменить/TODO).
- Регрессионные тесты-скрипты поверх новых фикстур (прямой dispatch TypeTextEvent/ClickElementEvent,
  без LLM) + прогон на `/slow`; метрики fallback_rate / mis-click в отчёт.

### Рекомендация по флагам (текущая)

- `fast_input` — **opt-in** (принят по A/B; включать в default после live-site smoke на масках/React).
- Остальные флаги — выключены до своих изолированных A/B.
