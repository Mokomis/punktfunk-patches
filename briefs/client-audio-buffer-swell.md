# Brief: client audio buffer swells at connect

A self-contained task for a session with no access to the tablet, the Windows host or the home network. Source-only: write the change, prove it with unit tests, deliver a patch. Do not claim it fixes anything on the device; that is tested later on the tablet.

## Read first

- `BACKLOG.md` in this repository, section **Client**, item 1 ("Audio buffer swells at connect"). It has the measurements and the code locations.
- `patchsets/0.42.0-mokomis.4/` for the layout and writing style of a client patchset and its `VERIFICATION.md`.

## Source

Upstream is `https://git.unom.io/unom/punktfunk.git`, tag `v0.42.0` (commit `8f046f239f3d6dcfc1fa0a25343be926a233a5a5`). Clone it outside this repository. **If it cannot be reached, stop and say so with the exact error. Do not reconstruct the code from memory.**

The code is in `crates/punktfunk-core/src/audio/jitter.rs` (`JitterPolicy`: `step`, `note_read`, the constants `GROW_UNDERRUNS`, `GROW_WINDOW_MS`, `GROW_STEP_MS`, `SHRINK_QUIET_MS`, `SHRINK_QUIET_SYNC_MS`, and about a dozen existing unit tests). The Android caller is `clients/android/native/src/audio.rs`. The change does not conflict with the other client patches, so work on plain `v0.42.0`.

## The problem

The host sends no audio packets during true silence. At connect the PC is usually silent, so the client's ring runs dry, or primes on a stray sound and then empties. The policy counts each of those as an underrun, and three in five seconds grow the target by 10 ms, up to the 90 ms ceiling of `JitterTuning::AAUDIO`. The result is sound 110–140 ms behind the picture for about two minutes after every connect, until the slow shrink brings the target back to 25 ms.

A drained ring because nothing was sent is not a struggling link, and should not grow the buffer.

## What to build

One patch, client-only, no wire or protocol change, no host change.

1. Make the policy tell "the source was silent" from "audio was sent and arrived late", and stop counting the first as an underrun. Look at what the caller already knows before adding anything: packet sequence numbers resuming without a jump mean nothing was lost or late; a jump or a burst after a hole means late audio. Prefer the smallest change that the existing structure supports.
2. Keep genuine protection: late or bursty audio on a bad link must still grow the target exactly as it does now. Every existing test must still pass unchanged, unless a test encodes the behaviour being fixed, in which case say which and why.
3. Do not change the tuning constants or the 90 ms ceiling.

## Verification expected

- New unit tests in `jitter.rs` for: a silent start that never grows the target; a stray sound then silence; continuous audio with real late arrivals still growing as before; silence in the middle of a session.
- `cargo test -p punktfunk-core` for the audio module, and `cargo clippy` on the crate.
- The Android client itself will probably not build in this environment (it needs the Android NDK). Say plainly whether the Android caller was compiled or only edited.

## Deliverable

A pull request on this repository, from a new branch, **not merged**, containing:

- `patchsets/0.42.0-client-audio-buffer.1/client-audio-buffer-silence.patch` (plain `git diff` against `v0.42.0`),
- `SHA256SUMS`,
- `VERIFICATION.md`: what changed and why, exactly what was run and what was not, what to measure on the tablet (the client logs `audio: ... buffer_ms=… target_ms=… av_ms=…` every few seconds; a fixed build should hold `target_ms=25` through a silent connect), and any design decision the owner should confirm.

Write for a reader who was not in the session: short, concrete, no claims beyond what was run.

Do not push to, open issues on, or contact `git.unom.io`; these patches are private. Do not delete this brief; the owner will remove it.

End the pull request description with: 🤖 Generated with [Claude Code](https://claude.com/claude-code)
