# Punktfunk patches

Private archive of tested Windows host and Android client fixes for reuse after official updates. Upstream: [unom/punktfunk](https://git.unom.io/unom/punktfunk). This repository does not publish or modify the upstream project.

## Windows host patchset

[`patchsets/0.42.0-reconnect-fix.3`](patchsets/0.42.0-reconnect-fix.3) targets **v0.42.0**, commit `8f046f239f3d6dcfc1fa0a25343be926a233a5a5`. The tested executable identifies itself as `0.42.0+reconnect-fix.3`.

The patch makes the virtual-display keepalive worker interruptible, skips the video drain when a session is stopped, waits for complete session teardown instead of an unconditional 1.5-second handoff delay, and bounds silent Windows audio reads to 100 ms so the audio sender notices stop promptly. The existing 1.5-second maximum handoff grace is retained. No driver source is changed.

The tested binary, patch and checksums are attached to the matching GitHub release. Keep the executable out of Git history.

## Android client patchsets

All build the Android client under the application id `io.unom.punktfunk.mokomis` and carry the same two changes: the PyroWave HDR10 presenter fix ported from 0.41.0, and a change that stops the connect-time ramp from lowering a PyroWave pin when its wall lost no packets. A further patch holds the build configuration. `0.42.0-mokomis.2` adds one more, which lets a PyroWave stream run at 4:4:4 when the host's **Full color 4:4:4** setting is on. That works, but at 2520×1680 and 120 Hz the tablet throttled its GPU after about 13 minutes; see its notes.

| Patchset | Base | Use with |
|---|---|---|
| [`patchsets/0.42.0-mokomis.4`](patchsets/0.42.0-mokomis.4) | v0.42.0, `8f046f239f3d6dcfc1fa0a25343be926a233a5a5` | A 0.42.0 host. **Current.** Fixes a false Wi-Fi warning in the stats overlay on a quiet stream. |
| [`patchsets/0.42.0-mokomis.3`](patchsets/0.42.0-mokomis.3) | v0.42.0, `8f046f239f3d6dcfc1fa0a25343be926a233a5a5` | A 0.42.0 host. Adds the panel's HDR range in the handshake and a Wi-Fi downlink line in the stats overlay. |
| [`patchsets/0.42.0-mokomis.2`](patchsets/0.42.0-mokomis.2) | v0.42.0, `8f046f239f3d6dcfc1fa0a25343be926a233a5a5` | A 0.42.0 host. Adds PyroWave 4:4:4. |
| [`patchsets/0.42.0-mokomis.1`](patchsets/0.42.0-mokomis.1) | v0.42.0, same commit | A 0.42.0 host, without 4:4:4. |
| [`patchsets/0.43.0-mokomis.1`](patchsets/0.43.0-mokomis.1) | v0.43.0, `d6920bf5dc7cb93673201b58bf9de61de3dcfbe5` | A 0.43.0 host. It also streamed against the 0.42.0 host. |

Matching the client's release to the host's is the safer choice. Controller buttons misbehaved in some sessions on both builds, for a reason that was not identified; see the notes. Each folder's `VERIFICATION.md` has results and limitations; the pin change is a deliberate trade-off for a link known to carry the host cap.

On a clean checkout of the patchset's base commit, apply in this order, then build:

```sh
P=/path/to/punktfunk-patches/patchsets/0.42.0-mokomis.4
git apply "$P/android-pyrowave-hdr.patch" "$P/pyrowave-pin-timing-wall.patch" \
  "$P/android-pyrowave-444.patch" "$P/android-display-hdr-volume.patch" \
  "$P/android-wifi-downlink-hud.patch" "$P/android-wifi-downlink-hud-load.patch" \
  "$P/android-custom-app-id.patch"
cd clients/android && VERSION_NAME=0.42.0-mokomis.4 ./gradlew :app:assembleDebug
```

`scripts/apply.py` covers the host patchset only. A separately signed client has its own pairing identity: pair it once with the host. Builds installed over the same application id keep it.

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
