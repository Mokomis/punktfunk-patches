# Current streaming default — HEVC 800 / P4

Selected personal default after the October 12, 2026 comparison:

| Setting | Value |
|---|---|
| Codec | HEVC |
| Bitrate target | 800 Mb/s (800000 kb/s) |
| Windows NVENC preset | P4 |
| Stream size | 2520×1680, full panel, landscape |
| Refresh target | 144 Hz |
| Color | 10-bit HDR, 4:2:0 |
| Client low-latency mode | On |
| Frame presentation | Arrival / immediate release |

The Windows host setting is `PUNKTFUNK_NVENC_PRESET=4` in `%ProgramData%\punktfunk\host.env`. The next stream uses the preset after the host restarts. The desktop HEVC-Preset-Test launcher provides P4, P1 and restoration of the host settings saved before testing. Changing this host setting can also affect other NVENC sessions; it is not a per-game override.

Practical conclusion: HEVC 800/P4 matches the inspected static detail of tuned PyroWave in this scene, with similar capture-to-decoded latency. Two final HUD samples averaged 16.75 ms / 137.5 FPS for HEVC and 17.5 ms / 134 FPS for PyroWave. Lighting changed, and no controlled motion replay or source-reference quality score establishes equality in every scene. The user also reported P4 sharper or cleaner than the earlier HEVC setting.

Keep P4 for now. P5 is the next optional comparison; P5, P6 and P7 have not been tested here, so no further quality or latency gain is claimed. No HEVC-versus-PyroWave power measurement was performed.

Keep the game focused after reconnecting. In this session, clicking the game recovered HEVC from 30 FPS with visible character artifacts to approximately 136–138 FPS with clean rendering.

HEVC uses the Qualcomm hardware video decoder. Bundled Turnip remains available for PyroWave, which stays installed as an alternative. The driver and APK are unchanged. This is the user's chosen configuration and the archive's recommendation, not a new hard-coded default in the APK or an upstream default change. DroidDeck is unchanged.
