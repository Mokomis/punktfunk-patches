# No Man’s Sky codec comparison — October 12, 2026

## Photo-mode follow-up and correction

Subsequent photo-mode captures found a roughly 4.1% horizontal scaling mismatch in the original comparison. Earlier softness reports therefore do not isolate codec quality. With matched full-panel dimensions, PyroWave and HEVC 800 look very close, with no convincing static-image winner. See [the photo follow-up](photo-codec-comparison-report.md). The measured latency results below remain the recorded live-run results.

For this live scene, PyroWave with the tested Turnip client retained more visible motion detail than HEVC or AV1 at 400 Mb/s in the user’s final full-screen checks. At 800 Mb/s, both conventional codecs were reported to look about the same as PyroWave. HEVC at that setting had similar measured latency; AV1’s latency was substantially higher.

Bandwidth was not scored or restricted to a common budget. The practical conclusion is to keep PyroWave for this quality-first setup. High-bitrate HEVC remains a competitive alternative; this test does not establish a clear quality or latency victory over HEVC at 800 Mb/s.

## Measured results

Same tablet, host and installed client: OPD2515 / Adreno 829, 2414×1680@144, 10-bit HDR. HEVC and AV1 opened `c2.qti.hevc.decoder.low_latency` and `c2.qti.av1.decoder.low_latency`, respectively; both hardware decoder names were verified in application logs, with no software fallback. PyroWave used the existing optimized Turnip build and its normal automatic quality settings. Its target stayed at 1125 Mb/s in the included samples.

| Configuration | Average displayed p50, ms | Average displayed p95, ms | User’s detail assessment |
|---|---:|---:|---|
| PyroWave / Turnip, target 1125 auto | 16.9 | 19.3 | Reference picture |
| HEVC, target 400 | 15.9 | 19.0 | Softer in final landscape check |
| HEVC, target 800 | 17.4 | 21.6 | About the same as PyroWave |
| AV1, target 400 | 17.9 | 21.5 | Softer in landscape |
| AV1, target 800 | 28.1 | 35.2 | About the same as PyroWave |

Each run takes five HUD readings about six seconds apart. PyroWave combines two settled runs (10 readings), HEVC 400 combines three runs (15 readings), and the other primary rows use five readings each. These are means of rolling HUD percentiles, not percentiles calculated from a single raw frame distribution. The measured endpoint is host capture to decoded output availability, not input-to-photon response or physical screen scanout. Small differences around one millisecond should not be treated as a guaranteed perceptible advantage.

HEVC 400 averaged about 137 FPS, PyroWave about 137 FPS, and AV1 400 about 138 FPS in the primary samples. Peak throughput was similar; FPS is not the deciding advantage here. HEVC 400 had the lowest measured delay but gave up detail in the final full-screen assessment. Raising its target to 800 brought its delay close to PyroWave’s. AV1 800 averaged about 28 ms of displayed p50 latency versus about 17 ms for PyroWave, while maintaining a similar output FPS; pipelined throughput is different from per-frame delay.

## Visual checks

The user panned across foliage and rocks for each codec. Initial answers described both high-bitrate codecs as about the same as the usual PyroWave picture. Initial lower-rate checks also seemed comparable, but a portrait capture revealed that downscaling could conceal detail differences. The final full-screen landscape answers were:

- AV1 at 400 Mb/s: “AV1 looks softer”.
- HEVC at 400 Mb/s, immediately after seeing PyroWave again: “HEVC looks softer”.

Those final answers supersede the earlier apparent parity at 400 Mb/s. Higher-rate HEVC and AV1 comparisons were captured in landscape. Screenshots and a native-pixel foliage/rock crop comparison are retained as supporting material, not as a substitute for the user’s motion judgment on the HDR tablet.

No source-reference lossless frame was captured on the Windows host. The game stayed live at the user’s request, so lighting, foliage, character animation and camera framing could change between sessions. This was not a blinded test, and no PSNR, SSIM, VMAF or universal quality score is claimed. Android screenshots also do not preserve the full physical HDR-panel experience. The result is a practical observation for this scene, not proof that one codec wins in every game or at every encoder setting.

## Repeats and exclusions

The first AV1 800 attempt remained in the library and produced no valid stream readings; those empty rows are excluded. A later live AV1 800 session was verified and supplied five valid readings. The AV1 400 repeat initially encountered portrait navigation and a UI-sampling interruption. Its completed repeat measured about 19.4 ms p50, but the retained capture was portrait, so that run is kept separately rather than pooled into the primary landscape latency row. Its final landscape motion assessment remains recorded.

The first PyroWave reconnect set included a startup FPS reading of 121. That whole five-reading set is preserved as `pyrowave-repeat`; the headline uses the initial stable run and a subsequent settled run, rather than presenting startup as a sustained throughput result. Other runs and all original readings remain in the JSON.

## Final state and reproduction

No code, driver or APK changed during this comparison. Original app settings were backed up before testing and restored afterward: PyroWave codec, original quality value 1.8, automatic PyroWave rate selection, native resolution, 144 Hz, HDR and the original presentation preference. Turnip remains selected for PyroWave; it does not replace the Qualcomm hardware video decoder used by HEVC and AV1. Temporary profiling properties remain clear and automatic rotation remains enabled. DroidDeck was untouched.

The evidence archive contains valid and failed sampling traces, decoder logs, screenshots and comparison helpers. App-private settings backups, signing keys and pairing identities are omitted. The existing driver/client release is unchanged; this is an additional comparison report.
