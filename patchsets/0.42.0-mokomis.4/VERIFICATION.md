# Verification — October 4, 2026

Android client `0.42.0-mokomis.4` (arm64, application id `io.unom.punktfunk.mokomis`) for an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`.

This is [`0.42.0-mokomis.3`](../0.42.0-mokomis.3) plus one patch. The other six patches are byte-identical to that set.

## The added patch

`android-wifi-downlink-hud-load.patch` fixes a false warning in the overlay's Wi-Fi line.

The line added in `mokomis.3` turned to `no 320 MHz seen` after 30 seconds without a 320 MHz rate. A still desktop or a loading screen always met that: the access point sends narrow when there is little to send. On October 4 the warning appeared on an idle desktop while the same connection read 3,843 Mb/s at 320 MHz a moment later, and it led the user to believe the connection was a narrow one.

Now each one-second reading also records what actually arrived in that second (`TrafficStats.getTotalRxBytes`). Only seconds that carried at least 300 Mb/s count toward the warning, and it needs 30 of them inside the one-minute window. A quiet stream shows the rate with no verdict. A rate above 2883 Mb/s still names 320 MHz at once.

## Results

- **Unit tests:** `./gradlew :app:testDebugUnitTest --tests io.unom.punktfunk.WifiLinkLogTest` passed, 7 tests. Three cover the line: 320 MHz named from a rate, the warning only after 30 loaded seconds, and no verdict through two minutes of a quiet stream.
- **Install:** installed over `0.42.0-mokomis.3` with the same signing key. The identity file was unchanged.
- **On the device:** not yet observed. The build was installed with no stream running; the idle-desktop case and the 320 MHz case still need one session each to confirm by eye.
- **Reproducibility:** the seven patches applied in order to a clean `v0.42.0` tree, and the result matched the built source with no differences outside the app-id files.

## Correction to the `mokomis.3` notes: the display HDR range is verified

The `mokomis.3` notes list the display volume as not confirmed. It was confirmed later on October 4, on `0.42.0-mokomis.3`:

- The client logged `display HDR luminance peak=1600.0 min=0.001 nits` at connect and opened an `A2B10G10R10_UNORM_PACK32 HDR10_ST2084_EXT` swapchain.
- On the host, Windows Settings → System → Display → Advanced display → Display 2 (Punktfunk Virtual Display) showed **Peak brightness: 1,600 nits**, with 10-bit RGB and colour space "High dynamic range (HDR)" at 2520 × 1680, 120 Hz.

So the host applies the range the client sends. Before `android-display-hdr-volume.patch` the Android client sent none.

## Limitations

- The 300 Mb/s load threshold suits a high-bitrate PyroWave stream. A low-bitrate stream never counts as loaded, so it never gets the warning; it still gets the 320 MHz verdict when the rate shows it.
- `TrafficStats` counts all traffic on the device, not only the stream. Another large download would count as load.
- The limitations in the `mokomis.3` and `mokomis.2` notes still apply.

## Actual build environment

Built on macOS with Rust 1.96, cargo-ndk 4.1.2, NDK 30.0.14904198, compile SDK 37, and OpenJDK 21. Debug variant, signed with the local Android debug key.

```sh
cd clients/android
VERSION_NAME=0.42.0-mokomis.4 ./gradlew :app:assembleDebug
```
