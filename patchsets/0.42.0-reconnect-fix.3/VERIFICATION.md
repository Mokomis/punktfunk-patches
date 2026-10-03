# Verification — October 3, 2026

Tested Windows host x64 with Punktfunk driver 9.9.1001.1005, protocol 9, and Android client 0.41.0. Stream: 2520×1680, 144 Hz, AV1 HDR, NVENC.

| Observed build | Fresh startup | Reconnects |
|---|---:|---:|
| Official 0.42.0 with standby configuration mitigation | 1.985 s | 4.523 s |
| Custom reconnect-fix.1 | 1.956 s | 3.559 / 3.575 s |
| Custom reconnect-fix.2 | 1.962 s | 2.499 / 3.533 s |
| Installed reconnect-fix.3 | 1.978 s | 2.152 / 2.168 s |

These are individual observations to first video packet, not a statistical latency benchmark. The final two silent-desktop handoffs finished in 89 ms and 67 ms, without reaching the fallback timeout. Final diagnostics reported healthy capture, zero encoder drops, and full loopback/microphone readiness. Audible quality, image quality and tablet presentation latency were not re-benchmarked.

Validation: 167 virtual-display library tests passed; two keepalive cancellation tests and three lifecycle-wait tests also passed as Windows executables on the host. The source patch reverse-application check passed against the patched source. Deployment verified the executable checksum and service health, with rollback to the preceding executable on failed startup.

The second build's variable reconnect time exposed a silent-audio shutdown delay: the old sender waited in a five-second WASAPI read. The third build changes the Windows idle read budget to 100 ms and checks stop before processing the returned chunk. Active pacing and infill policy are unchanged.

## Actual build environment

Cross-compiled on macOS with Rust 1.96, cargo-xwin 0.23.1, LLVM 23.1.2 and the Windows x64 target. Default streaming features plus `nvenc,qsv` were enabled. The original Windows icon and PerMonitorV2 DPI manifest were compiled to a resource and linked into the executable.

The cross-build used `LIBCLANG_PATH`, `XWIN_CACHE_DIR`, `CMAKE_POLICY_VERSION_MINIMUM=3.5`, and `CFLAGS=-msse4.1` / `CXXFLAGS=-msse4.1` for the bundled audio dependency. The saved binary requires SSE4.1. An ordinary native Windows build uses the upstream build prerequisites and resource handling.

Remaining limitation: Windows monitor restoration/recreation accounts for most of the approximately two-second startup. The handoff still has the existing 1.5-second maximum if teardown stalls. These checks do not prove that every intermittent driver failure is eliminated.
