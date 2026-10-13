# HEVC P4 versus tuned PyroWave — final comparison

Practical conclusion: HEVC at an 800 Mb/s target with requested host P4 matches the visible static detail of the tuned PyroWave setup in this No Man’s Sky scene. Inspection of foliage, flowers, ship surfaces and the clean final character capture does not show a convincing PyroWave quality advantage. This is visual judgment, not pixel identity or a source-reference fidelity score. No new controlled camera-pan comparison was completed.

Both inspected codec outputs are 2520×1680@144 in landscape, 10-bit HDR. The background view is retained without camera input by the agent. Image registration verifies closely matched scale, eliminating the approximately 4% horizontal scaling mismatch from the earlier safe-area comparison. Character idle animation, foliage, clouds and time of day continue changing; the final focused HEVC captures are darker than PyroWave. No PSNR, SSIM or VMAF ranking is claimed.

| Two screenshot HUD readings | PyroWave | HEVC 800 / requested P4 |
|---|---:|---:|
| Mean displayed p50 capture-to-decoded latency | 17.5 ms | 16.75 ms |
| Mean displayed p95 | 22.85 ms | 21.5 ms |
| Mean displayed FPS | 134 | 137.5 |
| Mean actual wire traffic | 1041.55 Mb/s | 305.3 Mb/s |

These are two rolling-HUD samples per codec, not a sustained statistical benchmark or physical input-to-photon measurement. The roughly 0.75 ms p50 difference supports similar latency; it does not prove a perceptible HEVC advantage. Scene lighting and sample times differ. Bandwidth was not used as the quality scoring criterion.

## Focus-related exclusions and correction

Initial HEVC reconnects fell to 30 FPS and showed severe artifacts around the character. The user clicked the game on Windows; throughput returned to about 136–138 FPS and the visible character artifacts disappeared. This points to a background-rendering condition, not proof of HEVC compression failure. Unfocused images are retained in the evidence archive but excluded from the final latency/throughput headline and normal-quality judgment. The mechanism was not diagnosed further.

The preceding quick comparison incorrectly called the PyroWave switch unverified because Android accessibility returned empty text. A saved screenshot clearly shows PyroWave 2520×1680 and its latency HUD. Verification now includes direct screenshot inspection. That older pair had different camera views and is not pooled into this result.

## Final state

The released client APK and custom Turnip driver are unchanged. HEVC target 800 and requested Windows NVENC P4 remain active, with full-panel 2520×1680 retained for matching display dimensions. The earlier native safe-area setting is not restored at the end of this phase. No orientation lock, driver change or thermal override was applied. Original preference backups remain private. The desktop preset launcher retains a restore option for host settings. P5–P7 were not tested.

## Selected default

The user selected HEVC target 800, host NVENC P4, full-panel 2520×1680@144, 10-bit HDR and arrival/immediate presentation as the current personal default. P5–P7 remain untested. No new APK or driver build changes compiled defaults. See CURRENT-STREAMING-DEFAULT.md for settings and restoration.
