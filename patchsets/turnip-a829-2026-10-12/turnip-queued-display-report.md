# Decode-to-display handoff — 2026-10-12

Implemented, built and installed a queued display handoff for Punktfunk on this tablet. The Android client selects it automatically only for Mesa Turnip on Adreno 829 (device ID `0x44030a20`). The original fence-first path remains the default for other driver/device combinations and for existing shared-decoder callers.

The app now records and submits display work while GPU decoding is still underway, then waits for decode completion before reusing decoder buffers or publishing CPU latency/audio timing. It still has at most one pending decode. This overlaps CPU display work with decoding without adding more frames to the pipeline.

The existing decode-to-fragment memory barrier protects sampling on the same queue, including later submissions, under the [Vulkan pipeline-barrier rules](https://docs.vulkan.org/refpages/latest/refpages/source/vkCmdPipelineBarrier2.html). No extra inter-queue semaphore is required here. The queued decoder API is explicitly unsafe: any sampling must use that queue after decode submission and before the next decode. The synchronous API retains its completion guarantee. Resize waits for pending decode; teardown idles the shared queue before destroying resources.

## Measurements

Same running No Man’s Sky save, 2414×1680 at 144 Hz, 10-bit 4:2:0 HDR, target 1125 Mb/s. Each reported window contains 600 successfully submitted pictures. The analysis excludes the first two retained windows per process and keeps at most ten following windows. Raw log buffers can roll over, so the archive includes the exact selected windows.

| Run under the normal governor | CPU decode/display handoff | Receipt to completion | Decoded/submitted FPS |
|---|---:|---:|---:|
| Repeated original-path control | 5.687 ms | 6.135 ms | 136.8 |
| Queued handoff, second test | 4.593 ms | 4.737 ms | 137.1 |
| Final build, automatic selection | 4.493 ms | 4.615 ms | 137.0 |

The latest valid control/test pair shows about **1.1 ms less CPU handoff time**. Frame rate is essentially unchanged. These are live observations with adaptive GPU/CPU clocks, a changing day/night scene and variable network delivery; they do not establish an exact causal percentage or physical display latency.

Earlier runs during a thermal transition measured 8.486 ms / 113.9 FPS for the control and 7.263 ms / 131.5 FPS for queued handoff. Those values are retained in the JSON but excluded from the headline because clock and thermal conditions changed. A requested 646 MHz maximum was not consistently honored by actual GPU frequency telemetry. Cap-attempt data is retained for transparency and excluded from fixed-clock conclusions. Failed connection attempts with no timing windows are also excluded. The GPU limit is restored to its original 1,225,000,000 Hz maximum / power level 0.

`fence_wait` measures actual CPU blocking. `observed_completion` is submit-to-CPU-observed completion, not a pure GPU timestamp: delayed observation and intervening CPU display work are included. `total` measures decode-call entry through display submission and decode completion. `receipt_to_complete` starts at packet reassembly. Both variants wait for actual decode completion before reporting latency, so the improvement does not come from relabeling a pending frame as finished.

## Validation and final state

- Android build passed; native imports passed the API-28 compatibility check.
- Narrow patch reverse-apply check and whitespace check passed.
- Motion check: user reported “Looks clean”; screenshots also appeared clean.
- No shaders, colour math, image formats or filtering were changed in this phase. There was no new offline pixel-by-pixel comparison; this phase tests synchronization and lifetime behavior.
- No decode-fence timeout or device-loss error was observed in the retained active-session logs.
- Repository writing check still fails on pre-existing patch commit subjects. The touched decoder module documentation was shortened to the repository limit.
- Diagnostic handoff/profiling overrides are cleared. Automatic selection remains enabled on the tested Turnip/Adreno pair; other pairs remain synchronous.
- Automatic rotation is restored: accelerometer rotation 1, user rotation free, fixed-to-user rotation disabled. Temporary testing controls caused the reported portrait lock and were removed.
- Earlier dequant subgroup-64 corruption workaround and reconstruction optimization remain. DroidDeck is unchanged.

## Files and rollback

`punktfunk-turnip-queued-display.apk` is the installed final APK. `turnip-queued-display.patch` contains only this handoff change, layered over the preceding reconstruction build. `turnip-queued-display-results.json` contains selected timing windows; `turnip-queued-display-evidence.zip` contains raw logs, clocks, build/check output and the patch.

For a diagnostic comparison, `debug.punktfunk.pyro_queue_present=0` selects fence-first; `1` selects queued presentation; an empty value uses automatic detection. Restart the client after changing it. `debug.punktfunk.pyro_handoff_stats=1` enables the CPU timing log. Clear both after testing. The preceding `punktfunk-turnip-reconstruction.apk` remains available as a full APK rollback.
