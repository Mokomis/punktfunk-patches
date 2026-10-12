# PyroWave driver comparison (diagnostic)

Not part of the client build. These patches compare PyroWave decoding on the Qualcomm
driver and on Turnip, using byte-identical input, before any colour conversion or
presentation.

| Patch | What it adds |
|---|---|
| `0001-pyrowave-plane-replay.patch` | `pyrowave_planes` (decode a capture, write raw Y/Cb/Cr planes and a manifest), `pyrowave_compare_planes.py`, the Android capture switch, and an opt-in readback usage on decoder planes |
| `0002-pyrowave-dequant-subgroup-pin.patch` | `PYROWAVE_DEQUANT_SUBGROUP_LOG2` pins the dequant shader's subgroup size |

Apply on a checkout of upstream `55cc38de8a20271fd86fbf95d59dbc3beffea207`:

```sh
git am ../client/*.patch
git am 0001-pyrowave-plane-replay.patch 0002-pyrowave-dequant-subgroup-pin.patch
```

## What is known so far

Checked on Linux with Mesa's software Vulkan driver (lavapipe 25.2.8). Nothing here has run on the tablet yet.

1. **The replay tool reads planes back correctly.** On upstream's golden fixtures (`clients/apple/Tests/PunktfunkKitTests/PyroWaveFixtures`, 256×144, 8-bit 4:2:0), the planes come back with the right size and geometry.

2. **Lavapipe decodes those fixtures wrongly**, in a way that looks like the Turnip corruption: wrong colours, smeared detail, visible 32×32 block structure.

   | Lavapipe subgroup size | PSNR against the reference (Y / Cb / Cr) |
   |---|---|
   | 8 (default) | 12.3 / 13.1 / 15.7 dB |
   | 16 (`LP_NATIVE_VECTOR_WIDTH=512`) | 25.9 / 31.0 / 29.5 dB |

   Upstream's own test treats more than 45 dB as matching.

3. **The dequant shader depends on subgroup size.** `shaders/wavelet_dequant.comp` computes per-block byte offsets with a `subgroupInclusiveAdd` over threads 0–15, inside `if (local_index < 16)`. That is correct only when those 16 threads share one subgroup.
   - The decoder asks for subgroup sizes 16–128 when the driver offers them. Failing that, it falls back to 4–128, which this scan cannot handle; that explains lavapipe at size 8.
   - At size 16 the scan is correct, yet lavapipe still corrupts. So either lavapipe has a second problem, or another part of the shader depends on how the driver runs subgroup operations in divergent code.
   - Lavapipe is therefore not a usable reference.

4. **What this means for Turnip:**
   - Adreno drivers offer subgroup sizes 64 and 128, so the decoder lets the driver vary the size ("varying subgroup size", full subgroups). The shader is correct at both sizes on paper.
   - The open question is whether Turnip's new A8xx code runs this shader's subgroup scans correctly, at whichever size it picks.
   - Also open: the two finest wavelet levels are stored as R16_SFLOAT at the client's default precision 1. Your shaderFloat16 test (case 4) changed only the arithmetic, not that storage. `PYROWAVE_PRECISION=2` stores everything as R32_SFLOAT.

5. **Expect small differences even between correct drivers.** The wavelet maths uses floats and is not bit-exact across GPUs. Read the comparison's PSNR, not the checksums:
   - above 45 dB: both drivers decode the frame the same;
   - below 30 dB: real corruption.

## Running the comparison on the tablet

### 1. Capture from a live session

Use the test APK built with these patches. Use the Qualcomm driver here: the capture records the decoder's input, so the driver does not matter, and Qualcomm gives a clean picture to check against.

```sh
adb shell setprop debug.punktfunk.dump_video /data/data/io.unom.punktfunk.mokomis/cache/pfdump
adb shell setprop debug.punktfunk.dump_video_frames 120
```

Connect and stream No Man's Sky with the usual settings (2414×1680, 10-bit 4:2:0 HDR), wait a few seconds, then disconnect. Clear the switch, then copy the capture out (needs root):

```sh
adb shell setprop debug.punktfunk.dump_video ""
adb shell su -c 'cp -r /data/data/io.unom.punktfunk.mokomis/cache/pfdump /data/local/tmp/ && chmod -R a+r /data/local/tmp/pfdump'
adb shell cat /data/local/tmp/pfdump/mode.txt     # e.g. "2414x1680 10 420 transfer 16 shard_payload 1408"
```

