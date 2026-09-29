# QA: Classic, app-wide features, files, exam mode, accessibility, languages

Area owner: QA worker "app-wide" (Locus on port 8976, GeoGebra reference on
port 8930), 2026-09-25. Every check was driven with Playwright (Chrome,
headless): real clicks, key presses and drags where the feature is
interactive, the `ggbApplet` API for comparisons. Console errors, page
errors and request hosts were captured in every run. "Console clean" means
no error or warning apart from WebGL driver notices in 3D, the font preload
hint and Chrome's `willReadFrequently` canvas hint.

Status: **works** (same result as GeoGebra, or the Locus behaviour
described), **fixed in `<commit>`**, **upstream** (GeoGebra behaves the
same; not changed unless noted), **by design** (Locus changed it on
purpose), **not testable headless** (reason given).

The reference runs with `prerelease=true`; features only visible there are
intentionally off in Locus and were not ported.

## 1. Classic menus

| Feature | How tested | GeoGebra | Locus | Status |
| --- | --- | --- | --- | --- |
| Menu sections | opened the main menu, listed sections | File, Edit, Perspectives, View, Settings, Tools, Help & Feedback, Sign in | same without Sign in | works; Sign in by design |
| File items | expanded File | New, Open, Save online, Save to your computer, Export Image, Share, Download as, Print Preview | New, Open, Save to Your Computer, Export Image, Download As, Print Preview | works; online save/share by design |
| File > New | objects present, clicked New | asks to save | "Do you want to save your changes?" Discard/Save | works |
| File > Open | clicked Open, answered the file chooser | materials browser with "Local file" | native file chooser directly (no online search) | works (by design) |
| File > Save to Your Computer | with File System Access API (picker mocked) and without it | download | picker suggests `Untitled.ggb`, writes a valid zip; without the API the download was `locus-export.ggb` | fixed in `837766f`: every fallback name is the translated Untitled (`Untitled.ggb`, German `Unbenannt.ggb`) |
| File > Download As submenu | opened it | opens left of the menu | opened over the menu and ran off the right edge | fixed in `d755f2f` |
| Download As: ggb, png, svg, pdf, PSTricks, PGF/TikZ, construction protocol html, web page html, Asymptote, Collada dae/html | clicked each, confirmed the dialog, captured the download | files of the same size and header | same size and headers (PNG 452 KB, SVG 19181 B, PDF 42630 B, …); texts say Locus instead of GeoGebra | works |
| Download As: 3D print (.stl) | clicked, dialog with sizes | dialog; no download in headless | same | works (dialog); download not reproducible headless in either app |
| File > Export Image | dialog, Copy to Clipboard and Download | image/png on the clipboard | image/png on the clipboard | works |
| Animated GIF | `exportGIF('a',…)` with a slider | GIF89a, 344 KB | GIF89a, 345 KB | works (no menu entry in either; "TODO add gif back" upstream) |
| Video export | `exportGIF` with a .webm name | writes a GIF | writes a GIF | upstream (no web video export) |
| File > Print Preview | Algebra, Graphics, Construction Protocol, then Print; captured `window.print` and rendered the print media to PDF | dialog with view choice and scale | dialog works; Graphics prints the image; Algebra printed the item buttons as empty boxes; a changed choice printed the previous preview too; caption fields printed as empty boxes | fixed in `cfd2422` and `1ee4fca` |
| Edit items | expanded Edit | Undo, Redo, Graphics View to Clipboard, Copy, Paste, Options, Select All | same | works |
| Edit > Graphics View to Clipboard | clipboard read after the action | image/png | image/png | works |
| Edit > Select All | client listener select events | all objects selected | all objects selected | works |
| Perspectives | clicked each item, compared visible views | Graphing, CAS, Geometry, 3D, Spreadsheet, Probability | same views; also Exam Mode | works; Exam Mode added by design (offline exam enabled on the web) |
| Perspectives popup on start | load classic.html | open | open | works (same as GeoGebra) |
| View items | toggled every item, compared `getPerspectiveXML` | view set per click | identical view sets | works |
| View menu layout | screenshot | icon, check box, label in a row | icon on its own line above each check box | fixed in `79bc5b2` |
| Settings | opened with all views visible, every tab | General, Algebra, Graphics, Graphics 2, 3D Graphics, Spreadsheet, CAS | same tabs and same controls | works |
| Tools > Customize Toolbar | opened; expanded a group; dragged "Move Graphics View" to the Tools list; Apply | works, toolbar loses the tool | worked, but the screen was unstyled (icons piled up, Tools list off screen) | fixed in `50c212b` (also phone layout) |
| Tools > Create New Tool | output M = Midpoint(sg), inputs A, B, name "Mid", Finish, then `Mid((0,0),(2,4))` | works; console TypeError "reading 'Uab'" | works, console clean | works (upstream console error) |
| Tools > Manage Tools | opened with the tool loaded | list, open/save, name, icon | same | works |
| Tool dialogs accessibility | name scan | up/down/delete buttons and lists without names | same | fixed in `1b78710` |
| Help and Feedback | expanded | Tutorials, Manual, Help, Report problem, About, Privacy | Report a Problem (opens the Locus issue tracker; was "Report a Bug" unlike the other apps), About and License | works; wording unified in `1e06e1e`; online help by design |
| Classic header buttons | name scan, keyboard | Open and Menu buttons without names; Enter on Menu toggles twice so it never opens | same | fixed in `9b17e3e` |

