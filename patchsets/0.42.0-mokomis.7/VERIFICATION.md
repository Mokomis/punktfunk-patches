# Verification — October 8, 2026

Android client `0.42.0-mokomis.7` (arm64, application id `io.unom.punktfunk.mokomis`) for an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, ColorOS 16) against Windows host `0.42.0+reconnect-fix.3`.

This is [`0.42.0-mokomis.6`](../0.42.0-mokomis.6) plus one patch. The other ten are byte-identical to that set.

## The added patch

`android-frame-presentation.patch` adds a client setting, **Frame presentation** (Settings, Display, advanced; stored as `android.frame_presentation`), for how hardware-decoded frames reach the panel. It applies to HEVC, AV1 and H.264. PyroWave has its own presenter and ignores it.

| Choice | Path | Stored value |
|---|---|---|
| Automatic (default) | ASurfaceControl, one frame per vsync slot. Upstream's behaviour. | `auto` |
| Direct | SurfaceView with the timeline presenter | `direct` |
| Direct, on arrival | SurfaceView, each frame released the moment it is decoded | `arrival` |

Both alternatives already existed upstream, reachable only through debug properties (`debug.punktfunk.present_backend`, `debug.punktfunk.presenter`) that are lost on reboot. The patch makes them a stored setting; the properties still override it.

## Why

On October 8 an HEVC stream at 2520×1680, 144 Hz, with the game running at 70–100 fps, juddered heavily on this tablet. PyroWave in the same game at the same rate did not. The panel has fixed 60/90/120/144 Hz modes and no adaptive refresh.

Each variant was run in turn in the same scene, switched with the debug properties and judged by the user:

| Variant | Verdict by eye | Ready-to-panel wait (`latchMs` p50) | Capture to display (`e2eMs` p50) |
|---|---|---|---|
| Automatic (ASurfaceControl) | Heavy judder | 12–15 ms | 26–31 ms |
| Direct (SurfaceView, timeline) | Smooth | about 3 ms | about 18 ms |
| Direct, on arrival | Smooth, "a tad better" | not reported in this mode | not reported in this mode |

On the default path the presenter's own counters looked correct: at about 101 fps it showed 59 frames for one refresh and 42 for two each second, with no discards and almost no slot misses. That split is what a 101 fps source on a 144 Hz panel requires, so the overlay's judder figure (about 415‰) mostly restates the rate mismatch. Why the default path looks worse and holds frames about 10 ms longer on this device is **not established**.

## Results

- **Unit tests:** `./gradlew :app:testDebugUnitTest` passed, 205 tests, including the settings row, round-trip and catalogue checks.
- **Install:** installed over `0.42.0-mokomis.6` with the same signing key.
- **The setting from the app:** verified on October 9. With **Direct, on arrival** chosen in the settings screen and both debug properties unset, an HEVC session logged `decode: present backend = SurfaceView (frame presentation setting or sysprop)` and `decode: presenter = arrival`. That session showed the desktop, not a game, so the smooth result itself still rests on the debug-property runs in the table above.
- **Reproducibility:** the eleven patches applied in order to a clean `v0.42.0` tree, and the result matched the built source with no differences outside the app-id files.

## Limits

- One game, one evening, one stream mode (144 Hz with a 70–100 fps source), judged by eye.
- Not checked: a source that holds the stream's rate (for example a steady 120 fps on a 120 Hz stream), AV1, other refresh rates, the smoothness priority with its buffer, any other device.
- End-to-end delay in the on-arrival mode was not measured; the overlay reports capture-to-decoded there (about 12 ms), which leaves out the display stage.

## Also seen in the same session

- The client chose `c2.qti.hevc.decoder.low_latency`, which advertises a 70 Mb/s ceiling, and the stream ran at 62–78 Mb/s against a 150 Mb/s target. Picture quality, not judder; not followed up.
- The tablet's GPU clock floor was at stock during the PyroWave comparison (decode 8.8 ms, 56% GPU busy) and the stream still looked smooth.
