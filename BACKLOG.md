# Potential patches

Ideas not yet built, for the Windows PunktFunk host and for the Android client. The host on the PC today is `0.42.0+reconnect-fix.3`; the client on the tablet is `0.42.0-mokomis.4`.

- [Host](#host)
- [Client](#client)
- [Background: Wi-Fi 7 width switching on the tablet](#background-wi-fi-7-width-switching-on-the-tablet)

Evidence paths such as `logs/...` refer to the local tuning folder the measurements were taken in; those logs are not in this repository.

# Host

## 1. Audio channel stalls (added October 4, 2026)

**Symptom.** Audible gaps in game sound, worst in heavy scenes and at death/respawn. The client fills 50–150 ms holes and its audio buffer swells to 90 ms, putting sound about 140 ms behind the picture.

**What was measured.**

- The host hands audio over on time: `audio egress` showed 6,000 packets per 30 s, 0 infilled, 0 late, worst lateness 2 ms, while the gaps were happening.
- A packet capture on the tablet's audio/control port showed the packets arriving late: gaps of 46–142 ms, then the backlog in a burst (28–53 packets in the next 100 ms, where 20 is normal). The whole channel went quiet in both directions during each gap.
- Video on its separate UDP path kept flowing through every gap with no loss, on the same Wi-Fi link.
- Uncapped battle: 9 gaps in 4 minutes. Game capped at 60 fps: 2 gaps in 4 min 20 s, one of them (120 ms) with video perfectly steady.
- The host process already runs at High priority, and the PC's CPU (Ryzen 7 7800X3D) was not saturated.

**Where it is in the code.** Audio rides QUIC datagrams on the control connection (`crates/punktfunk-core/src/quic/endpoint.rs`, `datagram_send_buffer_size(4 * 1024)`, "latest-wins under congestion"). Video rides raw UDP. The host counts audio as sent when it calls `send_datagram` (`crates/punktfunk-host/src/native/audio.rs`), before any hold-up; the source notes that eviction there is silent.

**Not established.** Why the channel stalls. Candidates: the QUIC connection's congestion control or pacing backing off after a lost or delayed packet; or the host's QUIC task being delayed when the GPU is saturated. GPU load is a trigger but not the whole cause.

**Found in the source afterwards (v0.42.0).** The host's async runtime is built with two worker threads (`crates/punktfunk-host/src/native.rs`, `worker_threads(2)`), the QUIC connection is driven on it, and session code on the same runtime uses `block_in_place`. The QUIC transport uses the library's default congestion control and pacing; nothing is customised. Either could produce the stall; which one does is not measured.

**Possible directions.**

- Host-only, no protocol change: drive the QUIC endpoint on its own dedicated thread/runtime so blocked workers cannot delay it. The user's preferred long-term idea (October 4, 2026).

- Give the audio/control connection a congestion controller that does not back off for a flow this small, or disable pacing on it.
- Move audio off the shared QUIC connection onto its own UDP path with redundancy, as video has.
- Add a host counter for datagrams evicted or delayed after `send_datagram`, so the stall shows in the host log.

**Evidence files.** `logs/audio_gap_qcap.txt`, `logs/audio_gap_full_2.log` (uncapped), `logs/audio_cap60_qcap.txt`, `logs/audio_cap60_full.log` (60 fps cap), `logs/shots/h4a.png`, `h4b.png`, `h5a.png`, `h5b.png` (host log).

## 2. Reconnect refinements not confirmed in upstream 0.43

From `patchsets/0.42.0-reconnect-fix.3`. Upstream 0.43.0 replaced the fixed 1.5 s reconnect wait its own way; these three smaller parts were not confirmed to be there, and the patch does not apply to 0.43 as written (conflicts in `admission.rs` and `handshake.rs`).

- Interruptible display keepalive.
- Skipping the video drain on stop.
- Bounded silent-audio reads, so a session stop releases the parked capture promptly.

Check whether 0.43.x still needs each one before porting.

## 3. Stream goes silent on a still picture (added October 5, 2026)

**Why it matters.** With PyroWave the host sends almost nothing while the picture is still (a menu, a loading screen, the desktop: 0 to 60 Mb/s measured). On the OPPO tablet that lets the Wi-Fi link drop to 80 MHz, and the next movement asks for 1.1 Gb/s on a link that carries about half of that until it widens again. See the background section below.

**Possible directions.**

- Keep the link loaded during a still picture, for example by continuing to send frames at the session's rate for a short hold time after motion stops. A trickle is not enough: the tablet stayed at 80 MHz at every rate up to 100 Mb/s.
- Ramp the bitrate over a few hundred milliseconds when motion resumes, so the first frames fit the narrow channel.

**Not established.** Whether the resume actually costs frames. The step from 80 to 320 MHz takes about 8 ms when it works and up to 150 ms when the request times out (39 of 136 did), but dropped frames were not lined up against those moments.

# Client

None of these is specific to the OPPO tablet; they are in the client's shared audio code and would behave the same on any Android device. The OPPO-specific part of the audio delay (ColorOS keeping apps off the low-latency output paths) is handled outside the client and documented in the public `opd2515-low-latency-audio` repository.

## 1. Audio buffer swells at connect (added October 4, 2026)

**Symptom.** In the first seconds of every session the audio buffer target climbs from 25 ms to its 90 ms ceiling, putting sound about 110–140 ms behind the picture. On a clean link it steps back down to 25 ms in roughly two minutes; on a session with late audio it stays up.

**What was measured.**

- At connect the PC is usually silent, and the host sends nothing during true silence. In one 68-second desktop session only 765 audio packets arrived, where play delivers about 200 per second.
- The client counted 4,900 to 21,000 "underruns" in those seconds. Most are the client playing silence because there is nothing to play; the rest are the buffer priming on a stray sound and then emptying, which the policy reads as a device that needs more slack.
- Decay afterwards, on a clean 1,128 Mb/s stream: 90 to 25 ms between 10:06:44 and 10:08:29, after which the client measured audio 71–73 ms behind the picture (55–63 ms with the low-latency output path).

**Where it is in the code.** `crates/punktfunk-core/src/audio/jitter.rs`: three underruns in a 5 s window, or one near-miss, grow the target by 10 ms (`GROW_UNDERRUNS`, `GROW_WINDOW_MS`, `GROW_STEP_MS`), up to `max_target_ms` (90 for `JitterTuning::AAUDIO`). It shrinks one step per 30 s of quiet, or per 5 s when the A/V sync loop is asking for less (`SHRINK_QUIET_MS`, `SHRINK_QUIET_SYNC_MS`). The Android side is `clients/android/native/src/audio.rs`.

**Possible directions.**

- Do not count a drained buffer as an underrun while the host is sending no audio at all: a silent source is not a struggling link. This needs a way to tell "nothing was sent" from "it was sent and is late", for example from the packet sequence resuming without a jump.
- Hold the grow logic off until audio has flowed continuously for a second or two after connect.
- Shrink faster once a session has been clean for a while.

**Not established.** Whether any of these would be audible in practice. The swell costs about two minutes of extra delay per connect and then clears by itself; the larger audio problem is the host-side stall above.

**Evidence files.** `logs/audio_capture_full.log` (connect and decay), `logs/audio_fastpath_test.log`, `logs/audio_gap_full_1.log`.

## 2. Connect-time speed test reads the narrow channel (added October 5, 2026)

**Symptom.** On every connect the bring-up ramp reports a wall at about 500 to 545 Mb/s with no packets lost, and an unpatched client lowers a PyroWave pin to roughly 350 Mb/s. `pyrowave-pin-timing-wall.patch` works around it by keeping the pin when the wall lost nothing.

**Likely cause (inference, not tested directly).** The ramp sends 25 ms bursts. The tablet's Wi-Fi firmware reconsiders its channel width every 100 ms and sits at 80 MHz when idle, so the ramp finishes before the link has widened and measures the 80 MHz channel. About 520 Mb/s is what that channel carries. A sustained 1.1 Gb/s stream on the same connection runs at 320 MHz with no loss.

**Possible directions.**

- Precede the ramp with a few hundred milliseconds of traffic, or make the last ramp steps long enough to span several 100 ms decisions.
- Treat a timing-only wall as provisional and re-test once the stream has been running for a second.

**Where it is in the code.** `crates/punktfunk-core/src/abr/probe.rs` (ramp), `crates/punktfunk-core/src/abr/mod.rs` (`on_ramped`).

# Background: Wi-Fi 7 width switching on the tablet

Not a patch idea by itself; this is the behaviour several items above work around. Measured October 5, 2026 on the OPPO Pad Mini (Qualcomm WCN7750 Wi-Fi) on a TP-Link Deco 6 GHz network, with the firmware log (`wifidriverlog_on`) and the firmware's message catalogue (`Data.msc`).

**What happens.** The tablet's connection to the 6 GHz network is a Wi-Fi 7 multi-link (MLO) association, with one link. The firmware's multi-link power-save module (`wlan_powersave_mlo_sta.c`) decides the receive width every 100 ms from the tablet's own share of channel airtime, and asks the router to follow with an operating-mode (OMI) frame. The router complies.

| Traffic to the tablet | Width chosen |
|---|---|
| 0 to 100 Mb/s | 80 MHz |
| 200 Mb/s | 80 MHz, asking for more about a fifth of the time |
| 400 Mb/s | flips between 80 and 320 MHz about twice a second |
| 1,100 Mb/s (PyroWave stream) | 320 MHz, steady |

**Consequences.**

- A bitrate between roughly 300 and 700 Mb/s is the worst place to be: the link changes width constantly. A 60 fps cap put PyroWave at 564 Mb/s, inside that range.
- Lower is not automatically safer. Either stay high enough to hold 320 MHz or go well below the range.
- An idle or low-rate reading of 80 MHz says nothing about the connection's quality.

**It is not specific to PunktFunk or to OPPO's software.** Plain UDP from another machine produced the same flipping. It is the Wi-Fi firmware's behaviour on a multi-link association.

**Tried, without finding an off switch.**

| Tried | Result |
|---|---|
| `gEnableBmps=0`, `gEnableImps=0` | Both antennas stay on at idle; width still switches |
| `gDtim1ChRxEnable=0`, `enable_dynamic_nss_chain_config=0`, `gRuntimePM=0` | No visible effect |
| Low-latency profile | Already at the firmware's highest mode during a stream; the module ignores it |
| `mlo_support_link_band=0x33` (no multi-link on 6 GHz) | The Deco rejects the association; reverted |
| `gDot11Mode=10` (Wi-Fi 6E mode) | The tablet no longer sees 6 GHz networks; reverted |
| Deco app, MLO Network off | Removes the separate `_MLO` network only; the 6 GHz network is still multi-link |
| Steady keep-alive traffic | Needs hundreds of Mb/s |

`dynamic_bw_switch` is a transmit-side setting and not this behaviour. The firmware catalogue shows no enable or disable message for the width decision.

**Also found the same evening.** The tablet sometimes joined the far mesh node (4 of about 21 connections) and a running stream kept it there. Fixed on the router: Deco app, the tablet's client entry, Specified Connection set to the near node, Mesh Technology off for that entry; 22 of 22 joins correct afterwards.

**Still unexplained.** On October 4 six connections in a row stayed at 160 MHz under a 1.1 Gb/s stream, on the right node at a strong signal, with a single link. It did not recur in 17 connections on October 5. The module also weighs other networks' airtime, and large file transfers were running through the same mesh that day; that is a possible cause, not a confirmed one.