## 2. Views, docking, input bar

| Feature | How tested | GeoGebra | Locus | Status |
| --- | --- | --- | --- | --- |
| Rearranging views | View menu open, dragged the graphics view's handle onto the left side | glass pane, views swap (1@3, 2@1) | the handle ignored the press (floating title bar had pointer events off), nothing happened | fixed in `b7689cc`, now swaps like GeoGebra |
| Closing views | style bar toggle, looked for close buttons | none in the title bars (View menu closes) | same | works |
| Undocking into windows | — | not available on the web | not available | upstream (desktop only) |
| Input bar (View > Input Bar) | typed `P=(1,2)` in the bottom bar | object created | object created | works |
| Command suggestions | typed "Circ" | popup with Circle syntaxes above the bar | popup appeared, but the splitter line ran across it and items had a 40 px indent | fixed in `c4104cd` |
| Input help | clicked the ? button | help panel with function list and command categories | same, Locus wording | works |
| Narrow algebra view | all views open, Algebra about 115 px wide | text clipped on one line | text wrapped character by character | fixed in `adea328` and `c4416a9` (see section 12) |

## 3. Keyboard shortcuts (Classic)

Harness: construction A=(1,1), B=(3,2), c=Circle(A,B), f(x)=x²/4, checkbox;
each case reset with `setXML`; selection tracked with a client listener.
Compared objects, selection, mode, visible views, view scale, font size,
algebra style and input bar content.

| Keys | Result (both apps) | Status |
| --- | --- | --- |
| Ctrl+A | selects all | works |
| Delete, Backspace on A | deletes A and c | works |
| Ctrl+Z, Ctrl+Shift+Z | undo, redo | works |
| Ctrl+Y after Ctrl+Z | redoes in Locus; the reference did not redo in the headless run | works (Locus correct) |
| Ctrl+C, Ctrl+V | pastes a copy (A_{1}) | works |
| Ctrl+X | cuts | works |
| Arrow keys on A | ±0.1; Shift ±0.01; Alt ±1; Ctrl moves nothing | works (identical) |
| Escape | back to Move | works |
| F3, F4, F5 on A | definition, value, name into the input bar | works |
| Ctrl+Plus / Ctrl+Minus / Ctrl+M | zoom in, zoom out, standard view | works |
| Ctrl+E | object properties | works |
| Ctrl+G, Ctrl+H | hide object / label | works |
| Ctrl+D | algebra description mode 3 → 0 | works |
| Ctrl+1, Ctrl+2 | font size 12 / 20 | works |
| Ctrl+Shift+A, Ctrl+Shift+1, Ctrl+Shift+L | toggle Algebra, Graphics, Construction Protocol | works |
| Ctrl+Shift+S, 2, 3, P, K, Ctrl+P, Ctrl+R, Ctrl+F, Ctrl+Shift+D | same (partly no visible effect in headless) in both | works (identical) |
| Ctrl+I | inverts the selection | works |
| Tab in graphics | selects the next object | works |
| Enter | focuses the input bar | works |
| Alt+letters in the input | α Α β δ Δ ℯ ϕ γ ί λ μ ν ° π Π sqrt() σ θ ∞ ω ^(2) € ⊕ | identical in both | works |

## 4. File compatibility

