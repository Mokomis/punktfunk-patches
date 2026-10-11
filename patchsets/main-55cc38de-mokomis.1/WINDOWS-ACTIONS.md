# Personal Windows host installer

The `Build personal Windows host` GitHub Actions workflow builds the x64 host from upstream commit `55cc38de8a20271fd86fbf95d59dbc3beffea207` and applies this patchset's host patch. It uses the upstream installer scripts and rebuilds the virtual-display and gamepad drivers.

Open the successful run under Actions and download `punktfunk-host-0.44.0-dev-mokomis.1-windows-x64`. Extract the ZIP on the host PC and run its setup executable. Windows 11 22H2 or newer is required. Settings are preserved by the upstream upgrade installer.

The default is a personal self-signed build, so Windows may show an unknown-publisher prompt. The drivers use the upstream personal-build certificate path. No upstream signing credentials are used. SHA256SUMS.txt covers the downloadable files.

The workflow includes compile checks, Windows unit tests, installer inspection and a silent dry-run. Streaming, HDR and GPU behavior still need testing on the real PC and tablet.

If the upstream npm registry requires authentication, set the repository secret `UNOM_REGISTRY_TOKEN` to a token that can read its packages. Optional stable personal signing secrets are `MSIX_CERT_PFX_B64`, `MSIX_CERT_PASSWORD`, `DRIVER_CERT_PFX_B64` and `DRIVER_CERT_PASSWORD`; otherwise the upstream scripts generate temporary certificates for this build.
