# Locus script editor

[CodeMirror 6](https://codemirror.net) (MIT) with JavaScript highlighting,
line numbers and undo history, behind the global `window.GeoGebraCodeMirror`
that `CodeMirrorEditorWidget` (button dialog script area) calls:
`createEditor(element, {value, onChange})` returns an object with `destroy`,
`focus`, `getValue`, `setValue`, `refresh`, `getCursorPosition`,
`setCursorPosition`, `replaceText` and `getCursorPixelPosition`.
It replaces GeoGebra's closed `org.codemirror:editor` bundle.

```sh
npm ci
npm run build   # writes ../web/src/main/resources/org/geogebra/web/full/gui/util/locus-codemirror.js
npm test        # runs the committed bundle in jsdom
npm run check   # fails if the committed bundle does not match the sources
```

Versions are pinned in `package.json` and `package-lock.json`; the same lock
file gives the same bundle. The bundle is committed and embedded by
`ScriptEditorResources`, so the Gradle build does not need Node.
