# Turnip reconstruction experiment — 2026-10-12

Implemented and installed a small compute inverse-wavelet reconstruction optimization for Punktfunk on Turnip / Adreno 829. It packs pairs of half-precision shared-memory values into 32-bit words and processes the tile edge in groups of eight rather than four. Other GPUs, drivers and precision modes retain the existing shader. The earlier dequantization subgroup-64 corruption workaround remains active.

## Controlled replay results

All timing variants decoded the same saved No Man’s Sky capture: 2414×1680, 10-bit 4:2:0, 115 complete frames from 120 access units. Each variant ran three times. Replay includes GPU readback, so absolute replay times should not be compared to live-stream times.

| Reconstruction variant | Mean GPU time |
|---|---:|
| Recompiled original shader | 4.901 ms |
| Packed shared memory + wider edge processing | 4.808 ms |
| Wider edge processing alone | 4.862 ms |
| Packed shared memory alone | 4.919 ms |
| Workgroup-to-subgroup barriers | 4.924 ms |
| Two tiles per workgroup | 4.893 ms |

Selected candidate reduces reconstruction time by **1.89%**, about **0.093 ms** in this benchmark. Other experiments, including forcing reconstruction subgroup 64 and reducing arithmetic precision, did not justify shipping a separate change. Lower arithmetic precision also introduced larger pixel differences.

## Correctness

- Full capture: 280/345 planes byte-identical; maximum difference one 10-bit code; minimum finite plane PSNR 106.93 dB. Five incomplete access units were skipped consistently.
- Three 8-bit golden fixtures (dense 4:2:0, chunked 4:2:0, dense 4:4:4): all nine planes byte-identical to the original shader. Both shaders passed the reference quality threshold.
- Shader validation passed. The generated shader installed in the APK matches the tested candidate byte-for-byte: SHA256 `cf55ad41150269932635cc9fb852796b59b23fb2f4395ed025342672ade5e204`.
- Android build and native import compatibility check passed.
- Repository writing check failed on pre-existing patch commit titles and an unchanged 24-line documentation block in `video_pyrowave.rs`; no unrelated history or documentation was rewritten.

## Live-stream limits

Live tests used the same running save at target 1125 Mb/s. The scene’s day/night cycle and GPU conditions changed during the experiment. Initial control averaged 137.8 FPS / 5.48 ms total decode; the first optimized sample averaged 135.0 FPS / 6.00 ms, and the repeated control averaged 135.8 FPS / 5.76 ms. These are noisy observations, not evidence of a frame-rate improvement or a reliable shader regression. GPU stage times also shifted between runs. Only the byte-identical-input replay supports the reported 1.9% gain.

The first optimized overlay recording contains a blank sample and a control-session startup sample after restart; the summary uses only its first three valid optimized samples. Raw evidence retains those rows for transparency. A second optimized run after reconnection received long video-packet gaps and then zero video ingress. Its overlay stayed at 0 FPS, so it is excluded from performance conclusions. The driver and optimized shader did initialize successfully. A fresh connection after clearing profiling flags confirmed the optimized shader again, but still showed 2–6 second receive gaps and only 21–71 Mb/s video ingress instead of the earlier approximately 1 Gb/s. Host/path video delivery remains a live-test limitation. All diagnostic overrides are cleared, with Turnip selected.

The final build is installed on the tablet. Startup logging identifies `reconstruction=a829-packed-apron8`. Driver remains Turnip, reconstruction remains compute, and the dequant subgroup-64 workaround is retained. DroidDeck is untouched.

## Deliverables and reproduction

- `punktfunk-turnip-reconstruction.apk`: installed Android build.
- `turnip-reconstruction.patch`: only this reconstruction change, layered over the existing working client changes; reverse-apply check passes against the local working tree.
- `turnip-reconstruction-results.json`: timings and valid overlay samples.
- `turnip-reconstruction-evidence.zip`: raw timing/comparison logs and build/check logs.

The patch includes the generated shader plus `shaders/build_idwt_a829.py`, which rebuilds it with glslangValidator and SPIR-V Tools. The original shader source retains its default behavior unless the candidate macros are explicitly set.

For a diagnostic control run, set Android property `debug.punktfunk.pyro_recon_baseline=1` and restart Punktfunk. Clear it and restart to restore the optimized shader. This is a diagnostic switch, not a player-facing setting.

## Follow-up after restarting the game

Reconnected successfully after the user restarted the game. The optimized shader startup marker was confirmed. Following the initial connection warm-up, consecutive 10-second receive windows showed approximately 1.080 Gb/s of video with maximum receive gaps of 16 ms and 13 ms, and zero reported dropped frames. The live screenshot showed the expected No Man’s Sky scene with no visible reconstruction corruption. The statistics overlay was hidden, so this follow-up does not establish an FPS or total decode-time improvement. Profiling flags remain cleared and the optimized stream was left connected.
