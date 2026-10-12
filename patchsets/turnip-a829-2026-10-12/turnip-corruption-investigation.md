# Turnip corruption investigation — October 11, 2026

The live-stream corruption remains unresolved. A diagnostic client tested the suspected aliasing path and several other driver/decoder controls. None produced a clean picture. The original client and Qualcomm driver were restored afterward.

## Conditions

OPPO OPD2515 / Adreno 829; Mesa Turnip 26.3.0-devel `745709a000`; No Man's Sky on ROBMACHINEX; 2414×1680 at a requested 144 Hz; PyroWave 10-bit 4:2:0. The game continued running while the tablet client restarted between cases. These were visual live-stream tests, not identical compressed-frame comparisons. Automatic bitrate and the game lighting varied.

The diagnostic APK loads Turnip through AdrenoTools and rejects its capability probe if the runtime driver identity is not MESA_TURNIP. Unit tests, native import checks and APK assembly passed. The original working APK was retained throughout.

## Results

| Case | Configuration | Result |
| --- | --- | --- |
| Prior baseline | Turnip, fragment, normal aliases, FP16 | Corruption |
| 1 | Turnip, fragment, aliases disabled | Corruption; four valid overlay samples showed 6.4–6.9 ms decode |
| 2 | Turnip, compute, aliases disabled | Corruption; observed about 5.8–6.1 ms decode |
| 3 | Case 2 plus system-memory rendering (`sysmem`) | Corruption |
| 4 | Case 2 plus FP16 disabled | Corruption; runtime logged `float16: false` |
| 5 | Case 4 plus image compression disabled (`noubwc`) | Corruption |
| 6 | Case 4 with SDR output surface, preserving 10-bit input/decode | Corruption; runtime logged `R8G8B8A8_UNORM SRGB_NONLINEAR` |

The fifth sample of case 1 was collected during an app restart and was empty; it is excluded from the timing range. Later cases were inspected using screenshots and individual overlay readings rather than five-sample benchmarks. Corrupted output makes all timing values unsuitable for choosing a production configuration.

## What the tests establish

Disabling the linear-image alias optimization alone does not cure this failure. It affects both compute and fragment reconstruction. Neither the system-memory rendering control, disabling half-precision shader support, disabling driver image compression, nor changing the final output to an SDR surface corrected the picture in the tested configurations.

These results weaken the corresponding hypotheses; they do not prove each mechanism is irrelevant or identify the faulty instruction. In particular, the SDR-surface test keeps the source and decoder at 10 bits: it tests the final output surface, not an 8-bit source stream. The overlay still labels the incoming stream HDR in that case.

The next discriminating experiment is to capture one complete 10-bit compressed frame and compare raw decoded Y/Cb/Cr planes from both drivers before color conversion and presentation. That would distinguish decoder/dequantization/image-access corruption from a later color-conversion or sampling issue. A root cause has not yet been established.

## Reproducible diagnostic controls

- `debug.punktfunk.vulkan_driver=turnip`: select bundled Turnip after process restart.
- `debug.punktfunk.pyro_idwt=fragment|compute`: choose the reconstruction path for a new decoder.
- `debug.punktfunk.pyro_no_linear=1`: return before creating aliased linear textures; retain existing buffer fallback.
- `debug.punktfunk.pyro_fp32=1`: withhold optional shaderFloat16 when creating the Vulkan device and handing its enabled features to PyroWave.
- `debug.punktfunk.pyro_sdr_surface=1`: use an SDR surface without changing input/decode depth.
- `debug.mesa.tu.debug=sysmem|noubwc`: Mesa's Android property equivalent of TU_DEBUG, read at driver initialization.

The property translation is verified in the [pinned Mesa source](https://gitlab.freedesktop.org/mesa/mesa/-/blob/745709a000482a4a24c91faef5c5a40bd653a863/src/util/os_misc.c); the flags are defined in [tu_util.cc](https://gitlab.freedesktop.org/mesa/mesa/-/blob/745709a000482a4a24c91faef5c5a40bd653a863/src/freedreno/vulkan/tu_util.cc).

## Preserved artifacts

The diagnostic APK and `turnip-corruption-diagnostics.patch` are saved beside this report, along with screenshots for fragment/no-alias, compute/no-alias, sysmem, FP32, noubwc and SDR-surface cases. They are diagnostic artifacts, not a recommended replacement for the working client.

Final state: reinstalled `0.44.0-dev-mokomis.1` in place; cleared every diagnostic property above. Settings and pairing remain preserved. The original Mesa debug property was empty and was restored to empty.

Restoration verification: the original client reconnected and displayed a clean game picture. A subsequent overlay reading showed 136 FPS, 6.4 ms decode and 17.9 ms median capture-to-decoded latency. A screenshot captured moments earlier showed 126 FPS and 6.7 ms during a game notification; performance varies with content. `qualcomm-restored-after-diagnostics.png` preserves the clean control capture.
