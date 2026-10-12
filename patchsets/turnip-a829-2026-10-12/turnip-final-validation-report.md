# Final Turnip validation — October 12, 2026

No further repeatable software speedup was found in this final round. Keep the existing reconstruction and queued-display changes, plus the completed-decode feedback fix. Cooling recovered most of the sustained FPS loss, making reduced GPU work or better cooling the clearest future direction at the same image settings.

## Sustained load and recovery

Same OPD2515 / Adreno 829 tablet and No Man’s Sky save, at 2414×1680@144, PyroWave 10-bit 4:2:0 HDR. The game continued running and its live scene can evolve; these live runs are not identical-pixel benchmarks. The separate shader replay uses the same saved capture for each variant.

After three minutes without streaming, the final installed APK streamed for ten minutes. Streaming stopped for three minutes, followed by a two-minute recovery run. Android retained control of thermal limits throughout.

| Phase | Measured FPS | GPU state |
|---|---:|---|
| First 90 seconds of sustained run | 137.0 mean of valid samples | 925–975 MHz at the sampled instants |
| Last 90 seconds of sustained run | 124.0 mean | 646 MHz |
| After cooling, two-minute recovery | 136.2 mean of three valid samples | 891–1075 MHz |

Battery temperature went from 37.0°C at sustained-test startup to 42.1°C at the final health sample, briefly peaking at 42.3°C after stopping. Battery level fell 69→63% during the sustained test. Battery temperature lags the processor temperature: after three idle minutes, Android’s thermal status returned to light and its allowed GPU maximum returned to 1225 MHz even though the battery remained warm. See [Android thermal status definitions](https://developer.android.com/reference/android/os/PowerManager). Current units were not verified; there is no watt estimate.

This repeats the earlier slowdown and shows that much of it reverses after cooling. It does not establish the benefit of a particular external cooler or guarantee unlimited sustained 144 FPS.

## Where GPU time increased

Means of the first and last twelve logged GPU windows, each aggregating hundreds of frames:

| Stage | Early ms | Late ms |
|---|---:|---:|
| Reconstruction | 1.811 | 2.238 |
| Dequantization | 1.098 | 2.418 |
| Display draw | 1.269 | 1.452 |

Dequantization showed the largest growth. These live windows also differ in temperature and automatic bitrate, so they locate pressure rather than isolate a shader defect. GPU timestamps exclude physical screen scanout; their sum is not the HUD’s end-to-end latency.

## Decode feedback works

The controller recorded 19 retarget events with positive `decode_mean_us` values, typically about 10–11 ms under thermal pressure. Previously this input was missing (`-1`). The controller tried lower bitrates, restored them when latency did not follow the rate, and increased its interval between probes. These probes did not produce a lasting FPS recovery. The fix supplies the expected input; it does not change the controller policy or demonstrate a new FPS gain.

No bitrate, FPS, resolution or image-quality preference was manually reduced. Automatic bitrate did temporarily change during the test, as the existing policy allows; unchanged preferences do not mean a constant bitrate.

## Final shader experiment

The candidate derives 8-bit and 16-bit payload values from the existing 32-bit sampled texture rather than fetching through separate texture views. It keeps subgroup size 64 and the current reconstruction shader.

All three storage-mode shaders compiled and passed SPIR-V validation. In the actual linear-texture mode, all 48 compared output planes from 16 decoded frames matched the control byte-for-byte.

Six alternating replay runs per variant measured 2.4345 ms mean dequantization for the control and 2.5043 ms for the candidate. The early control benefited from a cooler state; the last four runs averaged 2.4968 versus 2.5113 ms, near parity. GPU frequency was not locked, and the recorded pre-run frequency is an idle sample, not an active fixed-clock guarantee. There is no repeatable gain, so the candidate was rejected and was never installed in the normal client.

## Pacing, memory and limits

The full sustained presentation trace and periodic logs are preserved. Median presentation interval was about 6.95 ms, p95 about 13.90 ms; roughly 88.6% of observed adjacent intervals were one refresh, 10.5% two refreshes and 0.8% longer. The longest observed interval was about 264 ms. Thermal slowdown and automatic-rate changes occurred during this run; the exact cause of individual long gaps was not isolated.

PSS rose from 464678 to 478978 KiB, about 14 MiB including warm-up; the final four samples ranged from about 476–479 thousand KiB. This run alone does not establish a leak or prove perfectly flat memory. The prior ten-minute test was flatter. No device-loss, fence-timeout or panic matched the captured application logs. Log snapshots were taken every 30 seconds; these are sampled retained logs, not a guarantee that every system event was captured.

The Android build and all 43 adaptive-controller tests passed. Both source diffs passed whitespace checks, and the combined patch passed reverse-application validation against the tested tree. The repository writing check still rejects existing patch commit titles; diagnostics are retained rather than rewriting unrelated history.

## Final installed state and archive

The APK remains `punktfunk-turnip-decode-feedback.apk`. Turnip is selected, reconstruction and queued display remain automatic for the tested device, all temporary profiling/experiment properties are clear, and automatic rotation is restored. The final screenshot showed 134 FPS, target 1125 Mb/s and HUD decode 4.9 ms after restarting normal streaming; it is a spot check, not another sustained result. DroidDeck was untouched.

The driver ZIP was verified byte-for-byte against the driver bundled in the APK. All six driver/hook libraries in the APK match `turnip-client-native-libraries.zip`.

The complete session archive preserves the earlier builds, reports, screenshots and capture. The final validation archive holds this phase’s raw traces, shader source/SPIR-V, manifests and helpers. The source archive and combined patch support reproduction; no signing private key or pairing database is included.
