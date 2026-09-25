# Locus JavaScript sandbox

[QuickJS](https://bellard.org/quickjs/) (MIT, Fabrice Bellard and Charlie
Gordon) compiled to WebAssembly by
[quickjs-emscripten](https://github.com/justjake/quickjs-emscripten) (MIT,
Jake Teton-Landis). User scripts (button scripts, update scripts, global
JavaScript) run in it when `AppletParameters.getParamSandbox()` is true, which
is the default for the Locus app pages. It replaces GeoGebra's closed
`org.quickjs:emscripten` bundle.

The bundle defines `window.QJS.getQuickJS()`, which resolves to an object whose
`newContext()` returns a quickjs-emscripten `QuickJSContext`, the API used by
`org.geogebra.web.html5.main.scripting.QuickJS`. Locus adds one thing: a script
(including what it calls) is interrupted after 10 seconds, so an endless loop
cannot freeze the page.

The WebAssembly binary comes prebuilt from the npm package
`@jitl/quickjs-singlefile-browser-release-sync`; it is built from the QuickJS
sources vendored in the quickjs-emscripten repository (see its `README.md`
for the QuickJS commit and the Emscripten flags).

```sh
npm ci
npm run build   # writes ../web-common/src/main/resources/org/geogebra/web/html5/main/scripting/locus-quickjs.js
npm test        # runs the committed bundle in node
npm run check   # fails if the committed bundle does not match the sources
```