| Construction | How tested | Result | Status |
| --- | --- | --- | --- |
| Classic 2D/3D/spreadsheet/scripts: points, circle, polygon, functions, slider, texts, checkbox, list, A1:B1 cells with Sum, sphere, plane, If function, vector, angle, button, input box, segment, caption, colour, thickness, filling, an onUpdate GeoGebra script and a JavaScript click script | built in both; `getBase64` → `setBase64` both ways and through the Open dialog; compared `getXML` | XML identical except window size; scripts run after loading (b = 6 after a = 3) | works |
| CAS app cells (Solve, f(x):=…, Derivative, Integral, Factor) | typed into the CAS view of both, cross-loaded | identical build XML; loading adds the same `symbolic`/arbitrary constant elements in both | works |
| Notes: rich text (bold, italic), table with cell text, pen stroke | made with the tools in both, cross-loaded, rendered | content round-trips, renders in both | works |
| Custom tool (Mid) | created through the dialog in each app, file opened in the other; `Mid((10,0),(0,10))` | macro present, command gives (5, 5), tool button shown | works |
| CSV import | Open dialog with a 2-column CSV | same cells (A1(x)=x from the header row, as in GeoGebra) | works (upstream quirk) |
| Default object names | created each kind in English and German | Locus used inputBox/textfield, penStroke, locus and German Stiftstrich, poly, Richtungsfeld; GeoGebra uses InputBox, stroke, loc, Strich, Vieleck, Steigungsfeld | fixed in `5f8740e` |

## 5. Embedding and the ggbApplet API

| Feature | How tested | Result | Status |
| --- | --- | --- | --- |
| API surface | one script calling about 70 functions in both apps: evalCommandGetLabels, getValue, setCoords, colour/line/point/label/layer/fixed/trace setters and getters, renameObject, getCommandString, getLaTeXString, sliders, setTextValue, setListValue, setMode, getToolName, axes/grid, setCoordSystem, getViewProperties, getGraphicsOptions(1), rounding, getPNGBase64, exportSVG/PDF/PGF/PSTricks/Asymptote, exportConstruction, construction steps, getXML/getAlgorithmXML/evalXML/setXML, undo/redo, getBase64, setPerspective, isSaved/setSaved, getFileJSON, evalCommandCAS, asyncEvalCommandGetLabels, newConstruction | identical results; both log the same "reading 'call'" TypeError | works |
| Listeners | add, remove, rename, update, clear, client, object update | same events in both | works |
| evalCommand before any user input | `evalCommand('Circle(…)')` right after load | fails in both ("… commands not loaded yet"/Unknown command) until the command modules load | upstream |
| evalCommand with German names | `evalCommand('Kreis(…)')` after switching to German | rejected in both: the API looks commands up by internal (English) name | upstream (by design) |
| HTML export embed | exported "Dynamic Worksheet as Webpage", served it from another origin (port 8977) | the page stayed empty: code chunks (XHR) and fonts were blocked by CORS; with CORS headers the worksheet loads with all objects | fixed in `8298859` (`_headers`: `Access-Control-Allow-Origin: *`), narrowed to the asset paths in `4ea4d5a` (section 12); live check needs the deployment |

## 6. Exam mode

| Feature | How tested | Result | Status |
| --- | --- | --- | --- |
| Offered in | menus of all apps | Classic (Perspectives), Graphing, Geometry, 3D, CAS, Suite (with exam types). Standalone Scientific and Notes have none; the reference offers it there only through a Safe Exam Browser launch URL | by design (Scientific via the Suite) |
| Start dialog | Classic: CAS/3D choice; others: notice; Suite: exam type list | works | works |
| Timer panel | header-less pages float `.examPanelStandalone` | styled from an inline style in Java | fixed in `dad3c0a` (exam.scss) |
| Leaving and returning | visibilitychange/blur and back | log shows "Left the exam" / "Returned"; rail or Classic bar turns red | works |
| Icons on the red/green bar | screenshots | Classic info/undo/menu icons and the rail menu icon were dark on red/green | fixed in `9b17e3e` (Classic, style in `_toolbar.scss`) and `a0b66bb` (rail) |
| Exam log | info button / Exam Log item | log dialog with date, times, activity | works; Escape does not close it (same code as GeoGebra) |
| Ending the exam | End Exam → confirm → summary → Exit | works in Classic, Graphing, Geometry, 3D, CAS, Suite | works |
| Menu button after the exam | reopened the menu four times | a second, stale Menu button stayed in the frame under the new one (two focusable Menu buttons; clicking the first match fails) | fixed in `dad3c0a` |
| Full screen during the exam | — | `requestFullscreen` needs a user gesture | not testable headless |

