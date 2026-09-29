# QA checklist: Graphing, algebra, table of values, spreadsheet tab

Area: `graphing.html` and the same features inside `suite.html`. Tested on
2026-09-25 against the untouched GeoGebra build (reference,
`127.0.0.1:8930`) and Locus (`127.0.0.1:8971`, same `source/web/web/war`),
with Playwright and Chrome at 1400 x 900 (some runs 1600 x 900 or
1400 x 1200) and as a touch phone at 390 x 844. Steps ran through real
clicks, typing and keyboard keys; results were compared through `ggbApplet`
(`evalCommandGetLabels`, `getValueString`, `getCommandString`,
`getObjectType`, `getXML`, `getViewProperties`, `getColor`, `getLineStyle`,
`isTracing`) and screenshots. Console errors and page errors were captured
in every run.

Status: **works** = same result as GeoGebra; **fixed** = was broken or
different, fixed in the named commit; **upstream** = same behaviour or bug in
GeoGebra, left as is; **not testable** = explained.

## Algebra input

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Kernel results for 109 inputs | `evalCommandGetLabels` of polynomials, trig, `If` (two and three branches), implicit curves, inequalities, conics by equation (circle, ellipse, hyperbola, parabola), `Curve`, parametric `(t², t)`, polar `r=2sin(3θ)`, points (cartesian and polar), vectors, lists, `Sequence`, matrices, `Invert`, `Determinant`, `Transpose`, matrix product, `Identity`, text, booleans, `Derivative`, `f'(x)`, `Integral` (indefinite and definite), `Root`, `Roots`, `Extremum`, `InflectionPoint`, `Intersect`, all `Fit*` regression commands, statistics, complex numbers, angles, `Slider`, list commands, `SlopeField`, graphing-restricted commands (`Polygon`, `Solve`, …) and bad input | identical object names, types, values and definitions; the graphing app refuses the same geometry and CAS commands in both | works |
| Typing in the input row | type `f(x)=x^2-3`, `a x+b`, `1/3`, `A=(1,2)` with the physical keyboard | same objects; free parameters `a`, `b` get sliders in the algebra view | works |
| Automatic sliders | `a x+b` | sliders a and b with −5…5 range, play button | works |
| Error message for bad input | type `Root(` and Enter | error tooltip "Wrong number of arguments" with the three syntaxes; GeoGebra also shows a "Help" link to its online manual, which Locus does not have (no manual service) | works (manual link removed on purpose) |
| Command autocomplete | type `Roo` | popup Root, RootList, RootMeanSquare, Roots, ComplexRoot in both; German `Nullst` offers Nullstelle, Nullstellen, … | works |
| Syntax list of a suggestion | click Root in the autocomplete | submenu with the three syntaxes | works |
| Input help | plus button > Help | "Mathematical Functions" and all command categories | works |
| Plus menu | plus button | Expression, Text, Help (same entries) | works |
| Redefining | click a row, edit, Enter | definition updated, dependent objects recomputed | works |
| Deleting | item menu > Delete; style bar Delete | object removed, undo restores it | works |
| Duplicate | item menu > Duplicate Input, Enter | copy created as next free name | works |
| Visibility toggle | click the marble | `getVisible` toggles | works |
| Symbolic/numeric toggle | ≈ button of `1/4` | switches value between 0.25 and 1/4 | works |
| Slider in the row | click the slider track; play button | value set by click; animation runs and stops | works |
| Special points | item menu > Special Points on `x^3-3x` | roots, extrema and y-intercept added as points (6 points, same names) | works |
| Item menu entries | open the three-dot menu of a function, a point | Table of Values, Special Points, Duplicate Input, Delete, Settings; points without the first two | works |
| Item menu > Settings | open | properties sheet with Basic, Style, Advanced, Scripting | works |
| Description modes | Settings > Algebra > Display: Definition and Value, Value, Description, Definition, Linear Notation | same texts per mode; linear notation shows text fields in both | works |
| Auxiliary objects | Settings > Algebra | checkbox present | works |
| Sorting | Settings > Algebra | graphing has no sort option in either app | works (not offered) |
| Drag and drop | drag a row onto another row; drag a row into the graphics view | no reordering in either app; dropping on the view creates a text of the item (the emulated drag also leaves a pen stroke in both) | works |
| Long values | intersection output `(-1.7320508075689, 0)` | Locus broke the number inside its digits because the value row reserved the button column twice | fixed in fc4ec99 |
| App name logo | empty space under the items | unstyled, left aligned; now centred, secondary text, clear of the keyboard button | fixed in fc4ec99 |
| Long definitions | `Roots(f,-10.05,10.05)`, long polynomial | canvas runs under the three-dot button in both | upstream |
| Extra output rows | second and third outputs of `Intersect` | Locus shows a small "=" badge in front (design choice), GeoGebra an invisible spacer | works |

