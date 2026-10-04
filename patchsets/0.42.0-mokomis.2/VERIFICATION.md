# Verification — October 4, 2026

Tested Android client `0.42.0-mokomis.2` (arm64, application id `io.unom.punktfunk.mokomis`) on an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`. Stream: 2520×1680, 120 Hz, PyroWave 10-bit HDR over 6 GHz Wi-Fi 7, host PyroWave cap 1125 Mb/s.

This is [`0.42.0-mokomis.1`](../0.42.0-mokomis.1) plus one patch. The HDR and pin patches are byte-identical to that set.

## The added patch

`android-pyrowave-444.patch` makes the client advertise `VIDEO_CAP_444` when PyroWave is the preferred codec and the device can decode it. Upstream leaves this off on Android and has no setting for it there. The PyroWave decoder already handles 4:4:4, so nothing else changes.

There is no switch on the tablet. The host's **Full color 4:4:4** setting decides: on gives 4:4:4, off gives 4:2:0, at the next connect. Hardware codecs are never asked for 4:4:4.

## Results

- **4:4:4 negotiated:** the client logged `2520x1680 10-bit 4:4:4` on an `A2B10G10R10_UNORM_PACK32 HDR10_ST2084_EXT` swapchain, and the overlay showed 4:4:4. The picture looked correct to the user.
- **Decode at 120 Hz:** 6.5–6.6 ms with the GPU clock floor at 1225 MHz, 7.3 ms at 1025 MHz, against an 8.3 ms deadline. 118–120 fps and no dropped frames in the windows sampled. At stock GPU settings decode took 10.0 ms and the stream fell to 86 fps, so 4:4:4 at this resolution needs the floor.
- **Latency:** 17.8–19.3 ms median capture-to-decoded, about 3 ms more than 4:2:0 on the same setup.
- **Not sustainable at these settings.** From a cool start the GPU reached 88 °C and the surface estimate 49.5 °C, and after about 13.5 minutes the tablet cut the GPU clock from 1225 to 646 MHz. Lowering the floor to 1025 MHz did not cool it. The heat follows the decode workload, about twice that of 4:2:0.
- **4:2:0 on this build:** with the host setting off the stream is 4:2:0 as before. At 120 Hz it decoded in 3.9–4.1 ms at the 1225 MHz floor with the GPU about 42% busy.
- **Pairing:** installed over `0.42.0-mokomis.1` with the same signing key. The identity file was unchanged.
- **Pin fix:** still active. On the 4:4:4 connect the ramp reported a wall at 536 Mb/s and the client kept the 1125 Mb/s pin.

## Limitations

- The new unit test (`full_chroma_is_asked_for_only_when_told`) was not run: the Android client crate builds only for Android. The build compiled it out; the behaviour was checked on the device instead.
- If the host cannot provide PyroWave and falls back to HEVC while this capability is advertised, it may send HEVC 4:4:4, which the tablet's hardware decoder very likely cannot decode. Turning the host's 4:4:4 setting off avoids it. This was not observed.
- 4:4:4 at 90 Hz or at a lower resolution, which would reduce the heat, was not tested.
- The controller-input and other limitations in the `0.42.0-mokomis.1` notes still apply.

## Actual build environment

Built on macOS with Rust 1.96, cargo-ndk 4.1.2, NDK 30.0.14904198, compile SDK 37, and OpenJDK 21. Debug variant, signed with the local Android debug key.

```sh
cd clients/android
VERSION_NAME=0.42.0-mokomis.2 ./gradlew :app:assembleDebug
```
