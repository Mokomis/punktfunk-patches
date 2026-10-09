# Verification — October 6, 2026

Android client `0.42.0-mokomis.6` (arm64, application id `io.unom.punktfunk.mokomis`) for an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`.

This is [`0.42.0-mokomis.5`](../0.42.0-mokomis.5) plus two patches. The other eight are byte-identical to that set.

## The added patches

### `pyrowave-gpu-step-timing.patch`

An optional readout of where the GPU time of a decoded frame goes. **Off by default.**

The codec already writes timestamps around its two steps; the patch reads them out every 600 frames. The Android presenter gains its own pair of timestamps around the colour-conversion draw. To turn both on for the next session:

```sh
adb shell setprop debug.punktfunk.pyro_stats 1     # "" turns it off; lost on reboot
adb logcat | grep -E "PyroWave GPU time|present draw GPU"
```

Readings taken with it on this tablet (fragment path, 2520×1680, 120 Hz, 10-bit HDR, GPU floor 1025 MHz), steady over a minute each:

| Step | 4:2:0 | 4:4:4 |
|---|---|---|
| Inverse wavelet | 1.83 ms | about 3.1 ms |
| Unpacking coefficients (dequant) | 0.75 ms | about 1.3 ms |
| Colour-conversion draw | 0.64 ms | about 0.6 ms |

At 4:2:0 the three add up to 3.2 ms of an 8.3 ms frame, 38%, against a measured GPU busy of 37%.

### `android-wifi-hud-reduced-wording.patch`

The overlay's Wi-Fi warning read `no 320 MHz seen` whenever the downlink rate stayed at or under 2,883 Mb/s under load. That is also what a 320 MHz link on one spatial stream reports. On October 6 the warning appeared while the radio reported `1921.5 MBit/s 320MHz EHT-MCS 9 EHT-NSS 1`. It now reads `reduced: 1 stream or under 320 MHz`. The logic is unchanged.

## Results

- **Unit tests:** `./gradlew :app:testDebugUnitTest --tests io.unom.punktfunk.WifiLinkLogTest` passed, 7 tests.
- **Timing option:** produced the readings above in two sessions. With the property unset, no timing lines are logged.
- **Install:** installed over the previous build with the same signing key.
- **New wording on the device:** not yet observed. The build was installed after the session that showed the old wording.
- **Reproducibility:** the ten patches applied in order to a clean `v0.42.0` tree, and the result matched the built source with no differences outside the app-id files.

## 4:4:4 on the fragment path

Run with this set's timing option on, and ruled out on heat: correct picture and 120 fps, but the GPU ran about 30 °C hotter than at 4:2:0 and was still climbing at 12 minutes. Details are in [`BACKLOG.md`](../../BACKLOG.md), Client item 3.

## Limits

Those of `0.42.0-mokomis.5` still apply to the fragment path. The presenter's draw timer exists only in the Android client.