## Virtual keyboard

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Tabs | 123, f(x), ABC, #&¬ | same key sets | works |
| Typing with keys | 2, 𝑥, +, 1, Enter | `f(x) = 2x + 1` | works |
| Greek | ABC > αβγ > α, `=3` | `α = 3` | works |
| More (…) | keyboard more button | opens the input help with all command categories | works |
| Key icons | log_b, 10^x, nroot, d/dx keys | drawn smaller than other key symbols (listed in the integration issues for the icon owner) | open (icons area) |

## Graphics view

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Mouse wheel zoom | wheel in and out at a point | scale 0.0200 → 0.0182 → 0.0200 in both | works |
| Zoom buttons | Zoom In, Zoom Out | view scales about the centre | works |
| Pan | drag empty space with Move | view moves | works |
| Home (standard view) | appears after zoom; click | back to the standard view | works |
| Point dragging | drag A | coordinates follow the mouse | works |
| Rendering of object types | implicit cubic, inequality, ellipse, hyperbola, curve, polar curve, vector, piecewise function, list of points, text | same drawings | works |
| Quick style bar (function) | click the graph | Color, Line Style (with thickness slider), Name, Delete, More | works |
| Quick style bar (point) | click the point | Color, Point Style, Name, Delete, More | works |
| Style changes | pick a colour, dashed line, point style, Show Value | `getColor`, `getLineStyle`, `getPointStyle`, `getLabelStyle` change | works |
| Trace | More > Show Trace, drag the point | `isTracing` true, trace drawn | works |
| Labels | Name popup: Show Label, Show Value | label and value label shown | works |
| Tooltips | hover zoom buttons | tooltip appears to the left after a short rest | works |
| Hidden tooltip boxes | measured scroll containers with and without tooltip boxes | hidden `[data-title]::after` boxes were laid out and made the spreadsheet style bar 30 px taller and 10 px wider than its content | fixed in ebac08d (boxes exist only while hovered, fade-in is an animation) |
| Focus ring on the canvas | click the canvas with the mouse | no ring after a pure mouse click; a ring shows when the last interaction was a key press (browser focus-visible heuristic) | works |
| Graphics settings | gear > Graphics: Grid (type, colour, line style, bold, fixed distance), Axes (colour, line style, label style), Dimensions (ratio, xMin…yMax), x-Axis and y-Axis (label, ticks, distance, numbers, unit, stick to edge, cross at, positive direction, selection), Advanced (background, right angle style, point snapping, object labels) | toggling Grid changes `evSettings grid`; xMin = −3 applied | works |

## Tools (graphing toolbox)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| All 30 tools | select each tool from the Tools tab, click four places in the view | objects created as expected, no console errors | works |
| Input Box, Button dialogs and Table of Values dialog | open the dialog | every focus of an input field without supportive text threw `TypeError … reading 'Uab'` (upstream, also in GeoGebra) | fixed in f1db740 (ComponentInputField) |

## Table of values

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Create from function | item menu > Table of Values, dialog −3…3 step 1 | same table and `TableValuesPoints`; Locus no longer logs the TypeError | fixed in f1db740 |
| Type x values | Table tab, type 1…4 in the x column | x list created | works |
| Data column | type values in the next column | `y_{1}` list and points | works |
| Edit an x value | set first x to 10 | function column recomputed (100) | works |
| Column menus | x: Edit, Clear Column, Import Data, x Statistics; function: Hide Points, Edit, Remove Column; data: Hide Points, Remove Column, y1 Statistics, x y1 Statistics, Regression | same entries | works |
| Points toggle | Hide Points | points removed from the view | works |
| Regression | Regression sheet, models Linear…Logistic, Quadratic, Plot | same parameters (a = 1.0428571428571 …) and R²; Plot creates the list and the fitted function | works |
| Statistics sheets | one- and two-variable statistics | same values | works |
| Side sheet layout | open Regression or Statistics | Locus content sat flush against the sheet edge | fixed in 67e54c0 |
| Remove column, clear column | Remove Column, Clear Column | same results | works |
| Undo after Clear Column | Ctrl+Z | "Opening file failed … FitPoly(RemoveUndefined((x_{2}, y_{1})), 2)" when a plotted regression depends on the column | upstream |