The capture is `au-<time>.pyrowave` plus `.pyrowave.idx`. At about 1 Gb/s, 120 frames is roughly 120 MB.

### 2. Build the replay tool for the tablet

From the patched upstream checkout, with the NDK and `cargo-ndk` already set up for the client build:

```sh
cargo ndk -t arm64-v8a build --release -p pf-client-video \
  --no-default-features --features pyrowave --example pyrowave_planes
adb push target/aarch64-linux-android/release/examples/pyrowave_planes /data/local/tmp/
adb push <your Turnip build>/libvulkan_freedreno.so /data/local/tmp/
adb shell chmod 755 /data/local/tmp/pyrowave_planes
```

### 3. Decode the same frames on each driver

Use the size from `mode.txt`. `CAP` is the capture's data file.

```sh
adb shell
cd /data/local/tmp
CAP=pfdump/au-<time>.pyrowave
./pyrowave_planes $CAP 2414x1680 10 out-qcom 16
./pyrowave_planes $CAP 2414x1680 10 out-qcom-2 16          # second run: is Qualcomm repeatable?
PYROWAVE_ICD=/data/local/tmp/libvulkan_freedreno.so ./pyrowave_planes $CAP 2414x1680 10 out-tu 16
```

If the Turnip run cannot open the GPU from the shell, run it under `su -c`.

The manifest's first lines confirm which driver ran: `driver Qualcomm ...` or `driver turnip Mesa driver | Mesa 26.3.0-devel ...`.

Then the Turnip variants. Each one changes a single thing:

```sh
T="PYROWAVE_ICD=/data/local/tmp/libvulkan_freedreno.so"
env $T PYROWAVE_DEQUANT_SUBGROUP_LOG2=6 ./pyrowave_planes $CAP 2414x1680 10 out-tu-sg64 16
env $T PYROWAVE_DEQUANT_SUBGROUP_LOG2=7 ./pyrowave_planes $CAP 2414x1680 10 out-tu-sg128 16
env $T PYROWAVE_PRECISION=2            ./pyrowave_planes $CAP 2414x1680 10 out-tu-fp32 16
env $T PYROWAVE_PLANES_IDWT=compute    ./pyrowave_planes $CAP 2414x1680 10 out-tu-compute 16
env $T PYROWAVE_PLANES_IDWT=fragment   ./pyrowave_planes $CAP 2414x1680 10 out-tu-fragment 16
```

Run the same subgroup and precision variants on Qualcomm too, so a variant that changes Qualcomm's output can be told apart.

### 4. Compare on a computer

```sh
adb pull /data/local/tmp/out-qcom . ; adb pull /data/local/tmp/out-tu . ; (and the variants)
python3 crates/client/pf-client-video/examples/pyrowave_compare_planes.py out-qcom out-qcom-2
python3 crates/client/pf-client-video/examples/pyrowave_compare_planes.py out-qcom out-tu --maps maps-tu
python3 crates/client/pf-client-video/examples/pyrowave_compare_planes.py out-qcom out-tu-sg64
...
```

Each plane line gives PSNR, the share of samples off by more than 1 and more than 16 codes, how many 32×32 tiles differ, and how much of the error sits in the partial tiles at the frame's right and bottom edges (2414 is not a multiple of 32). `--maps` writes a difference image per plane.

### Reading the result

| Result | Points to |
|---|---|
| Turnip matches Qualcomm (>45 dB) in replay, but the live picture is corrupt | Something outside decoding: the plane images as the presenter samples them, the presenter's colour conversion, or the AdrenoTools integration. Check those next |
| Turnip differs, and a subgroup pin (`sg64` or `sg128`) brings it above 45 dB | Turnip's handling of varying subgroup size in the dequant shader. Report to Mesa with this capture |
| Turnip differs, and only `fp32` fixes it | R16_SFLOAT storage of the two finest wavelet levels on A8xx |
| Turnip differs in every variant, errors spread over all tiles | Dequant or payload reads in general. Next: the texel-buffer payload path (Qualcomm-vendor devices read the payload through R8/R16/R32 texel buffers, two of them `mediump`) |
| Errors only in the edge tiles | Edge handling at a width that is not a multiple of 32 |
| Only the Cb/Cr planes differ | The 4:2:0 chroma path |

Restore afterwards: `adb shell setprop debug.punktfunk.dump_video ""`. The system driver is never touched: Turnip is loaded only into the replay tool's process.
