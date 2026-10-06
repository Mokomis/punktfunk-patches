# Verification — October 5, 2026

**Not installed and not tested against the symptom.** These two host patches were written from the measurements in [`BACKLOG.md`](../../BACKLOG.md) (Host, item 1: audio channel stalls). They compile and their unit tests pass; whether either one changes what is heard is unknown until a patched host runs a real session.

They apply in order on top of v0.42.0 with [`0.42.0-reconnect-fix.3`](../0.42.0-reconnect-fix.3) applied. Neither changes anything on the wire, so no client change is needed. The first can be installed alone.

## 01 — `01-audio-egress-stall-stats.patch`

The host counts an audio frame as sent when `send_datagram` accepts it, which only queues it. This patch makes what happens afterwards visible, in the existing 30-second `audio egress` log line. New fields:

| Field | Meaning |
|---|---|
| `dgram_evicting` | Sends that found the 4 KiB datagram queue full; each makes the connection drop its oldest datagram |
| `dgram_queue_max` | Most bytes found still waiting before a send; 0 when every frame leaves before the next |
| `tx_stalls`, `tx_stall_max_ms` | Stretches of 20 ms or more, and the longest stretch, with datagrams queued and none sent |
| `tx_stall_cwnd`, `tx_stall_udp` | Congestion window during the longest stall, and UDP packets the connection still sent during it |
| `cwnd`, `cwnd_min`, `rtt_ms`, `rtt_max_ms`, `lost`, `cong_events` | The QUIC connection's own transport statistics for the window |
| `rt_timer_max_ms`, `rt_wake_max_ms`, `rt_late` | How late the async runtime ran a 5 ms timer and a wake from the audio thread; `rt_late` counts delays of 20 ms or more |

**How to read it after a session with audible gaps.**

- `tx_stalls` above 0 with `rt_timer_max_ms` or `rt_wake_max_ms` high in the same line: the runtime was starved. Patch 02 is aimed at exactly this.
- `tx_stalls` above 0 with the `rt_*` fields low, and `cwnd_min` collapsed, `lost` or `cong_events` above 0, or `tx_stall_udp` above 0: the transport was running and chose to wait. Patch 02 will not help; the congestion controller or pacing is the place to look.
- `tx_stalls` at 0 while the client still logs gaps: the delay is after the host's QUIC stack (network or client), and neither candidate cause is right.

## 02 — `02-quic-own-runtime.patch`

Builds the QUIC endpoint, and accepts each connection, with a separate one-thread runtime (thread name `punktfunk1-quic`) current, so the endpoint driver, connection drivers, socket and transport timers run there and not on the two-worker serving runtime that session code blocks. Session code is not moved; it uses the connection through its handle from where it ran before. The `audio egress` line gains `quic_timer_max_ms`, `quic_wake_max_ms` and `quic_late` for the new runtime beside the `rt_*` fields for the serving one.

**Risks.**

- It is a guess at the cause until patch 01's numbers say the runtime is the one stalling.
- One thread now carries all QUIC work for every session. For one client that is far more than enough; it was not measured with several.
- The browser (WebTransport) plane builds its own endpoint and is left on the serving runtime.
- Shutdown order changed slightly: the new runtime is declared before the endpoint and shut down in the background on drop. Exercised only by a unit test, not by a real service stop.
- It touches `native.rs` near code the reconnect patch also changed. The reconnect behaviour was not re-measured.

## What was checked

On macOS (the host's platform-independent code), Rust toolchain as in the reconnect patchset:

- 18 new unit tests pass (`native::egress_watch` 10, `native::rt_lag` 4, `native::quic_rt` 4). Two of them are a matched pair on a loopback QUIC connection: with the serving runtime's only thread blocked for 400 ms, a datagram arrives in under 200 ms on the dedicated runtime and waits out the block without it.
- Full host test run: 909 passed, 3 failed. The same 3 fail on the unpatched base on this Mac (`game::gamelease::…reports_running_at_once`, `mgmt::…host_info_reports_identity_and_ports`, `native::…clipboard_control_and_fetch_decline_over_session`), so they are not caused by these patches.
- `cargo xwin check -p punktfunk-host --target x86_64-pc-windows-msvc` finishes without errors with both patches applied.

Not done:

- No Windows executable was built. The check above type-checks the Windows code; it does not link a binary.
- Nothing was run on Windows, and no session was streamed.
- Patch 01 alone was not compiled separately for Windows (it was the committed state the tests were first written against; only the combined result was checked there).
- `cargo clippy` was not run.
