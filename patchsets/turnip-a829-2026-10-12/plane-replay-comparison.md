# Qualcomm versus Turnip: PyroWave plane replay

On both the No Man’s Sky menu and the loaded save, forcing dequant subgroup size 64 makes Turnip match Qualcomm by the diagnostic README’s >45 dB criterion. Default Turnip, subgroup 128, precision 2, compute and fragment remain corrupt. No decoder fix was made after these measurements.

## Setup

- Tablet: OPD2515, Adreno 829, ADB over Wi-Fi with root available.
- Stream: 2414×1680, 10-bit 4:2:0, HDR transfer 16; shard payload 1408.
- Upstream: 55cc38de8a20271fd86fbf95d59dbc3beffea207 plus client main-55cc38de-mokomis.1 and both diagnostic patches from branch commit 0e46dbca2a03229b807e83afb72b05649f213e60.
- Qualcomm: Vulkan 1.4.295, driver build 718a07726a / Ic95db9d944 dated 2026-05-29, compiler E031.50.19.29.
- Turnip: Mesa 26.3.0-devel (git-745709a000), MESA_TURNIP, Vulkan 1.4.363. The manifest confirms this identity for every Turnip run.
- Captured 120 access units per scene; replayed the first 16 complete units (48 planes). Five incomplete units skipped identically across drivers. Comparator reported no mismatched access-unit indices.
- Gameplay capture: au-1791774612.pyrowave; SHA-256 eb1d58fa9764df46f91d035c0e89c09579ae8a0a8fc11e29cb3f62560dff3c3a.
- Gameplay runs were performed with the live client stopped to avoid GPU competition. Menu replay ran while the Qualcomm stream was active.

## Required build and loader corrections

The supplied Android capture patch called au_dump while that module and its punktfunk-core dependency were desktop-only. Both gates were extended to Android. The previously authorized set_gpu_stats compile fix was retained. See plane-replay-build-fixes.patch. No shader, dequant algorithm, precision default or presentation code was changed.

The Android Turnip library exports the Android HAL HMI, not vkGetInstanceProcAddr or vk_icdGetInstanceProcAddr. Direct loading in the supplied replay tool therefore failed. A small external adapter exports vkGetInstanceProcAddr and forwards through the already-built AdrenoTools loader, leaving the replay tool and decoder unchanged. PYROWAVE_ICD pointed to /data/local/tmp/libturnip_replay_loader.so; the adapter selects /data/local/tmp/libvulkan_freedreno.so. Its source is included in the results archive. Qualcomm uses the system loader.

The standalone build additionally needed the same NDK, Ninja and libclang environment as the Android Gradle build. Both builds passed.

## Results

The table gives the **minimum PSNR across the 16 frames** for each plane, in dB. “Exact” means every plane of that type was byte-identical. Higher is better; the README considers >45 dB matching. Exit 1 from the comparator means some bytes differ, not that replay failed. Every replay process exited 0.

### Gameplay

Qualcomm repeatability: 48/48 planes identical.

| Turnip variant versus Qualcomm default | Y | Cb | Cr | Byte-identical planes |
|---|---:|---:|---:|---|
| Default | 29.04 | 32.50 | 31.98 | 2/48 planes identical |
| Subgroup 64 | 51.84 | 60.66 | 62.40 | 2/48 planes identical |
| Subgroup 128 | 29.04 | 32.50 | 31.98 | 2/48 planes identical |
| Precision 2: R32_SFLOAT throughout | 29.02 | 32.49 | 31.97 | 2/48 planes identical |
| Compute IDWT | 29.04 | 32.50 | 31.98 | 2/48 planes identical |
| Fragment IDWT | 29.06 | 32.51 | 32.00 | 3/48 planes identical |

| Qualcomm variant versus Qualcomm default | Y | Cb | Cr | Byte-identical planes |
|---|---:|---:|---:|---|
| sg64 | Exact | Exact | Exact | 48/48 planes identical |
| sg128 | Exact | Exact | Exact | 48/48 planes identical |
| fp32 | 108.87 | Exact | Exact | 33/48 planes identical |
| compute | 50.91 | 60.16 | 62.11 | 2/48 planes identical |
| fragment | Exact | Exact | Exact | 48/48 planes identical |

Matching Qualcomm and Turnip variants were also compared (sg64, sg128, fp32, compute, fragment). Their complete output is in the archive; only sg64 passes all planes.

### Menu

Qualcomm repeatability: 48/48 planes identical.

| Turnip variant versus Qualcomm default | Y | Cb | Cr | Byte-identical planes |
|---|---:|---:|---:|---|
| Default | 23.52 | 35.31 | 34.87 | 2/48 planes identical |
| Subgroup 64 | 51.80 | 64.49 | 64.23 | 2/48 planes identical |
| Subgroup 128 | 23.52 | 35.31 | 34.87 | 2/48 planes identical |
| Precision 2: R32_SFLOAT throughout | 23.51 | 35.29 | 34.86 | 2/48 planes identical |
| Compute IDWT | 23.52 | 35.31 | 34.87 | 2/48 planes identical |
| Fragment IDWT | 23.53 | 35.33 | 34.89 | 3/48 planes identical |

| Qualcomm variant versus Qualcomm default | Y | Cb | Cr | Byte-identical planes |
|---|---:|---:|---:|---|
| sg64 | Exact | Exact | Exact | 48/48 planes identical |
| sg128 | Exact | Exact | Exact | 48/48 planes identical |
| fp32 | 94.34 | Exact | Exact | 33/48 planes identical |
| compute | 51.01 | 63.85 | 63.31 | 2/48 planes identical |
| fragment | Exact | Exact | Exact | 48/48 planes identical |

Matching Qualcomm and Turnip variants were also compared (sg64, sg128, fp32, compute, fragment). Their complete output is in the archive; only sg64 passes all planes.

## Interpretation and next step

Subgroup 64 fixes the large error on two captures, while pinning Qualcomm to 64 or 128 does not change its output. Pinning Turnip to 128 preserves corruption. This narrows the problem to the dequant shader’s interaction with Turnip subgroup selection/128-lane execution. It does not establish whether the underlying fault is a Mesa compiler/runtime bug or a shader assumption.

Full FP32 does not repair it, so R16_SFLOAT storage alone is not the explanation. Both inverse-wavelet paths remain bad without the subgroup-64 pin. Errors affect Y, Cb and Cr and interior tiles, so the problem occurs before colour conversion/presentation and is not confined to partial edge tiles.

Next: test a narrowly scoped dequant subgroup-64 workaround in the live Turnip client, then compare picture quality and performance against Qualcomm on the loaded save. That change has not been made in this run.

The normal Qualcomm APK was restored, pairing/settings retained, and both capture properties cleared. The system driver was never replaced.

Raw decoded planes and both captures remain in work/replay-results and work/replay-save-results. The gameplay input is also supplied separately as pyrowave-gameplay-capture.zip.
