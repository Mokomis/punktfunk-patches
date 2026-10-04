# Verification — October 4, 2026

Tested Android client `0.42.0-mokomis.1` (arm64, application id `io.unom.punktfunk.mokomis`) on an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`. Stream: 2520×1680, 144 Hz, PyroWave 10-bit HDR over 6 GHz Wi-Fi 7.

This is the same three patches as [`0.43.0-mokomis.1`](../0.43.0-mokomis.1), carried onto the host's own release. Both source patches applied to v0.42.0 without conflicts. Use this patchset with a 0.42.0 host.

## Why this base

With the 0.43.0 client against the 0.42.0 host, some buttons on a USB telescopic controller (seen by Android as an Xbox 360 pad) did not work correctly. The official 0.41.0 client and this 0.42.0 build both work with the same controller and host. Which buttons failed, and which 0.43.0 change is responsible, were not identified.

## Results

- **Controller:** buttons reported working by the user on this build. No per-button test was recorded.
- **Pairing:** installed over `0.43.0-mokomis.1` with the same signing key. The identity file was unchanged and the client connected without pairing again.
- **HDR:** the client logged an `A2B10G10R10_UNORM_PACK32 HDR10_ST2084_EXT` swapchain.
- **Pin fix:** on the first connect the ramp reported a wall at 523 Mb/s and the client logged `PyroWave pin kept, the ramp's wall lost no packets`, staying at the 1000 Mb/s host cap.
- **Unit tests:** `cargo test -p punktfunk-core --lib abr` passed, 166 tests, on macOS.

Stream quality figures (bitrate, dropped frames, decode time) were measured on the 0.43.0 build and not repeated here.

## Limitations

The limitations in the 0.43.0 notes apply unchanged: the pin fix is a deliberate trade-off for a link known to carry the cap, a separately signed build needs pairing once, and there was no long-session testing.

## Actual build environment

Built on macOS with Rust 1.96, cargo-ndk 4.1.2, NDK 30.0.14904198, compile SDK 37, and OpenJDK 21. Debug variant, signed with the local Android debug key.

```sh
cd clients/android
VERSION_NAME=0.42.0-mokomis.1 ./gradlew :app:assembleDebug
```
