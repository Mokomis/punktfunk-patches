# Verification — October 3–4, 2026

Tested Android client `0.43.0-mokomis.1` (arm64, application id `io.unom.punktfunk.mokomis`) on an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`. Stream: 2520×1680, 144 Hz, PyroWave 10-bit HDR over 6 GHz Wi-Fi 7.

## Patches, in application order

| Patch | Purpose |
|---|---|
| `android-pyrowave-hdr.patch` | Port of the 0.41.0 HDR fix: the PyroWave presenter opens an HDR10 (ST 2084) surface when the session is HDR and forwards HDR metadata. Falls back to SDR when the surface offers no HDR10 format. |
| `pyrowave-pin-timing-wall.patch` | The connect-time ramp no longer lowers a PyroWave pin when its wall lost no packets (every packet arrived, late). A wall with real loss still lowers it. Adds one unit test. |
| `android-custom-app-id.patch` | Build configuration only: separate application id and label, arm64 only. |

## Results

- **HDR:** the client logged an `A2B10G10R10_UNORM_PACK32 HDR10_ST2084_EXT` swapchain on every connect and the overlay reported PyroWave 10-bit HDR. Picture quality was judged by eye only.
- **Pin fix:** observed live on three connects. The ramp reported a wall at 516–533 Mb/s and the client logged `PyroWave pin kept, the ramp's wall lost no packets`, staying at the host cap (750 and 850 Mb/s). The unpatched 0.41.0 client lowered the same sessions to 336–381 Mb/s.
- **Unit tests:** `cargo test -p punktfunk-core --lib abr` passed, 168 tests, on macOS.
- **Stream at a 1000 Mb/s host cap:** 1003 Mb/s delivered at 144 fps, no dropped frames in nine consecutive 10-second windows after connect, decode 4.3 ms, end-to-end 15.6 ms median. This is a 90-second observation, not a soak test.
- **Version skew:** a 0.43.0 client connected and streamed against the 0.42.0 host on `punktfunk/1`. On most connects the 0.42.0 host left the ramp unanswered, so the pin fix was exercised on only some of them.

## Limitations

- The pin fix trades safety for bitrate: a link that truly cannot carry the pin also delivers packets late, and with this patch PyroWave stays at the pin and drops frames instead of fitting to the link. It suits a link known to carry the cap; it is not suitable for upstream as written.
- The earlier low ramp readings were taken on a Wi-Fi association stuck at half channel width and one spatial stream in the downlink. Re-associating restored 320 MHz and two streams. The ramp was measuring that link honestly.
- A separately signed build has its own pairing identity. The identity is wrapped by a per-app Android Keystore key and cannot be copied from the official app. Pair once; updates installed over the same application id keep it. A saved host card copied from another app must be removed first, or the client attempts a silent reconnect and times out.
- **Controller input:** with a USB telescopic controller, some controller buttons stopped working correctly in several sessions, on both the 0.43.0 and the 0.42.0 build. The cause was not identified. Every affected session had been started remotely over adb with simulated taps or key presses, several of them after switching codec between AV1 and PyroWave; sessions started by hand with the controller worked on the 0.42.0 build. Whether the 0.43.0 build has any input problem of its own is unknown. An earlier version of these notes blamed the 0.43.0 client against the 0.42.0 host; that was not established.
- No long-session, thermal or battery testing. Other Android devices and other codecs were not tested.

## Actual build environment

Built on macOS with Rust 1.96, cargo-ndk 4.1.2, NDK 30.0.14904198, compile SDK 37, and OpenJDK 21. Debug variant, signed with the local Android debug key.

```sh
cd clients/android
VERSION_NAME=0.43.0-mokomis.1 ./gradlew :app:assembleDebug
```
