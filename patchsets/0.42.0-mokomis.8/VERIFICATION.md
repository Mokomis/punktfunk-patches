# Verification — October 9, 2026

Android client `0.42.0-mokomis.8` (arm64, application id `io.unom.punktfunk.mokomis`) for an OPPO Pad Mini (Snapdragon 8 Gen 5, Adreno 829, ColorOS 16) against Windows host `0.42.0+reconnect-fix.3`.

This is [`0.42.0-mokomis.7`](../0.42.0-mokomis.7) plus one patch. The other eleven are byte-identical to that set.

## The added patch

`android-per-title-presets.patch` closes three gaps around per-title streaming settings.

1. **Frame presentation in the console (controller) settings.** `mokomis.7` added the setting to the touch settings screen only. With a controller attached the client shows its console interface, whose Display page had no such row. It now has one, in the advanced group below Low-latency mode, Android only, stored under the same `android.frame_presentation` key.
2. **A preset can carry Frame presentation.** It is an overlay field, like Low-latency mode, so one title can use a different display path from another. It is edited from the touch settings screen with a preset selected as the scope; the console's preset editor does not model Android-only rows.
3. **Per-title presets from the touch library.** A title's menu gains **Settings preset…**, which binds one of the existing presets to that title (or clears the binding). A launch from the touch library now uses the title's binding. Before, the touch library ignored bindings: only the console interface wrote or honoured them. A shelf opened from a pinned host card still uses that card's preset for every title, as upstream intends.

## Results

- **Console interface tests:** `cargo test -p pf-console-ui --lib` passed, 386 tests (8 ignored), on macOS. Two tests that list the settings rows were updated for the new row.
- **App unit tests:** `./gradlew :app:testDebugUnitTest` passed, 205 tests, including the preset round-trip with the new field.
- **Install:** installed over `0.42.0-mokomis.7` with the same signing key; stored settings were unchanged afterwards.
- **On the device, item 1:** the console Display page shows **Frame presentation — Direct, on arrival**, the value stored earlier from the touch screen.
- **On the device, items 2 and 3:** not yet exercised. No preset has been created on this tablet, so the picker and a bound launch have not been run.
- **Reproducibility:** the twelve patches applied in order to a clean `v0.42.0` tree, and the result matched the built source with no differences outside the app-id files.

## Limits

- Changing the new row from the console interface, and the stream that follows, were not exercised; the row was only read.
- The touch library resolving a preset per title is a deliberate departure from upstream, which resolves one preset per shelf so that two titles on a shelf cannot stream differently.
- The console change is in shared code (`pf-console-ui`), but the row is declared Android-only and was only built for Android.
