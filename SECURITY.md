# Security and safety policy

RepairDB is a static, educational reference. It does not collect accounts, device identifiers, repair submissions, or telemetry. Search runs in the visitor's browser; the dataset is fetched from the same site origin. Theme preference is stored in local storage. There are no forms or backend services.

## Safe-use boundaries

Content must not encourage lithium-cell puncture, bending, reflow, baseband/carrier protection bypass, or unsafe disassembly. Stop and seek qualified service for swelling, smoke, severe heat, liquid exposure, or damaged glass. The examples are not verified model-specific faults, and they are not a substitute for manufacturer manuals or trained repair expertise.

## Reporting a vulnerability

Please avoid filing a public issue with exploit details if you believe you have found a security issue in the site, its dependency handling, or the build workflow. Contact the repository maintainer privately using the security contact configured in the GitHub repository. Include steps to reproduce and impact, but do not send personal repair records or device identifiers. If no private contact is configured yet, request one through a minimal public issue without sensitive details.

## Supply chain

GitHub Actions are pinned to immutable commit SHAs. Fuse.js 7.5.0 is vendored locally to avoid a runtime dependency on a script CDN; its upstream Apache-2.0 license is retained in `assets/FUSE-LICENSE.txt`. Review dependency updates and keep test/deploy permissions scoped to the workflow's needs.
