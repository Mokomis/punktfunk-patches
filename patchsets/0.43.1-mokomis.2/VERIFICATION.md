# Verification — October 9, 2026

Android client `0.43.1-mokomis.2` (arm64, application id `io.unom.punktfunk.mokomis`) for an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, ColorOS 16).

This is the [`0.42.0-mokomis.8`](../0.42.0-mokomis.8) patch series ported to upstream `v0.43.1`. It replaces `0.43.1-mokomis.1`, which carried only the first five patches and was never run.

## The port

| Patch | Result on v0.43.1 |
|---|---|
| The first five (HDR presenter, pin on a timing-only wall, 4:4:4, display HDR range, Wi-Fi line) | Ported in an earlier session |
| Wi-Fi line load fix, fragment iDWT path, GPU step timing, Wi-Fi wording | Applied unchanged |
| Frame presentation setting | Applied; one test-file conflict with upstream's new `padRumble` setting |
| Per-title presets and the console row | Merged by hand. Upstream had added a Second screen row and install/remove actions on library tiles in the same places; both sets of additions are kept |

## Results

- **App unit tests:** `./gradlew :app:testDebugUnitTest` passed, 236 tests.
- **Console interface tests:** `cargo test -p pf-console-ui --lib` passed, 405 tests (8 ignored), on macOS.
- **Reproducibility:** the twelve patches applied in order to a clean `v0.43.1` tree, and the result matched the built source with no differences outside the app-id files.
- **Install:** installed over `0.42.0-mokomis.8` with the same signing key; settings and host pairing carried over.
- **Against a 0.42.0 host** (`0.42.0+reconnect-fix.3`): connects and streams. In the log of the first session: the panel's HDR range sent (`peak=1600.0 min=0.001 nits`), `present backend = SurfaceView (frame presentation setting or sysprop)`, `presenter = arrival`, decoder `c2.qti.hevc.decoder.low_latency`. A later game session ran HEVC at about 100 fps and 95 Mb/s with no dropped frames, and the user reported it working normally.

## Not yet exercised on this build

- PyroWave, so the fragment iDWT path and the GPU step timing on upstream's reworked wavelet presenter.
- Per-title presets: creating one, the picker, a bound launch.
- A `v0.43.1` host. That host runs the virtual display at twice the stream rate, which may change the judder that the Frame presentation setting was added for; the comparison of the default path against Direct should be repeated there.
