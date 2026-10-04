# Verification — October 4, 2026

Tested Android client `0.42.0-mokomis.3` (arm64, application id `io.unom.punktfunk.mokomis`) on an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`. Stream: 2520×1680, 120 Hz, PyroWave 10-bit HDR 4:2:0 over 6 GHz Wi-Fi 7, host PyroWave cap 1125 Mb/s.

This is [`0.42.0-mokomis.2`](../0.42.0-mokomis.2) plus two patches. The HDR, pin, 4:4:4 and app-id patches are byte-identical to that set.

## The added patches

| Patch | Purpose |
|---|---|
| `android-display-hdr-volume.patch` | An HDR session fills `Hello::display_hdr` from the panel's own luminance range (`Display.HdrCapabilities`), so the host's virtual display can advertise this panel's peak instead of its default. Nothing is sent on an SDR session or when the panel reports no peak. |
| `android-wifi-downlink-hud.patch` | One more line in the stats overlay: the Wi-Fi downlink rate the radio reports, and whether the connection has shown a 320 MHz downlink in the last minute. |

### Why the overlay line exists

On this tablet and a TP-Link Deco mesh, the 6 GHz downlink width is settled per Wi-Fi connection: some connections reach 320 MHz and some never go above 160 MHz, with the same node, channel and signal. A 160 MHz connection carries the 1125 Mb/s stream with drop bursts; a 320 MHz one carries it cleanly. The cause was not found. The line makes a narrow connection visible so the user can toggle Wi-Fi and reconnect.

Android reports no downlink width, so 320 MHz is inferred from a rate above 2883 Mb/s, which two streams on a narrower channel cannot reach. The verdict is held for a minute because a 320 MHz link also runs slower codings. After 30 seconds of stream without such a rate the line turns to the warning colour and reads `no 320 MHz seen`. The width only shows under load, so the line means little on an idle desktop.

## Results

- **Overlay line:** showed `wi-fi ↓ 2882 Mb/s · 320 MHz` while the driver (`iw dev wlan0 link`) reported `3459.3 MBit/s 320MHz EHT-MCS 8 EHT-NSS 2` about a second later. The warning state was not seen on the device; it is covered by the unit tests only.
- **Stream:** 1128 Mb/s at 120 fps, no dropped frames in four consecutive 10-second windows, 15.9 ms median capture-to-decoded, 4.4 ms decode with the GPU clock floor at 1025 MHz.
- **Display volume:** not confirmed on this build. The same change on a 0.43.0 build logged `display HDR luminance peak=1600.0 min=0.001 nits` on its one connect; on this build the connect-time log lines had been overwritten before they were read. Whether the Windows host applied the value to its virtual display was not checked.
- **Unit tests:** `./gradlew :app:testDebugUnitTest --tests io.unom.punktfunk.WifiLinkLogTest` passed, 6 tests, 2 of them new.
- **Pairing:** installed over `0.42.0-mokomis.2` with the same signing key. The identity file was unchanged and the client connected without pairing again.
- **Reproducibility:** the six patches applied in order to a clean `v0.42.0` tree.

## Limitations

- The new Rust unit test for the display volume (`display_volume_is_sent_only_for_an_hdr_session_with_a_known_peak`) was not run: the Android client crate builds only for Android.
- The 320 MHz inference assumes a two-stream client. A device with more streams could exceed 2883 Mb/s on a narrower channel.
- The display volume uses BT.2020 primaries, the container the HDR10 surface presents in, not the panel's measured gamut.
- The limitations in the `0.42.0-mokomis.2` notes still apply.

## Actual build environment

Built on macOS with Rust 1.96, cargo-ndk 4.1.2, NDK 30.0.14904198, compile SDK 37, and OpenJDK 21. Debug variant, signed with the local Android debug key.

```sh
cd clients/android
VERSION_NAME=0.42.0-mokomis.3 ./gradlew :app:assembleDebug
```
