# Locus rich text editor

Canvas-based rich text and table editor used by text boxes, mind map nodes and
tables in Notes and the graphics view. It replaces GeoGebra's closed-source
`org.murok:editor` bundle and implements the API that the Java classes in
`source/web/carota-web` (`org.geogebra.web.richtext.impl.Carota*`) call, as
`window.murok`.

The design follows [Carota](https://github.com/danielearwicker/carota) by
Daniel Earwicker (MIT): documents are lists of formatted runs, lists are the
inline codes `{"$": "listStart"}`, `{"$": "listNext"}` and `{"$": "listEnd"}`.
The code here is written for Locus (EUPL 1.2).

## Content format

A text is a JSON array of runs, the form stored in the `<content val="...">`
element of `.ggb` files:

```json
[{"text": "Bold ", "bold": true}, {"text": "link", "url": "https://example.org",
  "color": "#0E7C86", "underline": true}, {"text": "\n"}]
```

Formatting keys, in the order they are saved: `size`, `font`, `color`,
`bgcolor`, `bold`, `italic`, `underline`, `strikeout`, `align`, `script`
(`super`, `sub`, `normal`, `none`), `url`. Values that equal the defaults are
left out. A document always ends with `\n` (or with `listEnd`); that final
newline takes the formatting of the character before it. Tables are described
at the top of `src/table.js`.

## Build and test

```sh
npm ci
npm test          # node unit tests (model, layout, tables, file compatibility)
npm run build     # writes ../carota-web/src/main/resources/org/geogebra/web/richtext/impl/locus-richtext.js
npm run check     # fails if the committed bundle does not match the sources
```

The Gradle build does not run Node: the bundle is committed next to its
sources and embedded by `RichTextResources`. Rebuild and commit it whenever
`src/` changes.
