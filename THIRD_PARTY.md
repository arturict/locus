# Third-party components

Locus is distributed under the EUPL 1.2 (see `LICENSE`). It builds on the
EUPL 1.2 source code of GeoGebra (see `README.md`) and includes the
third-party components below. Each section names the component, the version,
where it came from, its licence and which Locus files use it. Assets that are
not listed here were made for Locus and are EUPL 1.2.

## Material Symbols (Outlined)

- Version: `@material-symbols/svg-400` 0.47.5 (weight 400, outlined style),
  an unmodified npm packaging of Google's icons by
  <https://github.com/marella/material-symbols>
- Upstream: Google, <https://github.com/google/material-design-icons>
- Licence: Apache License 2.0,
  <https://www.apache.org/licenses/LICENSE-2.0>
- Changes: path data rescaled from the `0 -960 960 960` grid to a 24 x 24
  view box, and the default colour set on the root element so that the app
  can recolour the icon. The drawing is unchanged.
- Used by: 209 user-interface icons under
  `source/shared/common/src/main/resources/org/geogebra/common/icons/`
  (`svg/web/matDesignIcons/**`, `svg/web/keyboard/`, `svg/web/menuIconsTransparent/`
  and the PNG/GIF icons rendered from them under `png/`). Each SVG names its
  source icon in a comment; `tools/icons/sourced-icons.tsv` lists every file
  with its source icon.

## Font Awesome Free

- Version: `@fortawesome/fontawesome-free` 7.3.1
- Upstream: Fonticons, Inc., <https://fontawesome.com>,
  <https://github.com/FortAwesome/Font-Awesome>
- Licence: icons CC BY 4.0, <https://creativecommons.org/licenses/by/4.0/>
  (the package's fonts are SIL OFL 1.1 and its code MIT; Locus uses only icon
  SVGs). Attribution: "Font Awesome Free by Fonticons, Inc., CC BY 4.0".
- Changes: path data fitted into a 24 x 24 view box with a 2 px margin; the
  drawing is unchanged.
- Used by, relative to
  `source/shared/common/src/main/resources/org/geogebra/common/icons/`:
  - `svg/web/matDesignIcons/fontawesome/arrow-rotate-right.svg` (solid/arrow-rotate-right)
  - `svg/web/matDesignIcons/fontawesome/border-none.svg` (solid/border-none)
  - `svg/web/matDesignIcons/fontawesome/copy.svg` (regular/copy)
  - `svg/web/matDesignIcons/fontawesome/pen-line.svg` (solid/pen)
  - `svg/web/matDesignIcons/fontawesome/scissors.svg` (solid/scissors)
  - `svg/web/matDesignIcons/fontawesome/table-rows.svg` (solid/table-list)
  - `svg/web/matDesignIcons/fontawesome/x-2.svg` (solid/subscript)
  - `svg/web/matDesignIcons/fontawesome/x-square.svg` (solid/superscript)
  - `svg/web/matDesignIcons/openFileView/drive_icon_24px.svg` and
    `png/web/open-from-location_googledrive.png` (brands/google-drive)
- The Google Drive mark identifies the Google Drive service; it is a trademark
  of Google LLC and is used only to name that service.

## Noto Sans and Noto Serif (glyph outlines in icons)

- Version: Noto Sans Regular and Noto Serif Italic as shipped in Debian/Ubuntu
  `fonts-noto-core` 20201225
- Upstream: Google, <https://github.com/notofonts/latin-greek-cyrillic>
- Licence: SIL Open Font License 1.1, <https://openfontlicense.org>
- Use: the outlines of a few characters ("2", "1", "10", "log", "lim", "e",
  "d", "dx", "n") are converted to SVG paths inside icons drawn for Locus. The
  SVGs contain no font data and refer to no font.
- Used by, relative to the icon directory above: `svg/web/keyboard/`
  `square.svg`, `inverse.svg`, `e_power.svg`, `ten_power.svg`, `log.svg`,
  `derivative.svg`, `lim.svg`; `svg/web/matDesignIcons/av/`
  `engineering_notation_white.svg`, `fraction_white.svg`;
  `svg/web/menuIconsTransparent/menu_view_graphics2.svg`.

## Noto Sans and Noto Serif

- Version: `@fontsource-variable/noto-sans` 5.3.0 and
  `@fontsource-variable/noto-serif` 5.3.0 (variable weight axis, woff2,
  subsets latin, latin-ext, greek, greek-ext, cyrillic, cyrillic-ext)
- Upstream: The Noto Project Authors,
  <https://github.com/notofonts/latin-greek-cyrillic>
- Licence: SIL Open Font License 1.1, text in
  `source/web/web/src/main/resources/org/geogebra/web/resources/war/fonts/OFL.txt`
- Changes: none; the files are renamed only by their packaging.
- Used by: `war/fonts/noto-sans-*.woff2` and `war/fonts/noto-serif-*.woff2`,
  exposed as the font families `geogebra-sans-serif` and `geogebra-serif`
  in `scss/fonts.scss` and `scss/greek-font.scss`.
