# QA checklist: Notes

Area: `notes.html` (Notes whiteboard). Tested on 2026-09-25 against the
untouched GeoGebra build (reference, `127.0.0.1:8930`) and Locus
(`127.0.0.1:8975`, same `source/web/web/war`), with Playwright and Chrome,
1440 x 900 desktop, 820 x 1180 touch tablet and 390 x 844 touch phone.
Steps were run through real clicks, drags and typing; results were compared
through `ggbApplet` (`getXML`, `getBase64`/`setBase64`, `getAllObjectNames`,
`getMode`) and screenshots. Console errors were captured in every run.

Status: **works** = same result as GeoGebra; **fixed** = was broken or
different, fixed in the named commit; **upstream** = same behaviour or bug in
GeoGebra, left as is; **not testable** = explained.

## Toolbox

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Toolbox buttons | list buttons and aria labels | same nine buttons (select, pen, shape, text, upload, link, more, ruler, spotlight) | works |
| Tool button aria labels | read `aria-label` of popup tools | both said " Drag in the view ..." (tool name cut off at the first dot because the translated label was looked up as a key); ruler said " Help" / " Show a ruler ..." | fixed in 1fd1f49 (ToolIconButton, RulerIconButton) |
| Pen | pen popup, draw a stroke | identical stroke XML (`strokeBezierCoords`) | works |
| Pen colours | pick 4th swatch, draw | colour `#1565C0` saved | works |
| Pen colour layout | open pen popup | Locus showed 6 + 4 swatches with the custom button in the second row, GeoGebra 5 + 5 | fixed in 1e20c2f |
| Pen thickness | slider to 20, draw | thickness 20 saved, value shown | works |
| Highlighter | highlighter, draw | thickness 40, opacity 77, same XML | works |
| Eraser | eraser, drag across strokes | strokes split at the eraser path; first drag after opening the popup only closes it (same in GeoGebra) | works |
| Shapes | rectangle, square, parallelogram, stadium, triangle, circle, ellipse, pentagon, line, curve, freeform (clicks), mask | same object types and labels in both | works |
| Ellipse shape help | aria label of the ellipse tool | both said "Select two foci, then a point on the ellipse" (key shared with the classic Ellipse tool) | fixed in 1fd1f49: own `ShapeEllipse.Help` key (EuclidianConstants.getHelpTransKey) |
| Shape quick style bar | select a rectangle | colour, filling, line style, delete, more; same functions | works |
| Colour popup layout | open colour of a shape | Locus wrapped 28 swatches in rows of 8 with the custom button mid-row | fixed in 1e20c2f (rows of 7) |
| Filling | apply each of the 5 fill types | `fillType` 0, 1, 4, 2, 5 in both | works |
| Line style / thickness | line style popup | 5 dash styles + thickness slider | works |
| Select / move | click, drag | same | works |
| Rubber-band selection | drag around two shapes | both selected, style bar shows group actions | works |
| Text box | text tool, click, type | `inlinetext` with same content | works |
| Bold / italic / underline | style bar buttons and Ctrl+B/I/U | `bold`, `italic`, `underline` runs identical | works |
| Text colour | style bar colour | `color` rgba identical | works |
| Font size | size field, type 28 | `size: 28`; suggestion list 12 ... 120 | works |
| Font | font menu, Comic Sans | same eight fonts, `font` value identical | works |
| Alignment | horizontal (left, centre, right), vertical (top, middle, bottom) | `align`, `verticalAlign` identical | works |
| Background colour, border | style bar | `bgColor`, `borderColor` identical | works |
| Border thickness popup | text and table border popup | Locus showed no line previews and a check mark on both rows | fixed in 78a4e70 |
| Subscript / superscript | context menu toolbar in edit mode | `script: sub/super` identical | works |
| Bullet / numbered list | context menu toolbar | `listStart`/`listEnd` runs, toggle off restores plain text | works |
| Strikethrough | looked for a control | GeoGebra Notes has none in the UI either | works (not offered) |
| Hyperlink | More > Link, text + URL | link run with `url`; link colour is Locus teal `#0E7C86` instead of blue (design) | works |
| Copy/paste inside text | Ctrl+A, Ctrl+C, End, Enter, Ctrl+V | formatting kept (bold run pasted as bold) | works |
| Paste from outside | clipboard text with a newline | inserted as two lines; Ctrl+Z undoes it | works |
| Keyboard editing | Ctrl+Left, Backspace, Shift+Right, Home/End, Up, Ctrl+Home, Delete | identical resulting text | works |
| Equation | equation tool, type `x^2/3+sqrt(y)` | same `formula` content | works |
| Virtual keyboard over equation | equation near the bottom, keyboard open (desktop and touch tablet) | the keyboard covers the equation in GeoGebra too; no view shift exists in the Java code | upstream (matches GeoGebra) |
| Keyboard icons log_b, 10^x, n-th root, d/dx | f(x) tab | drawn at half the size of neighbouring keys | fixed in 0a93c90 (tools/icons/drawn.py, regenerated); checked in the rebuilt app, they now match the e^x and root keys |
| Table | table tool, type, Tab | Locus moves to the next cell on Tab, GeoGebra leaves the cell | works (Locus rich text editor; better than reference) |
| Table rows/columns | context menu insert above/below/left/right, delete row/column | 3 x 3 result in both | works |
| Table cell background | style bar background | `bgcolor` per cell identical | works |
| Table borders | all/inner/outer/clear, thin/thick | `vborders`/`hborders` identical | works |
| Wrapping, rotation, heading | context submenus | same options and keys; heading colour is Locus teal (design) | works |
| Long cell text | type a sentence into a 100 px cell | Locus wraps it and grows the row (84 px); the reference keeps 36 px and cuts the wrapped lines off; after "Clip" or "Rotate up" both clip | difference in the replacement rich text editor (Locus shows all text); file format unaffected |
| Create chart | context menu of a table | entry present in both | works (not further tested) |
| Mind map | mind map tool, type, "+" on the right | child with `parent align="RIGHT"` in both | works |
| Mind map move | drag a child | position changes, parent link kept | works |
| Image upload | Upload > Image, local PNG | image object, style bar opacity/crop/delete/more | works |
| Image opacity, crop | opacity 50 %, crop handle drag | `alpha 0.5`, `cropBox cropped="true"` | works |
| PDF upload | Upload > PDF, 3-page PDF | preview, page field "of 3", next page, insert page 2 | works |
| Camera | Upload > Camera | needs a webcam | not testable headless |
| Web page embed | Link > Web Page, URL, Insert | `embed` object | works |
| Web page dialog hint | open the dialog | hint text touched the field | fixed in 43fb0ce |
| Video embed | YouTube URL | `video` object (thumbnail blocked offline in both) | works |
| Audio embed | MP3 URL | "Please check your input" in both (URL not reachable offline) | not testable offline |
| Apps menu | More > Locus > Graphing, 3D, Geometry, CAS, Probability, Scientific | every app embeds and runs; typed `f(x)=x^2` into the graphing embed and it plots | works |
| Ruler | ruler button | ruler appears; pen strokes snap to its edge (identical stroke XML) | works |
| Ruler scale | compare ticks with the "Squared (1 cm)" ruling | Locus ruler and triangle used 40 px per cm, the page ruling and GeoGebra use 50 px | fixed in 1805d82 |
| Protractor | ruler popup > Protractor | shown, own Locus artwork | works |
| Spotlight | spotlight button on/off | dims the view, `spotlight` circle, removed when toggled off | works |
| Laser pointer | looked for it | not in GeoGebra's Notes toolbox either | works (not offered) |
| Sticky notes | looked for it | not in GeoGebra's Notes either | works (not offered) |

