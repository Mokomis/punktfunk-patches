# Turnip subgroup-64: fragment versus compute

Compute was faster on this tablet and scene. At matching bitrate, compute averaged 5.87 ms decode time versus fragment 6.64 ms; fragment took 13.1% longer. Both paths looked correct in screenshots, and the user confirmed the fragment picture “Looks correct”.

Same installed punktfunk-turnip-sg64.apk and Mesa 745709a000, Adreno 829. The dequant subgroup-64 workaround remained active throughout. No code or APK changes were needed. Only debug.punktfunk.pyro_idwt changed between sessions.

No Man’s Sky loaded save on the Windows host; user confirmed it was running and asked to keep the camera stationary. 2414×1680@144, 10-bit 4:2:0 HDR. Order: default compute → forced fragment → forced compute → forced fragment.

The automatic bitrate changed after packet loss. Primary comparison includes only samples with target 1125 Mb/s, selected by that rule regardless of measured performance. Initial ramp-up was saved separately in idwt-compute-first.json but excluded from the comparison. Each measured stage took five overlay samples roughly six seconds apart after settling; the repeat stages each have two qualifying samples. This is a short live comparison, with network and scene variation, not an offline identical-frame performance benchmark.

| Run | Included / total | Mean decode ms | Mean FPS |
|---|---:|---:|---:|
| compute-first | 5/5 | 5.88 | 137.6 |
| fragment-first | 5/5 | 6.64 | 135.4 |
| compute-repeat | 2/5 | 5.85 | 136.5 |
| fragment-repeat | 2/5 | 6.65 | 136.5 |

| Combined | Samples | Mean decode ms | Mean FPS |
|---|---:|---:|---:|
| compute | 7 | 5.87 | 137.3 |
| fragment | 7 | 6.64 | 135.7 |

The two matched-bitrate runs agree: compute 5.88/5.85 ms, fragment 6.64/6.65 ms. FPS differences were small. The first fragment run included a 7.5 ms decode sample and 58.7 ms p95 spike; it was retained because its bitrate matched. Lower-bitrate samples from both repeat runs were excluded; their raw data is included in the archive.

Final action: clear the IDWT override and reconnect. Turnip’s driver default is compute. Turnip remains selected, with the subgroup-64 fix. DroidDeck’s restored WinNative settings were not touched.

Screenshot: idwt-fragment-sg64.png. Full samples and this report are in turnip-idwt-comparison-output.zip.
