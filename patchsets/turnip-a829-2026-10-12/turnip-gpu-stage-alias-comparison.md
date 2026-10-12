# Turnip GPU stages and texture-alias comparison

Disabling texture aliases did not show a useful performance improvement. The normal path was restored, and profiling was disabled after testing. Wavelet reconstruction is the largest measured GPU stage. No code or APK changes were made.

## Setup

Existing subgroup-64 client, Mesa Turnip 745709a000, Adreno 829, default compute iDWT. No Man’s Sky loaded save at 2414×1680@144, PyroWave 10-bit 4:2:0 HDR. Order: aliases allowed → aliases disabled → aliases allowed again. debug.punktfunk.pyro_stats=1 enabled existing decoder GPU reports; the presenter already reports its GPU draw timing.

Aliases allowed means the decoder may promote payload texel buffers to linear sampled-image aliases if the format and allocation checks pass. debug.punktfunk.pyro_no_linear=1 skips that promotion, preserving the existing buffer fallback. The app logs collected here do not establish whether promotion actually succeeded in the baseline, so this is a comparison of those settings, not proof that different resource types were used in every run.

## GPU timing

Means are calculated from the latest app process in each captured log. Each reported timing window summarizes hundreds of frames; windows were not aligned to an identical input capture or identical bitrate. Display draw includes colour conversion/rendering, not the screen’s scanout latency. These stage times do not equal the overlay’s total decode or end-to-end time.

| Setting | Dequant ms | Reconstruction ms | Display draw ms |
|---|---:|---:|---:|
| Normal first | 1.199 | 2.347 | 1.308 |
| Aliases disabled | 1.242 | 2.340 | 1.317 |
| Normal repeat | 1.190 | 2.329 | 1.304 |

Stage timing is essentially unchanged. Dequant is slightly slower in the aliases-disabled sample, not faster. Reconstruction remains about 2.34 ms per frame and display drawing about 1.31 ms.

## Live overlay timing

The stream lowered its bitrate after packet loss and later measured its link ceiling. For overlay comparison, only samples at target 1125 Mb/s are included; all samples are preserved in the archive. Camera framing and daylight changed during the run, so small differences cannot be assigned confidently to the alias setting.

| Setting | Included / 5 | Mean decode ms | Mean FPS |
|---|---:|---:|---:|
| Normal first | 2/5 | 6.05 | 136.0 |
| Aliases disabled | 5/5 | 5.96 | 137.8 |
| Normal repeat | 5/5 | 5.60 | 136.6 |

The live timing varies more between the two normal runs than the setting change, supporting no useful gain from disabling aliases. Screenshots show a clean picture in both settings; no independent user visual confirmation was requested for this run.

## Final state and next work

Turnip remains selected with the subgroup-64 workaround. The IDWT override is clear, so the driver default is compute. The no-linear override and profiling property are clear, and the app was restarted to apply that state. DroidDeck’s WinNative configuration was not changed.

Further decoder optimisation should start with the compute inverse-wavelet kernels because they are the largest measured GPU stage. This test does not establish a specific shader optimisation or a guaranteed performance gain. A repeatable capture benchmark would be needed before accepting code changes.

Raw GPU reports and overlay samples: turnip-gpu-stage-alias-output.zip.
