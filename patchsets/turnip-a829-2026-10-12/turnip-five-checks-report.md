# Turnip streaming checks

Tested the No Man’s Sky save on OPD2515 / Adreno 829 at 2414×1680, 144 Hz, 10-bit HDR, with the existing automatic bitrate target of 1125 Mb/s. No manual image-quality reduction was made.

| Check | Result | Decision |
|---|---|---|
| CPU packet parsing | Retaining the fragment buffer saved only 0.303 microseconds per access unit, about 0.25%, in isolated replay. Live runs were affected by changing temperature. | Rejected. |
| GPU dequantization | Removing one subgroup synchronization step saved about 0.27%, below run variation. All 48 compared output planes were byte-identical. | Rejected. Keep the required subgroup size of 64. |
| Memory and barriers | After warm-up, PSS stayed around 474 MB (reported in KiB in the raw data). Existing staging reuse and linear texture aliases were active. | Keep buffer lifetimes and required visibility barriers. |
| Frame pacing | 93.79% of observed intervals were one refresh, 5.92% two refreshes, 0.29% longer. Median 6.95 ms, p95 13.89 ms. Two late gaps reached 250 and 125 ms. | Keep the existing presentation mode. |
| Sustained performance | About 136–137 FPS initially, falling to 127.6 and 123.7 FPS late in the ten-minute run. Battery temperature rose 36.3→41.1°C; battery level fell 79→75%. GPU frequency fell to 646 MHz. | Heat is a material limit; Wi-Fi also weakened late. |

The thermal status reached Android’s severe level. Status meanings follow [Android PowerManager documentation](https://developer.android.com/reference/android/os/PowerManager). No thermal limits were overridden. Battery current units were not verified, so there is no watt estimate.

The slowdown preceded the late network event: decode/display handoff rose from about 4.4–4.7 ms to 7.1–7.6 ms while wire rate remained near 1.06 Gb/s. Later, Wi-Fi weakened and the existing adaptive controller automatically reduced its target from 1125 to about 822 Mb/s after lost frames. That automatic change occurred during the test; we did not manually lower quality. The exact cause of the two long presentation gaps was not isolated.

## Fix found and installed

PyroWave measured completed decode latency for the HUD but did not report it to adaptive bitrate. Its late controller log therefore showed `decode_mean_us=-1`. The new build reports the completed-frame receipt-to-decode interval after GPU completion, independently of whether the HUD is enabled. It preserves the existing adaptive policy and quality preferences.

The Android build succeeded, all 43 adaptive-controller tests passed, and the APK was installed on the tablet. The running stream logged `adaptive bitrate decode feedback active sample_us=78077`; this is the first startup sample, not a steady-state latency claim. A subsequent screenshot showed 135 FPS with a 1125 Mb/s target and 4.5 ms HUD decode time. Reconstruction optimization and queued display remain active. No new performance gain is claimed for this feedback fix, and a second ten-minute soak has not been run.

`git diff --check` passed. The repository writing check still fails on existing patch commit titles; its diagnostics are included in the evidence archive. This change does not rewrite those commits.

## Evidence limits

The soak retained full health, presentation and memory series, but only the final roughly 43 seconds of Android logs. There was no decoder device-loss or fence timeout in that retained segment. A still image cannot verify motion artifacts. Raw plane files are omitted from the archive; comparison manifests retain their hashes.

The APK `punktfunk-turnip-decode-feedback.apk` is the installed build. `punktfunk-turnip-queued-display.apk` remains the prior working fallback. DroidDeck was not changed.