## 7. Accessibility

| Feature | How tested | Result | Status |
| --- | --- | --- | --- |
| Names of controls | scan of buttons, links, inputs, selects, role elements in every app at start, in every Classic menu section and in the Export, Print, tool and About dialogs: empty names or raw keys | no empty names or raw keys left (after the fixes above); drop-downs without a label no longer start with a space (`1b78710`) | works |
| Notes ruler button | aria-label | "Ruler. Show a ruler to measure lengths…" (GeoGebra: " Help") | works (fixed earlier in `1fd1f49`) |
| Tab order | Tab 22 times in Graphing | Menu → Settings → zoom buttons → input, cycling, same order as GeoGebra | works |
| Focus rings | keyboard focus vs mouse click on canvas, zoom and menu buttons in four apps | ring on keyboard focus only | works |
| Escape | main menu, graphics settings, context menu, algebra item menu, Export dialog | popups and dialogs close; the main menu stays open in both | works |
| Keyboard in Classic header | Enter on Menu | did not open | fixed in `9b17e3e` |

## 8. Languages

| Feature | How tested | Result | Status |
| --- | --- | --- | --- |
| Offered languages | Settings > Language | English (US), German / Deutsch | works |
| Browser language | locale de-CH / de-DE | apps start in German (GeoGebra's reference stays English) | works |
| Runtime switch | Settings drop-down and `setLanguage('de')`, then typing Kreis/Ableitung in Classic, Graphing, Suite, 3D (Kugel), CAS | German commands work in every flow, also when English was used first | works (coordinator's report reproduced only through the API, see section 5) |
| German UI | Classic menus, tools, perspectives popup, error message for `Kreis(1,2,3,4,5)` | German throughout ("Befehl Kreis: Falsche Anzahl Argumente: 5", syntax list) | works |
| Circle in Graphing | typed Circle/Kreis in Graphing | "Unknown command" in both: Graphing excludes the conic commands | upstream (by design) |

## 9. Landing page

| Feature | How tested | Result | Status |
| --- | --- | --- | --- |
| Links | every link on index.html | all app pages, CSS and favicon return 200 | works |
| Responsive layout | 1400, 768, 390, 360, 320 px | no horizontal scrolling, cards reflow to two columns | works |
| Keyboard | Tab through the page | every link reachable with a 2 px focus ring | works |
| Attribution footer | text | EUPL note, GeoGebra origin, non-affiliation, fonts | works; source code and issue links added in `1485162` |

## 10. Phone and tablet layouts

| Feature | How tested | Result | Status |
| --- | --- | --- | --- |
| All eight apps at 390×844, 360×740, 768×1024 (touch) | scan for controls outside the viewport and page scrolling; screenshots | nothing off screen (GeoGebra's Notes has two buttons off screen at 390 px) | works |
| Fullscreen button with the sheet open | 3D and Graphing at 390 px, Tools sheet | covered "Net" and "Best Fit Line" in the sheet's corner | fixed in `2d86e46` (button at the end of the sheet's tab row; checked at 360 and 768 px) |
| Classic menu and Customize Toolbar on phones | 390×844 | menu scrolls; toolbar editor one column | works (after `50c212b`) |

## 11. Network

Every flow above logged request hosts. Locus requested only its own origin
(`127.0.0.1:8976`, plus `blob:` URLs for exports) in all apps, including a
sweep that opened every app, its menu, Settings and About. The reference
contacts `www.geogebra.org`. User-initiated links (Report a Bug, licence,
source code) open external sites by choice.

## Open items for other areas

- Deployment: confirm `Access-Control-Allow-Origin` is served by the live
  site so exported worksheets load from other domains.

## 12. Polish pass (leftovers from all areas)

Worker "polish" (Locus on port 8977, reference on 8930), 2026-09-25 to
2026-09-29. Same method as above; every run captured console errors,
page errors and failed requests.

| Item | How tested | GeoGebra | Locus before | Locus now | Status |
| --- | --- | --- | --- | --- | --- |
| Very narrow Classic algebra view | perspective ACGSL, algebra splitter dragged to 113 px; points, A₁, list, text, slider, function | one line, clipped under the item button | plain values one character per line, texts too, "Inpu / t…" placeholder on two lines | plain values stay on one line and scroll sideways (like the value row); texts wrap between words only; placeholder clipped on one line. Graphing at 390 px rechecked: intersection values (commit 96a76be) unchanged, long lists now one scrollable line as in GeoGebra | fixed in `adea328`, `c4416a9` |
| Classic probability view at narrow width | perspective AGB at 1440, 900 and 700 px wide, Normal and Binomial; perspective B at 390 px | plot plus table | — | plot visible at every width, table at its natural width | works (after `2ac0753`) |
| Default file name | Classic File > Save to Your Computer without the File System Access API, English and German | `geogebra-export.ggb` vs picker `Untitled.ggb` | `locus-export.ggb` vs picker `Untitled.ggb` | `Untitled.ggb` / `Unbenannt.ggb`; image, SVG, PDF, tool and probability exports use the same fallback (`App.getExportTitle`), as do the save and exam dialogs | fixed in `837766f` |
| Classic Help menu wording | opened Help in English and German | Report problem | Report a Bug | Report a Problem / Problem melden, like the other apps | fixed in `1e06e1e` |
| Phone fullscreen button in CAS | cas.html at 390×844, touch: clicked the input, typed `1/3+1/4` and `sqrt(8)` with Enter, then closed the keyboard; also Graphing | button on the tab bar at the bottom | with the keyboard open the sheet hides its tab row, so the button sat on the first row over its ≈ button | button hidden while the tab row is hidden, back in the tab row when the keyboard closes (Graphing the same) | fixed in `969961b` |
| German short statistics commands | typed in Graphing (German): Mittelwert, Standardabweichung, StichprobenStandardabweichung, MAD, the new names and English `mean`; compared the definition, `getCommandString(…, false)` and the XML; English rerun | Mittelwert shows as `Mittel(…)`, the other three stay English | `mean(…)`, `stdevp(…)`, `stdev(…)`, `mad(…)` | German: `mittel`, `stabwn` (population SD), `stabw` (sample SD), `mittelabw`; English unchanged; the XML keeps `mean`, `stdevp`, `stdev`, `mad`; English names still accepted in German. No new name collides (case-insensitive) with another German command. `:common-jre:test --tests '*Localization*' --tests '*Autocomplete*' --rerun` passes | fixed in `f3f7591` |
| Special symbol picker (ByDS fonts) | Notes: text with a ByDS font (set through `evalXML`), selected, opened Special Characters, English and German | — | group and symbol names hard-coded German | English: Basic Characters, Difficulty Levels, Puzzle, Worm, House, Left …; German unchanged (Basiszeichen, Differenzierung, …) | fixed in `74d9fcc` |
| Standalone editor label | code review; the editor module is not part of the SuperWeb build | — | hard-coded "Enter your equation or expression here" | key `EnterExpression` through the editor's localization (English fallback, since that module loads no bundle) | fixed in `74d9fcc` |
| Notes ellipse shape help | aria label of the Ellipse shape button | — | — | "Ellipse. Drag in the view to draw an ellipse." (`ShapeEllipse.Help` via `getHelpTransKey`) | works (`1fd1f49`) |
| Font preload warning | loaded all nine pages, waited 8 s, filtered console warnings | — | "preloaded but not used" | no preload warning on any page | works |
| CORS scope in `_headers` | read the rules; served the war with a server that applies `_headers` (all matching rules, as on Cloudflare Pages / Netlify) and loaded an exported worksheet from another origin | — | `Access-Control-Allow-Origin: *` on every path including the pages | only `/web3d/*`, `/css/*`, `/fonts/*`, `/vendor/*`; no `Allow-Credentials`; pages get no CORS header; the worksheet loads with all objects and fonts | fixed in `4ea4d5a`; live check needs the deployment |
| Final sweep | `index.html` and the eight apps at 1440×900 and 390×844 (touch), screenshots reviewed | — | — | every page renders; no console errors or warnings (apart from WebGL notices), no page errors, no failed or 4xx requests | works |

Stale evidence elsewhere: `graphing.md`, `geometry.md` and `cas-stats.md`
still name `locus-export.*` downloads; since `837766f` those files are
called `Untitled.*` (`Unbenannt.*` in German).
