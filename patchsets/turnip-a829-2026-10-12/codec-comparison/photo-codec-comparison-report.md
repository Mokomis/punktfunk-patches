# Photo-mode follow-up — October 12, 2026

Practical visual judgment: PyroWave and HEVC with an 800 Mb/s target look very close in the matched-size No Man’s Sky still captures. Inspection of foliage, rock texture and suit detail did not reveal a convincing visual advantage for either. Keep the tuned PyroWave setup: HEVC 800 has not shown an improvement that warrants switching, and PyroWave has not demonstrated a large win over HEVC 800.

The earlier live comparison measured about 16.9 ms capture-to-decoded availability for PyroWave and 17.4 ms for HEVC 800. This photo follow-up did not repeat latency measurements. HEVC’s 800 Mb/s target previously produced about 387 Mb/s of actual traffic versus about 302 Mb/s at its 400 target; it did not consume the full target.

## Correction to the earlier quality interpretation

With the original 2414×1680 safe-area mode, image registration found approximately 4.1% different horizontal scaling between codec outputs. PyroWave logs showed a 2520×1680 swapchain for the 2414×1680 decoded frame. The underlying cause was not established. Earlier user reports that HEVC/AV1 at 400 looked softer remain recorded observations, but they cannot isolate codec quality from this display scaling difference.

For the follow-up, both codecs temporarily requested 2520×1680. Registration then found scale differences of approximately 0.08% horizontally and 0.135% vertically, with about one pixel of offset. These captures provide a much closer framing comparison. There is no obvious static-image winner; this is a practical visual assessment, not a source-reference fidelity score.

## Method and limits

The user entered photo mode with fixed time of day. Three stills were captured per session in a PyroWave → HEVC 800 → PyroWave sequence. No camera input occurred between those codec captures. A separate mouse calibration moved and returned the camera with roughly 10–12 pixels of drift. A paired, identical-motion codec replay was not completed, so no new controlled motion result is claimed.

No original lossless host reference was captured. Android screenshots do not reproduce the complete HDR-panel experience. Pixel disagreement between codecs is not a measure of which is more faithful.

Original settings were restored afterward, including PyroWave, quality 1.8, automatic target selection, native safe-area resolution, HDR and presentation preference. Turnip selection was verified and the temporary virtual mouse was removed. No client code, APK or driver changed.

Release files photo-pyrowave.png and photo-hevc-800.png are the first matched-size captures. The evidence archive includes all three full-size sessions, verification logs, registration results and comparison helpers. Private settings backups and installed analysis dependencies are excluded.
