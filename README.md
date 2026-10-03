# Punktfunk reconnect patches

Private archive of tested Windows host fixes for reuse after official updates. Upstream: [unom/punktfunk](https://git.unom.io/unom/punktfunk). This repository does not publish or modify the upstream project.

## Current patchset

[`patchsets/0.42.0-reconnect-fix.3`](patchsets/0.42.0-reconnect-fix.3) targets **v0.42.0**, commit `8f046f239f3d6dcfc1fa0a25343be926a233a5a5`. The tested executable identifies itself as `0.42.0+reconnect-fix.3`.

The patch makes the virtual-display keepalive worker interruptible, skips the video drain when a session is stopped, waits for complete session teardown instead of an unconditional 1.5-second handoff delay, and bounds silent Windows audio reads to 100 ms so the audio sender notices stop promptly. The existing 1.5-second maximum handoff grace is retained. No driver source is changed.

The tested binary, patch and checksums are attached to the matching GitHub release. Keep the executable out of Git history.

## Apply to the tested release

Clone the upstream source, check out the tested commit, then run:

```sh
python3 /path/to/punktfunk-patches/scripts/apply.py /path/to/punktfunk --check
python3 /path/to/punktfunk-patches/scripts/apply.py /path/to/punktfunk --apply
```

The helper checks the patch checksum, requires the tested base commit, rejects tracked working changes, and detects an already-applied patch. It does not build or install anything. It refuses an untested newer base rather than applying automatically.

## When an official release arrives

1. Check whether upstream already fixed these issues. If so, use the official release.
2. For fixes still missing, review their current code and port only those changes. A clean patch application alone does not establish compatibility.
3. Build against the new release, run the relevant tests, then validate fresh startup and repeated reconnects on a silent desktop. Check audio, input and video after each handoff.
4. Save the new patchset under its own release directory with its exact base commit, build version, checksums and results. Preserve this tested set.

An official update may overwrite the custom executable. The separately configured `PUNKTFUNK_STANDBY_SINK_KEEP=1` is a host-specific configuration mitigation and is **not** part of this source patch. Review that setting independently when changing display arrangements.

## Build and restore

On Windows with the upstream build prerequisites installed, apply the patch and build the host with its normal default features plus NVENC and QSV:

```powershell
$env:PUNKTFUNK_BUILD_VERSION = '0.42.0+reconnect-fix.3'
cargo build --release --target x86_64-pc-windows-msvc -p punktfunk-host --bin punktfunk-host --features nvenc,qsv
```

See [verification and build notes](patchsets/0.42.0-reconnect-fix.3/VERIFICATION.md) for the actual cross-build used to produce the release asset.

The saved executable is for the **0.42.0 Windows x64 host**, tested with driver `9.9.1001.1005` and protocol 9. Use it with the matching installation; do not install this older executable over an arbitrary newer host/driver combination.

Before replacement, back up the installed executable. Stop `PunktfunkHost`, replace `C:\Program Files\punktfunk\punktfunk-host.exe`, start the service, and check its version and health. Restore the backup if startup fails. Keep the official installer available for recovery.

## License

The patch derives from upstream Punktfunk, licensed under MIT or Apache-2.0. Both upstream license files are included. Preserve upstream attribution when reusing or sharing the patch.
