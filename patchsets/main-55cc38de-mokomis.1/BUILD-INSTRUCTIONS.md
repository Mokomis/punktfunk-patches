# Build the custom Punktfunk Android client (personal use)

Give this file to the agent doing the build. Work through the steps in order and stop at the first failure; do not change the patches to get past it.

## What this builds

Upstream Punktfunk at commit `55cc38de8a20271fd86fbf95d59dbc3beffea207` with the 11 patches in this folder's `client/` applied. The result is a debug APK with application id `io.unom.punktfunk.mokomis`. Build it on the same computer that built the APK now on the tablet: it is then signed with the same debug key and installs over it, keeping settings and pairing.

## 1. Tools

| Tool | Version |
|---|---|
| JDK | **21** (17–21 work; not newer) |
| Android SDK packages | `platforms;android-37.0`, `build-tools;37.0.0`, `cmake;3.22.1`, `ndk;30.0.14904198` |
| Rust | via rustup; the repo pins 1.96.0 and rustup installs it on first use |
| Rust Android target | `rustup target add --toolchain 1.96.0 aarch64-linux-android` |
| cargo-ndk | `cargo install cargo-ndk` |
| git | any |

Install the SDK packages with Android Studio's SDK Manager, or:

```sh
sdkmanager "platforms;android-37.0" "build-tools;37.0.0" "cmake;3.22.1" "ndk;30.0.14904198"
```

Set `ANDROID_HOME` to the SDK folder, and `JAVA_HOME` to JDK 21 if the default JDK is newer.

## 2. Source and patches

```sh
git clone https://github.com/punktfunk/punktfunk.git
cd punktfunk
git checkout -b mokomis 55cc38de8a20271fd86fbf95d59dbc3beffea207
git -c user.name=me -c user.email=me@localhost am /path/to/punktfunk-patches/patchsets/main-55cc38de-mokomis.1/client/*.patch
git log --oneline -12
```

The `github.com/punktfunk/punktfunk` mirror has the same history as upstream `git.unom.io/unom/punktfunk`; either works. `git am` must apply all 11 patches without conflicts. If one fails, run `git am --abort` and stop.

## 3. Build

```sh
cd clients/android
VERSION_NAME=0.44.0-dev-mokomis.1 ./gradlew :app:testDebugUnitTest
VERSION_NAME=0.44.0-dev-mokomis.1 ./gradlew :app:assembleDebug
```

The first build downloads dependencies and cross-compiles the native library, which takes a while. The APK is in `clients/android/app/build/outputs/apk/debug/`. Report any failing unit test before installing.

## 4. Install

Back up the APK currently on the tablet first, so you can go back:

```sh
adb shell pm path io.unom.punktfunk.mokomis      # prints package:/data/app/.../base.apk
adb pull <that path> punktfunk-previous.apk
adb install -r app/build/outputs/apk/debug/<the apk>.apk
```

If the install fails with a signature error, this computer's debug key differs from the old build's. Stop: uninstalling would delete the app's settings and pairing.

To go back: `adb install -r -d punktfunk-previous.apk`. `-d` allows the downgrade for a debug build.

## 5. Check on the tablet

1. Connect to the PC as usual.
2. Run `adb logcat -s punktfunk` and look for:
   - `display HDR luminance peak=` on an HDR session;
   - `pyro: swapchain ... HDR10_ST2084` on a PyroWave HDR session;
   - `idwt="fragment"` (fragment-shader wavelet decode).
3. Settings → Display shows **Frame presentation**; your choice there should still be **Direct, on arrival**.
4. The stats overlay shows the `wi-fi ↓ … Mb/s` line.
5. In the library, a title can be bound to a preset.
6. For PyroWave, set the bitrate to **Automatic** and use the new **PyroWave quality** setting. The old patch that kept a fixed PyroWave bitrate from being lowered on connect is not included.

## The host (PC)

The client is built from newer upstream code than the PC's `0.42.0+reconnect-fix.3` host. The patch in `host/` is ready for it, but a full Windows host build also rebuilds and re-signs the virtual-display driver (Windows Driver Kit, MSVC, CMake, LLVM), which is much more work.

Recommended order:

1. Install the new client and try it against the current host first.
2. Build a new host only if a session fails: no connection, or the picture freezes while audio continues. To build it, use the same commit, `git am host/*.patch`, then follow upstream's `docs-site/content/docs/developers/build-from-source.md` ("Windows host and client") and `packaging/windows/README.md` for the installer and driver.

## What has and has not been checked

- **Checked:** the original 12 patches matched their published checksums before porting. The host patch compiles for Windows and its keepalive tests pass. The console UI and Android native Rust code compile on Linux.
- **Not checked:** the Android build itself, the Kotlin app and its unit tests. Nothing has run on the tablet.
- **Dropped on purpose:** the 4:4:4 patch (ruled out on heat) and the fixed-bitrate PyroWave patch.
- **Not included:** anything in `0.43.1-mokomis.3` beyond the published `0.43.1-mokomis.2` series.
