# Turnip Adreno 829 subgroup-64 workaround: live test

The live No Man’s Sky stream is now visually correct with Turnip. The user confirmed that movement looks correct, and both captured screenshots show intact terrain, character detail and UI text.

The two Turnip runs averaged 6.00 ms decode time versus 6.78 ms across two Qualcomm runs: 11.5% less decode time. Average FPS was similar. These are short live measurements, not a repeatable offline performance benchmark.

## Change

The dequant pass requests exactly 64 lanes when driver_id is MESA_TURNIP, deviceID is 0x44030a20 (the tested Adreno 829), and 64-lane subgroups are supported. Other drivers/devices retain their existing subgroup selection. The arithmetic, precision, texture aliases and presentation path were left at their normal settings for this comparison.

This build includes the previously tested AdrenoTools integration and its unused diagnostic switches. All previous override properties were cleared. Turnip uses its normal compute inverse-wavelet path; Qualcomm uses its normal fragment path. The separate replay test already showed subgroup 64 removes the large decoding error on menu and gameplay captures.

## Validation

- Local Android build succeeded, including the native import check.
- Same APK used for Qualcomm → Turnip → Qualcomm → Turnip.
- Loaded No Man’s Sky save, 2414×1680 at requested 144 Hz, PyroWave 10-bit 4:2:0 HDR.
- Each run settled before five overlay samples, spaced about six seconds apart; ten samples per driver total.
- Turnip library and AdrenoTools verified in the running process mappings. The app also refuses a Turnip selection unless the queried Vulkan driver is MESA_TURNIP.
- User confirmed: “Looks correct”. Screenshots sg64-turnip-live.png and sg64-turnip-final.png saved.
- Workaround patch passed a reverse-apply check against the built source.

| Run | Mean decode ms | Mean FPS | Mean end-to-end p50 ms |
|---|---:|---:|---:|
| Qualcomm first | 6.70 | 136.8 | 19.20 |
| Turnip first | 5.96 | 137.4 | 18.14 |
| Qualcomm repeat | 6.86 | 133.2 | 19.52 |
| Turnip repeat | 6.04 | 135.2 | 18.40 |

| Combined | Mean decode ms | Mean FPS | Mean end-to-end p50 ms |
|---|---:|---:|---:|
| Qualcomm | 6.78 | 135.0 | 19.36 |
| Turnip | 6.00 | 136.3 | 18.27 |

Camera movement, daylight and Wi-Fi varied during live sampling. The second Turnip run included one Wi-Fi drop to a reported 34 Mb/s, with 32 lost frames and a 66.5 ms p95 spike; subsequent samples recovered. These results support a modest decode-time gain, not a large or guaranteed overall FPS gain.

## Installed state and artifacts

The patched client remains installed and streaming with Turnip selected through debug.punktfunk.vulkan_driver=turnip. Capture and earlier diagnostic overrides are cleared. Pairing and preferences were retained.

APK: punktfunk-turnip-sg64.apk
SHA-256: acbb38daa5209e1222be650206c20472ba0e81b45983c537e093a5ad9c90e101

Narrow workaround: turnip-adreno829-sg64-workaround.patch
Full current client source diff: punktfunk-turnip-sg64-client-changes.patch (bundled native libraries are in the APK; untracked binaries are not represented by a source diff).

Return this APK to Qualcomm by clearing debug.punktfunk.vulkan_driver and restarting the app. The original APK is also retained as punktfunk-0.44.0-dev-mokomis.1.apk. No repository push or GitHub build was performed for this step.
