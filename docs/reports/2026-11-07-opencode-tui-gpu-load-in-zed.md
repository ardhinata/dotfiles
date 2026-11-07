---
status: open
severity: major
---

# OpenCode TUI panes in Zed raise the GPU render engine load while agent output streams

## Summary

An OpenCode TUI pane inside a Zed terminal renders fine when it sits idle. But while an agent
streams tool output into it, the GPU render engine (RCS on Intel Iris Xe) sits at 50 to 80%.
Zed itself is innocent: with no opencode process, Zed renders at about 4%. The obvious lever
does not exist: opencode 2.2.6 carries no fps environment variable.
Upstream never merged the proposals for one. A local TUI plugin that clamped the renderer
frame rate gave a small (~17%) gain and was removed again on 2026-11-07. The main load rides
on output streaming, not on the frame rate.

## Steps to reproduce

1. Start `opencode` in a Zed terminal pane. Leave the rest of the desktop as it is.
2. Run an agent turn that streams a large tool dump into that pane.
3. Measure the GPU render engine while the text scrolls:

   ```sh
   sudo intel_gpu_top -c | tee /tmp/opencode/streaming.csv
   ```

4. Wait until the agent stops talking and measure again.

## Expected

Terminal-style text output in an editor pane should not hold the GPU render engine near its
maximum. A documented setting or environment variable should control the TUI frame rate.

## Actual

Measurements in one session (all captures with the same workload pattern, 60 Hz panels):

| Capture                    | Pane state                | RCS avg | RCS p50 | RCS max | Package power |
| -------------------------- | ------------------------- | ------: | ------: | ------: | ------------: |
| All apps running           | pane streaming + firefox  |   62.0% |   64.1% |   85.4% |         11.9 W |
| Firefox closed             | pane streaming            |   51.4% |   64.4% |  100.0% |         10.0 W |
| Same pane, fps cap off     | pane streaming            |   63.8% |   76.3% |   84.4% |         12.0 W |
| Opencode panes closed      | Zed alone                 |    4.0% |    3.1% |   25.7% |          3.6 W |
| Pane open, agent idle      | pane idle, fps cap on     |    6.6% |    4.5% |   95.1% |          3.8 W |

The render loop on opencode 2.2.6 got measured separately from the GPU table, in a fresh
TUI under a pty (opencode process sampled with `/proc/<pid>/io` char counts and CPU ticks):

| TUI state                                    | tty write rate | opencode CPU |
| -------------------------------------------- | --------------:| ------------: |
| Status idle, no turn                          | ~0 B/s         | ~0.3%        |
| Status running, spinner only, no output (shell mode `sleep 25`) | 33 B/s       | 0.7%       |
| Status running, `seq 1 300000` floods shell mode (2.6 MB/s raw stdin path) | 26 KB/s (207 KB per 8 s) | 13% |

The spinner-only state is cheap on this version. The burn lives in the streaming path.
Each incoming chunk schedules a diffed render frame. The diffs still amount to ~26 KB/s of
cell traffic for a 2.6 MB/s flood, and every frame repaints the Zed terminal surface.
One frame per burst is enough cost. No single frame is heavy.

The env-var claim was checked at the byte level: the installed binary contains 52
`OPENCODE_*` names and none of them mention FPS. Upstream state on
`anomalyco/opencode` (the repo moved from `sst/opencode`, links still redirect):

- PR #13814 (`OPENCODE_EXPERIMENTAL_FPS`) — closed, not merged.
- PR #13901 (web terminal FPS) — closed, not merged.
- Current source hardcodes `targetFps: 60` in `packages/tui/src/app.tsx` with no config hook.

Only one lever ships in the TUI plugin API: the plugin context exposes `renderer: CliRenderer`,
and code inside the product clamps `renderer.targetFps` and `renderer.maxFps` at runtime
(`packages/tui/src/component/dialog-go-upsell.tsx`).

## Environment

- Arch Linux, kernel 7.2.14-zen1, Intel TigerLake Iris Xe, KWin Wayland, all panels at 60 Hz.
- zed 1.27.0+stable, opencode 2.2.6 (`~/.bun/install/global/node_modules/@opencode/cli`).
- `intel-gpu-tools`. The CSV flag on this build is `intel_gpu_top -c`. The CSV has no
  per-process rows, so attribution is by A/B capture, not per process.
