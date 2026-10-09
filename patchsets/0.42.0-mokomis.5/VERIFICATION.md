# Verification — October 6, 2026

Android client `0.42.0-mokomis.5` (arm64, application id `io.unom.punktfunk.mokomis`) for an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, stock Qualcomm Vulkan driver) against Windows host `0.42.0+reconnect-fix.3`.

This is [`0.42.0-mokomis.4`](../0.42.0-mokomis.4) plus one patch. The other seven patches are byte-identical to that set.

## The added patch

`pyrowave-fragment-idwt.patch` lets the PyroWave decoder run its inverse wavelet as fragment passes.

The codec has two ways to do that step, compute shaders or render passes, and a function that says which a driver does better with (`pyrowave_decoder_device_prefers_fragment_path`; it answers fragment for Qualcomm's and Arm's own drivers). The client had always opened the decoder on compute. It now asks the codec. On the fragment path the three output planes are created as colour attachments in place of storage images and handed to the codec in `ATTACHMENT_OPTIMAL`; they still end each frame in `GENERAL`, which is what the presenter samples from. If the plane format cannot be rendered to on a device, the client warns and uses compute.

The open log line names the path: `PyroWave decoder open on the presenter's device (BT.709 limited) … idwt="fragment"`.

To force a path on Android for the next session, without rebuilding:

```sh
adb shell setprop debug.punktfunk.pyro_idwt compute    # or: fragment
adb shell setprop debug.punktfunk.pyro_idwt ""         # back to the codec's choice
```

The property is read when a stream starts and is lost on reboot.

## Results

One run per path, same session settings, same area of the same game, switched with the property above: 2520×1680, 120 Hz, 10-bit 4:2:0 HDR, about 1,125 Mb/s, 320 MHz Wi-Fi, GPU clock floor at 1025 MHz.

| Measure | Compute | Fragment |
|---|---|---|
| GPU busy, 30 samples over one minute, average | 50% | 37% |
| GPU busy, peak | 52% | 40% |
| Decode time in the overlay | 4.3, 4.4 ms | 3.2, 3.8, 3.9 ms |
| GPU temperature at the end of the minute | 52.7 °C | 53.1 °C |
| Frame rate | 120 fps | 120 fps |
| Frames dropped once the stream had settled | 0 | 0 |

- **Picture:** intact on the fragment path in every screenshot, in HDR.
- **Path chosen:** with the property unset the log showed `idwt="fragment"`; with it set to `compute`, `idwt="compute"`.
- **Reproducibility:** the eight patches applied in order to a clean `v0.42.0` tree, and the result matched the built source with no differences outside the app-id files.

## Limits

- One run per path, a minute of sampling each. The two scenes were close but not identical (the player had moved and enemies had arrived in the compute run).
- A minute is too short to show any difference in heat or battery drain. Not measured.
- Both runs dropped frames in the first 40 seconds after connect (12 on fragment, 21 on compute) with receive gaps of about a second; that happened on both paths and is not from this patch.
- 4:4:4 and 8-bit SDR were not run on the fragment path. Only the 10-bit (R16) plane format was exercised.
- A mid-session resolution change (the decoder's reconfigure path) was not exercised.
- Tested on one device and one driver. Mesa's Turnip, where the codec chooses compute, was not run.
- Only the Android client was built. The change is in shared client code (`pf-client-core`), so desktop clients built from this tree would also follow the codec's choice; none was built or run.

## Also seen in this session

The `mokomis.4` notes list its overlay fix as not yet observed on the device. In these sessions the Wi-Fi line named 320 MHz in the game and on a still desktop, with no false warning.