## Spreadsheet tab

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Values and formulas | type 3, 5, `=A1*2`, `=A1+A2` | B1 = 6, B2 = 8 as dependent objects | works |
| Text cells | type `(1,2)`, `hello` without `=` | kept as text in both | works |
| Canvas font | spreadsheet cells | canvas asked for family `mathsans`, which had no face (fell back to the browser default) | fixed in ebac08d (mathsans maps to Noto Sans) |
| Copy/paste | Ctrl+C, select range, Ctrl+V | headless clipboard delivers only the internal marker in both apps | not testable headless |
| Context menu | right click a range | Cut, Copy, Paste, Calculate, Statistics, Create Chart, insert/delete rows and columns | works |
| Calculate | Calculate > Sum on A1:A4 | `A5 = Sum(A1:A4)` = 29 | works |
| Statistics | one- and two-variable, frequency table, regression | sheets with the right values | works |
| Statistics sheet layout | Two-Variable Statistics, Regression | range inputs touched each other | fixed in a7a3dc2 |
| Create chart | Bar Chart from A1:B4 | `BarChart(A1:A4, B1:B4)` drawn | works |
| Insert/delete row | Insert Row Above, Delete Row | references shift; deleting the referenced row leaves `Sum(null:A1)` in both | upstream |
| Style bar | background colour, text colour, bold, italic, alignment, calculate, statistics, chart | bold and italic applied | works |
| Style bar popups | colour and alignment popups | Locus stacked the 28 swatches and the alignment buttons in one tall column | fixed in 06865af |
| Fill by dragging the handle | | not exercised (canvas handle; drag emulation unreliable) | not tested |

## Settings

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Rounding | 2 decimal places, 5 significant figures | `a = 0.33`, then `0.33333`, `f(x) = sin(x) / 3.0000` | works |
| Angle unit | Radian | `α = 0.52360 rad` | works |
| Coordinates | A(x \| y) | A(0.50000 \| 1.4142) | works |
| Font size | 24 pt | algebra and view text larger | works |
| Language | German and back | all visible labels translate, commands show as `Nullstellen`; the axis section titles showed `xAxisTitle` until c133ca7 (strings worker) | works |
| Labeling | | not offered in graphing in either app | works (not offered) |

## Files, undo, export

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Save with the File System Access API | Save to Your Computer, picker stubbed to capture the bytes | valid .ggb (geogebra.xml, defaults, thumbnail) | works |
| Save without the API | same with `showSaveFilePicker` removed | download `Untitled.ggb` | works |
| Open | Open > choose the saved file | same objects, colours, thickness, sliders, text, inequality and spreadsheet cells; XML differs only in view size | works |
| Undo/redo | add objects, `SetColor`, create a table; Undo three times, Redo three times | same states in both | works |
| Export PNG | Export Image > Download | 3000 x 2686 PNG with Noto Sans text | works |
| Download As | .ggb, .png, .svg, .pdf, .stl listed; downloaded .ggb, .svg (text as `geogebra-sans-serif, sans-serif`) and .pdf (embedded font) | works |

## Suite and phone

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Suite, graphing sub-app | `suite.html`: define `f`, item menu > Table of Values, Spreadsheet tab, menu | same rail, table and spreadsheet; menu adds Switch Calculator | works |
| Phone 390 x 844 | tap the input, type `f(x)=x^2-2`, item menu, Table of Values dialog, OK | row, menu, dialog and table fit the screen | works |

## Notes for other areas

- The page preloads `fonts/noto-sans-latin-wght-normal.woff2`, but the face
  arrives with the style sheet the Java injects later, so Chrome sometimes
  warns that the preload was not used within a few seconds.
