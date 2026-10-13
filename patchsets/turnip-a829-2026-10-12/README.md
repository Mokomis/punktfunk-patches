# Adreno 829 Turnip streaming experiments

Personal Android client for the OPD2515 tablet. The source is based on Punktfunk upstream `55cc38de8a20271fd86fbf95d59dbc3beffea207`, plus the eleven client patches in `../main-55cc38de-mokomis.1/client/`. Mesa and recipes are pinned in `turnip-build-source.txt` and `turnip-driver-workflow.yml`.

The final APK bundles Turnip and AdrenoTools. The app chooses the bundled driver when `debug.punktfunk.vulkan_driver=turnip`; this is app-local, not a replacement system driver. Qualcomm remains available by clearing that property and restarting the app. DroidDeck was restored to its own WinNative driver and is unchanged by this build.

Keep: required subgroup size 64 for correct dequantization, packed reconstruction with eight-wide apron handling, queued display with completion before buffer reuse, and completed decode feedback to adaptive bitrate. Device-specific shader and handoff defaults are restricted to Mesa Turnip on device ID `0x44030a20`.

Rejected experiments and their measurements are retained in the reports. The latest APK is a debug-signed personal build; its version label remains `0.44.0-dev-mokomis.1`. Use its checksum to distinguish it from earlier builds. Install over the same application ID with the same signing key to retain pairing. Do not uninstall to resolve a signature mismatch.

## Current recommended default

Use [HEVC 800 / NVENC P4](CURRENT-STREAMING-DEFAULT.md) at 2520×1680@144 with 10-bit HDR and immediate presentation. The tuned PyroWave/Turnip path remains available as an alternative. No APK or driver rebuild is required for the selected configuration.

## Build the client

1. Follow the tool setup in `../main-55cc38de-mokomis.1/BUILD-INSTRUCTIONS.md`.
2. Clone the upstream mirror, check out the pinned base, then apply the eleven numbered client patches with `git am`.
3. Apply `client-turnip-combined.patch` using `git apply`. This includes the generated reconstruction shader and all retained changes; do not additionally apply the individual experiment patches.
4. Extract the release asset `turnip-client-native-libraries.zip` into the source root. This supplies `clients/android/kit/src/turnipJniLibs/arm64-v8a/` with the six bundled libraries. Their exact bytes are used by the tested APK.
5. Run `VERSION_NAME=0.44.0-dev-mokomis.1 ./clients/android/gradlew -p clients/android :app:assembleDebug` with JDK 21, the documented SDK/NDK and Rust tools available.
6. Install with `adb install -r .../app-debug.apk`, set `adb shell setprop debug.punktfunk.vulkan_driver turnip`, then restart the app. Debug properties may need restoring after a device reboot.

To rebuild AdrenoTools from the included source snapshot, configure CMake with the NDK toolchain, `ANDROID_ABI=arm64-v8a`, `ANDROID_PLATFORM=28`, `CMAKE_BUILD_TYPE=Release` and `BUILD_SHARED_LIBS=ON`, then build. Copy `libadrenotools.so` and the four `src/hook/` library outputs; copy the separately built Mesa driver into the bundled library directory. The archive already contains the tested library set.

The Mesa driver is built by the pinned workflow, also included here. The native library archive includes the driver and AdrenoTools hooks so rebuilding the client does not depend on reproducing those binaries first. Source provenance and licenses for the native components are included in that archive.

## Results

Start with `turnip-final-validation-report.md`, then `turnip-five-checks-report.md`, then the reconstruction, queued-display and corruption reports. Release assets hold the driver ZIP, final APK, native libraries, checksums, and complete experiment evidence. The final sustained, cooling/recovery and packed-read checks are complete.

## HEVC and AV1 comparison

The [final P4 comparison](codec-comparison/hevc-p4-pyrowave-final-report.md) is the current result: HEVC 800/P4 practically matches inspected static detail, with 16.75 ms mean displayed p50 capture-to-decoded latency versus 17.5 ms for tuned PyroWave in two final samples each. Both were verified at 2520×1680; lighting changed and motion fidelity was not tested with an identical replay.

Earlier [live codec observations](codec-comparison/codec-comparison-report.md) are retained, but the approximately 4% display-scaling mismatch confounded their 400 Mb/s softness judgments. Full-panel comparisons removed that mismatch. AV1 is not the selected default. P5–P7 remain untested. Evidence is attached to the same release.