- System load in the idle states measured near zero CPU for all suspects (zed 0.26%,
  kwin 0.3%, opencode processes under 0.5%). The load is GPUs-side only.

## Impact

- Agent-heavy work in a Zed pane holds the GPU near 80% and keeps portable power draw at
  10 to 12 W extra (fan noise, battery).
- Light sessions (prompt, reading, short answers) cost almost nothing.
- The effect scales with streamed output volume: giant tool dumps are the worst input.

## Workaround

Ranked by measured payoff:

1. Run long agent turns in a standalone terminal, not in a Zed pane. This moved the measured
   render-engine load back to the Zed-alone baseline. Costs nothing in configuration.
2. Make the agent stream less output. Small outputs cost little regardless of other settings.
3. Optional: keep a low fps cap from a local TUI plugin. Measured gain: streaming p50 from
   ~76% to ~64%, and no idle cost. The repo carried such a plugin at
   `dot_config/opencode/plugins/fps-cap/tui.ts` (commit 1c4b682) and removed it on 2026-11-07
   as insufficient. Restore it from that commit if a small gain helps.
4. Do not rely on TUI appearance settings. Idle pain was already small (about 7%), so
   `animations: false` does not address the main driver.
5. Rebuild Zed with the Wayland present mode returned to Fifo (set `preferred_present_mode: None`
   at `crates/gpui_linux/src/linux/wayland/window.rs:588`), pending any upstream request for a
   runtime knob. Not yet attempted. Zed builds take a long time. Fifo also re-openes the
   frame-callback stalls that #57077 fixed on some compositor+driver pairs (mainly NVIDIA
   Hyprland and RADV). Our Mesa i915 + KWin pair is believed unaffected, but unverified.

## Suspected cause

Each chunk of streamed output schedules a TUI redraw, up to the frame cap. Each redraw writes
diff cells to the terminal, and the Zed terminal surface after it. The render engine stays
busy for as long as output arrives, so the load follows the stream cadence, not the animation
loop. Confidence: verified with the A/B captures above plus the `/proc` tty and CPU sampling
in this report.

The Zed side carries its own amplifier: on Wayland, gpui hardcodes
`PresentMode::Mailbox` (merged 2026-05-19 in `zed-industries/zed` #57077, present in our
zed 1.27.0 from 2026-11-04). Mailbox never blocks the queue, so pending frame redraws from
terminal content get submitted at whatever rate the events arrive, unlike X11-with-Fifo
(vsync-paced). The same stall-free choice that fixed Wayland freezes on NVIDIA/RADV
(#50229, #55345) is the behavior that lets streaming saturate the render engine here.
An exact split needs the per-frame counters, which the CSV mode of `intel_gpu_top` does
not carry.

## Related

- Problem measurement history and the lever ranking live in project memory of the dotfiles
  agents (search for "OpenCode TUI GPU load").
- Upstream feature request for a reconnected fps limit: `anomalyco/opencode` issue #13817,
  and the drifting CPU work in issue #22017. Both PRs #13814 and #13901 stopped at review.
- Upstream product commits in this area: 59235 "perf(tui): step the tab pulse at 20 fps
  instead of holding the renderer live".
- `anomalyco/opencode` #42306 (open): spinner loop burned ~1 core on v1.18 with ~15 fps
  tty writev while status was running. The same state costs 0.7% CPU on 2.2.6 here, so the
  loop got cheap after v1.x. The report keeps the numbers for whoever reopens that thread.
- `anomalyco/opencode` #18446: opencode TUI active raised macOS WindowServer CPU, the same
  compositor-side shape as ours on KWin.
- `anomalyco/opencode` #6172: on VSCode, the terminal bring-burn reproduced with plain
  `btop` too, so part of the cost belongs to the editor terminal pipeline in general.
- `anomalyco/opencode` #42657 (open): render thread saturation during concurrent agents.
  One tester named Zed's integrated terminal on Windows as the aggravator.
- `zed-industries/zed` #57077 (merged 2026-05-19): hardcoded `PresentMode::Mailbox` on
  Wayland to stop FIFO stalls on NVIDIA/Hyprland and RADV. A likely amplifier here because
  it removes the vsync backpressure that paced terminal repaints. Candidate upstream
  request: a runtime knob (setting or env var) for present mode.
