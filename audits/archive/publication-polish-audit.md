# Publication Polish Audit

## Implemented improvements

- Added CI-driven first-page PDF preview generation for the paper, magazine, and print edition.
- Switched OpenGraph/Twitter previews to generated publication cover assets.
- Added breadcrumb navigation, publication history, and edition cards to the landing page.
- Replaced hard-coded landing-page metadata with manifest-driven hydration where available.
- Preserved the existing publication architecture and embedded reader workflow.

## Analytics evaluation

No analytics are enabled in this repository at this stage.

For future adoption, prefer an optional, privacy-preserving, cookieless setup such as:

1. self-hosted GoatCounter
2. self-hosted Umami in privacy mode

Recommended collection scope:

- landing-page visits
- PDF download click-throughs
- DOI outbound clicks

Recommended constraints:

- no advertising identifiers
- no cross-site tracking
- no fingerprinting
- no personal data retention
- explicit documentation in repository docs before enablement

## Reader-experience outcome

The publication landing page now emphasizes publication-specific navigation and edition discovery without redesigning the existing presentation model.