## Pages

| Feature | Steps | Result | Status |
| --- | --- | --- | --- |
| Page overview | top bar button | panel with previews | works |
| Add page | plus button twice | 3 pages, previews show content | works |
| Duplicate page | card menu > Duplicate Page | copy inserted after | works |
| Delete page | card menu > Delete | removed | works |
| Rename | card menu > Rename | title shown on the card | works |
| Reorder by drag | drag card 3 above card 1 | order and previews updated, same as GeoGebra | works |
| Card menu at the right edge | open card menu | menu is cut off at the window edge in both | upstream |
| Rulings | settings > Ruling, all 12 | every ruling draws; Squared (1 cm) is 50 px | works |
| Background colour | settings > Background Color | present | works |

## Selection, editing, undo

| Feature | Result | Status |
| --- | --- | --- |
| Group / ungroup | `<group l0 l1/>` written and removed | works |
| Order (bring to front etc.) | `ordering` changes | works |
| Copy / paste object | `q1_{1}` created | works |
| Fix object | `<fixed val="true"/>` | works |
| Undo / redo (Ctrl+Z / Ctrl+Y) | restores and reapplies | works |
| Context menus | same entries for shapes, text, tables, pages | works |
| Clicking a selected object again | hides the style bar in both | upstream behaviour |
| `newConstruction()` keeps an embedded app | same in GeoGebra | upstream |

## Files and export

| Feature | Steps | Result | Status |
| --- | --- | --- | --- |
| Save/open round trip | 3 pages with text (bold, italic, two lines), table with cell colour, mind map, equation; `getBase64` > `setBase64` > `getBase64` | the rich page XML is byte-identical; only the view size of another page changed because the page panel was open | works |
| Locus file in GeoGebra | load the same file in the reference | page XML identical after GeoGebra re-saves it; renders the same | works |
| GeoGebra file in Locus | GeoGebra table with clip, rotation, heading, borders and a formatted text | loads and renders; Locus re-serialises table JSON with explicit `null`s and a different key order, which GeoGebra reads back unchanged | works |
| Export Image | menu > Export Image > Download | PNG downloaded | works |
| Download As | .ggs, PNG, SVG, PDF | all four files valid; PDF has one page per Notes page | works |
| PDF table borders | export a page with a coloured cell | borders take the cell colour in both | upstream (canvas2pdf) |
| Print Preview | menu | dialog with scale in cm | works; printing itself not testable headless |
| Exam Mode entry | main menu | GeoGebra Notes shows it through its exam-launch URL (Safe Exam Browser on geogebra.org); Locus has no such service | removed on purpose |

## Layouts

| Layout | Result | Status |
| --- | --- | --- |
| Desktop 1440 x 900 | as above | works |
| Tablet 820 x 1180 touch | toolbox, text, style bar | works |
| Phone 390 x 844 touch | the top bar overflows; the page overview button was scrolled out of view | fixed in 7056442 (pinned to the right edge like GeoGebra) |
| Top bar dividers | sat at the top edge instead of centred | fixed in 7056442 |
| Phone shape popup | 3 columns (touch-size buttons) instead of 4 | works (fits) |
| German (de-CH browser) | toolbox, popups, style bar, context menus, page menu | all translated except Undo/Redo in the top bar (created before the bundle loads, never relabelled) and the Notes table named "Wertetabelle" | fixed: Undo/Redo in NotesTopBar (75be1ca), table in affc24b |

## Console

`TypeError: Cannot read properties of undefined` from
`ComponentInputField` (support label handler) appears in both apps when a
dialog input gains or loses focus; another worker has an uncommitted fix in
`ComponentInputField.java`. `ExtGState 'Alpha-1' is unknown` warnings in
exported PDFs come from canvas2pdf. No other console errors in Notes.
