# Locus visual design

Locus has its own look. It must be recognisably different from GeoGebra while
staying calm and familiar for students and teachers. Every style sheet, icon
and template follows this page.

## Principles

- Content first: the graphics view and the algebra input dominate; chrome is
  light, flat and quiet.
- One accent colour for interaction, neutrals for everything else.
- Touch-friendly: interactive targets are at least 40 px on touch layouts and
  32 px with a mouse. Every control has a visible `:focus-visible` ring.
- Works from 320 px phone width to large desktop screens, and in print.

## Colour tokens

Define these once as SCSS variables and CSS custom properties (`--locus-*`).

| Token | Value | Use |
| --- | --- | --- |
| `primary` | `#0e7c86` | buttons, selection, active tool, links, focus ring |
| `primary-dark` | `#0a5c63` | hover and pressed states, text on tints |
| `primary-tint` | `#e2f3f4` | selected rows, active backgrounds |
| `accent` | `#e8743b` | sparing highlights: new object, badges, recording |
| `text` | `#1c2024` | primary text |
| `text-secondary` | `#5b6470` | captions, hints, disabled labels |
| `border` | `#d6dade` | dividers, input borders |
| `surface` | `#ffffff` | panels, dialogs |
| `surface-alt` | `#f4f6f7` | toolbars, headers, zebra rows |
| `scrim` | `rgba(20, 24, 28, 0.45)` | behind modal dialogs |
| `error` | `#c62828` | errors and invalid input |
| `success` | `#2e7d32` | confirmation |
| `warning` | `#b26a00` | exam-mode and caution banners |

## Shape, spacing and elevation

- Spacing scale: 4, 8, 12, 16, 24, 32 px.
- Radius: 8 px for dialogs, cards and popups; 6 px for buttons and inputs;
  full radius for chips and floating action buttons.
- Elevation: popups `0 4px 16px rgba(20,24,28,.16)`; dialogs
  `0 12px 32px rgba(20,24,28,.22)`; nothing else casts a shadow.
- Motion: 150 ms ease-out for hover and small transitions, 220 ms for panels
  sliding; respect `prefers-reduced-motion`.

## Typography

- UI font: **Noto Sans** (SIL OFL 1.1), bundled as woff2, exposed as the font
  family `geogebra-sans-serif` that the Java code requests, with `sans-serif`
  fallback. Serif family `geogebra-serif`: **Noto Serif** (OFL).
- Base size 14 px desktop, 16 px on touch layouts; line height 1.4.
- Headings in dialogs 18 px semibold; captions 12 px.

## Icons

- UI icons (menus, style bar, dialogs): Material Symbols Outlined (Apache 2.0)
  at 24 px, `currentColor` where the code allows, otherwise `#5b6470`.
- Tool icons are drawn for Locus on a 32 x 32 grid, 2 px strokes with round
  caps and joins, few details, readable at 24 px. Object colours:
  - point: filled `#1f4e9c` circle, radius 3, with a 1 px white outline
  - line, segment, ray, vector: `#26303a`
  - circle, conic, arc, curve: `#0e7c86`
  - polygon and region fill: `#0e7c86` at 18 % opacity
  - the object the tool creates or the step it highlights: `#e8743b`
  - measurement text and labels: `#5b6470`
- Every drawn SVG has a `viewBox`, no embedded raster images, no fonts, and
  no scripts. PNG variants are rendered from the SVG, never hand-made.

## Brand

- Name: **Locus**. Wordmark: "Locus" in Noto Sans semibold, `text` colour,
  preceded by the logo mark: a teal circle outline with an orange point on it
  (a point moving on its locus).
- Page footer and About dialog: "Locus is free software under the EUPL 1.2,
  based on the source code of GeoGebra by GeoGebra GmbH
  (https://www.geogebra.org). Locus is not affiliated with or endorsed by
  GeoGebra GmbH."
