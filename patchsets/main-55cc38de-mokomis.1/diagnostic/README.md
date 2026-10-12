# PyroWave plane replay (diagnostic, work in progress)

Not part of the client build. Apply on top of the client series to compare drivers:

```sh
git am ../client/*.patch
git am 0001-pyrowave-plane-replay.patch
```

Purpose: capture identical PyroWave AUs from a live session, decode them on the Qualcomm
driver and on Turnip, and compare the raw Y/Cb/Cr planes before colour conversion.
Status: builds on Linux; not yet run on the tablet. Steps follow once the tool has been
validated on a Linux reference.
