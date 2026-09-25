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

## CodeMirror 6

- Version: `@codemirror/state` 6.7.6, `view` 6.43.13, `commands` 6.11.1,
  `language` 6.12.4, `lang-javascript` 6.2.5, `autocomplete` 6.20.3,
  `lint` 6.9.7; `@lezer/common` 1.5.3, `lr` 1.4.10, `highlight` 1.2.4,
  `javascript` 1.5.5; `style-mod` 4.1.4, `w3c-keyname` 2.2.8, `crelt` 1.0.7,
  `@marijn/find-cluster-break` 1.0.4 (pinned in
  `source/web/codemirror-js/package-lock.json`)
- Upstream: <https://codemirror.net>, <https://github.com/codemirror>
- Licence: MIT
- Used by: `source/web/web/src/main/resources/org/geogebra/web/full/gui/util/locus-codemirror.js`
  (built from `source/web/codemirror-js/`), the script editor.

## QuickJS and quickjs-emscripten

- Version: `quickjs-emscripten-core` and
  `@jitl/quickjs-singlefile-browser-release-sync` 0.32.0; QuickJS 2025-09-13
  (commit f1139494)
- Upstream: <https://github.com/justjake/quickjs-emscripten>,
  <https://bellard.org/quickjs/>
- Licence: MIT (Fabrice Bellard, Charlie Gordon; Jake Teton-Landis)
- Used by: `source/web/web-common/src/main/resources/org/geogebra/web/html5/main/scripting/locus-quickjs.js`
  (built from `source/web/quickjs-js/`), the sandbox for user scripts.

## Carota (design reference)

- Upstream: Daniel Earwicker, <https://github.com/danielearwicker/carota>
- Licence: MIT
- Used by: the design of the rich-text editor in `source/web/richtext-js/`;
  no Carota code is copied.

## esbuild (build tool only)

- Version: 0.28.2; licence MIT; <https://github.com/evanw/esbuild>. Used to
  bundle the three JavaScript libraries above; not shipped.

## Giac

- Version: 70501 (`fr.ujf-grenoble:giac-gwt`, WebAssembly build)
- Upstream: Bernard Parisse and Renée De Graeve, Université Grenoble Alpes,
  <https://www-fourier.univ-grenoble-alpes.fr/~parisse/giac.html>; build
  scripts at <https://github.com/geogebra/giac>
- Licence: GNU GPL 3.0 or later. The GPL 3.0 is a compatible licence under
  Article 5 and the Appendix of the EUPL 1.2.
- Used by: the computer algebra system (`CASgiacW`), loaded as a separate
  WebAssembly module.

## JLaTeXMath and its fonts

- Upstream: JLaTeXMath (Calixte Denizet and others), ported to the web in
  `source/*/renderer-*` as part of the GeoGebra source code
- Licence: GNU GPL 2.0 or later with the classpath-style linking exception
  in `source/shared/renderer-base/LICENSE`; fonts under the licences in
  `source/web/renderer-web/src/main/resources/com/himamis/retex/renderer/web/jlatexmath/public/fonts/licences/`
  (Knuth licence, OFL, dsrom licence)
- Used by: formula rendering.

## three.js

- Version: r92 (`three` 0.92.0 from npm, files unmodified:
  `build/three.min.js` and `examples/js/` `loaders/ColladaLoader.js`,
  `controls/OrbitControls.js`, `renderers/SVGRenderer.js`,
  `renderers/Projector.js`, `exporters/STLExporter.js`)
- Upstream: <https://threejs.org>, <https://github.com/mrdoob/three.js>
- Licence: MIT, copyright three.js authors (the licence text is next to the
  files as `LICENSE`)
- Used by: the 3D "Collada (.html)" export. The files are served from
  `source/web/web/src/main/resources/org/geogebra/web/resources/war/vendor/three/r92/`;
  the app copies them into the exported page (`ThreeJsInliner`), and the
  page falls back to `https://opengebra.arturf.ch/vendor/three/r92/`.
  `FormatColladaHTML` is adapted from a three.js example (MIT).

## Other bundled JavaScript libraries

| Library | Licence | Upstream | File |
| --- | --- | --- | --- |
| PDF.js (`pdfjs-dist` 4.10.38) | Apache 2.0 | <https://github.com/mozilla/pdf.js> | WebJar, Notes PDF import |
| fflate 0.8.2 | MIT | <https://github.com/101arrowz/fflate> | WebJar, `.ggb` zip handling |
| canvas2pdf | MIT | <https://github.com/joshua-gould/canvas2pdf> | `pub/js/canvas2pdf*.js` |
| canvas-to-svg | MIT | <https://github.com/geogebra/canvas-to-svg> | `pub/js/canvas-to-svg.umd.min.js` |
| gifshot | MIT | <https://github.com/yahoo/gifshot> | `pub/js/gifshot.min.js` |
| Whammy | MIT | <https://github.com/antimatter15/whammy> | `pub/js/whammy*.js` |
| MIDI.js | MIT | <https://github.com/mudcube/MIDI.js> | `resources/js/midi/` |
| Roboto, Roboto Serif (font data for PDF export) | Apache 2.0 / OFL 1.1 | <https://github.com/googlefonts> | `pub/js/Roboto*.js` |

## Build-time libraries from GeoGebra's Maven repository

These free libraries are published as patched builds on
`repo.geogebra.net`: `gwt-core` 1.0.1-GGB (Apache 2.0), treblereel
`gwt-widgets`/`gwt-resources` (Apache 2.0), `javacc` 8.0.5-GGB (BSD 3-Clause),
`apache-math-cross-platform` 3.6.3 (Apache 2.0,
<https://github.com/geogebra/apache-math-cross-platform>) and, for tests,
`gwtmockito` 1.1.11-SNAPSHOT (Apache 2.0).
