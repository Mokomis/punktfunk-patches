# OPPO Turnip comparison — October 11, 2026

Turnip compiled and loaded successfully, but corrupted the PyroWave picture. The original client and Qualcomm driver were restored after testing.

## Build and identity

- Mesa main verified before building: `745709a000482a4a24c91faef5c5a40bd653a863`.
- Banner A8xx build recipes: `3d82e747a6ac00d88de921aa2969cdaa08ac78d4`.
- A8xx patches: `a8xx_gen8.patch`, `a8xx_shared_mem.py`, `a840v2.py`.
- Source build: https://github.com/Mokomis/punktfunk-patches/actions/runs/38188035156
- Runtime identity: `MESA_TURNIP`, `turnip Mesa driver`, `Mesa 26.3.0-devel (git-745709a000)`.
- Driver archive SHA-256: `6e06add6c3d09737afd54b9bd7b7ed8351b06ed5a9fe8c30e37036c15ab58546`.

## Streaming test

OPPO OPD2515 / Adreno 829, No Man's Sky on ROBMACHINEX. Same scene, 2414×1680 requested 144 Hz, PyroWave 10-bit 4:2:0, HDR swapchain, fragment inverse-wavelet decoding. Five overlay samples about six seconds apart per run. The host used automatic bitrate; the exact frames and bitrate were not fixed. These are short live observations, not a controlled GPU-only benchmark or a long soak.

| Run | Decode time | Frame rate | Picture |
| --- | --- | --- | --- |
| Original client, Qualcomm baseline | 6.1–6.9 ms | 137–140 FPS | User reported clean |
| Test client, Turnip fragment | 4.9–5.4 ms | 137–140 FPS | Severe color and detail distortion |
| Same test client, Qualcomm control | 6.3–6.5 ms | 134–137 FPS | Clean capture |

The mean of the five displayed decode values was 5.16 ms for Turnip and 6.38 ms for the Qualcomm control, about 19% less time. The corrupted output makes Turnip unsuitable for this configuration despite that timing. Switching only the driver back to Qualcomm removed the distortion, isolating the problem to the Turnip decode path in this test.

The root cause was not established. PyroWave's aliased linear-texture path remains a candidate for a subsequent diagnostic experiment. No alias-disable, sysmem, or compute-mode variant was tested in this run.

## Final tablet state

Installed original `0.44.0-dev-mokomis.1` APK again with `adb install -r`; settings and pairing retained. Cleared both diagnostic driver and IDWT properties. The system driver is again the default. The test APK, driver archive, source patch and screenshots are preserved beside this report.
