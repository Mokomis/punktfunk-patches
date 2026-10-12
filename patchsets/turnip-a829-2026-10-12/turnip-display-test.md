# Display rendering test — 2026-10-12

The tested simplification did not improve performance, so it was rejected. The working Turnip build with the reconstruction optimization and dequant subgroup-64 fix was restored.

The Android renderer already samples the decoded Y/Cb/Cr planes, converts colour and displays the image in one draw. The experiment moved chroma siting from texture-size queries to a per-frame CPU push constant, and specialized away tone mapping for native HDR output. Filtering, colour coefficients, arithmetic precision, crop and HDR surface format were preserved. The test used a diagnostic property, not a new player-facing setting.

| Same test APK, successive runs | Mean display GPU interval |
|---|---:|
| Original shader, first control | 1.418 ms |
| Frame-specialized shader | 1.490 ms |
| Original shader, repeated control | 1.437 ms |

The candidate was nominally 3.7–5.1% slower than the controls. Live scene and GPU conditions vary, so this does not establish a precise regression, but there is no evidence supporting adoption. Values are means of 6/7/6 retained 600-frame reporting windows, respectively, after excluding the first two retained windows per process. The log buffer can roll over; raw logs and the exact retained values are provided in the archive. These timestamp intervals cover the render pass and transitions, and can include GPU synchronization; they are not an isolated fragment-instruction benchmark.

Build and native compatibility check passed; SPIR-V validation passed. With native HDR specialization frozen, the shader had zero texture-size queries, zero conditional branches and the same three texture samples. The live candidate screenshot appeared clean. No offscreen pixel-by-pixel output comparison was performed for this rejected candidate.

The original working APK is `punktfunk-turnip-reconstruction.apk`. Experiment source and SPIR-V, a narrow source patch, build log, raw timing logs and selected-window JSON are in `turnip-display-experiment.zip`. To recreate the experimental shader, compile `planar_csc_android.frag` with glslangValidator targeting Vulkan 1.1, then run `spirv-opt -O --strip-debug` and `spirv-val`. Apply the source patch and place the included SPIR-V beside the source. Diagnostic property `debug.punktfunk.pyro_csc_fast=1` selects it after restarting the experimental app.

Timestamp scope follows the [Vulkan timestamp-query rules](https://docs.vulkan.org/refpages/latest/refpages/source/vkCmdWriteTimestamp.html); these values include more than the shader alone.

All experiment-only source changes were removed from the active checkout. The earlier reconstruction optimization remains. Test properties are cleared. DroidDeck was not changed.
