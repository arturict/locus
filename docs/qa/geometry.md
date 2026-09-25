# QA checklist: 2D tools, object properties, construction protocol, custom tools

Area: every 2D tool and object feature in `geometry.html` and `classic.html`.
Tested on 2026-09-25 against the untouched GeoGebra build (reference,
`127.0.0.1:8930`) and Locus (`127.0.0.1:8972`, the shared
`source/web/web/war`), with Playwright and Chrome at 1440 x 900 (some runs
1440 x 1000/1100 or 1600 x 900) and as a touch phone at 390 x 844.

Method: tools were chosen through the UI (Tools panel with "More Tools",
Classic toolbar groups) and through `ggbApplet.setMode`, and constructions
were made with real mouse clicks and drags at canvas positions computed from
`getViewProperties` after `setCoordSystem(-10, 10, -6, 6)`, so both apps
received the same clicks in world coordinates. Results were compared through
`getAllObjectNames`, `getObjectType`, `getCommandString`, `getValueString`,
`getVisible`, `getColor`, `getLabelVisible`, `getXML` and screenshots. Every
run captured console errors and page errors; "console clean" means none
(the reference itself logs `TypeError … 'Uab'` whenever an input dialog
opens; that upstream bug in `ComponentInputField.addSupportiveTextLabel` was
fixed in Locus by another worker before these runs).

Status: **works** = same result as GeoGebra; **fixed in `<commit>`** = was
broken or different, fixed; **upstream** = GeoGebra behaves the same;
**by design** = Locus differs on purpose; **not testable headless** = reason
given. Locus strings are its own, so tool names and help texts are compared
for meaning and correctness, not wording.

## Tool lists and help texts

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Geometry Tools panel | open Tools, "More Tools"; list every `.toolButton` with its mode and aria label | same 39 buttons, same modes in the same order and categories | works |
| Geometry tool selection | click each of the 33 distinct tool buttons; read `getMode()` and the tool tip | every button selects its mode and shows "name / help"; Image opens the upload dialog at once in both | works |
| Classic toolbar groups | open each of the 11 groups, list `li[mode]` | identical groups and order (Move/Freehand/Pen; 8 point tools; 7 line tools; 8 special lines; 4 polygons; 9 circle tools; 4 conics; 8 measurement tools; 6 transformations; 6 action objects; 7 general tools) | works |
| Classic tool tips | select every tool from its group; read the snackbar | all 71 tools show their name and a help text, no raw keys; German (`?lang=de`) complete as well. GeoGebra adds a "Help" link to its online manual, Locus has no manual | works |
| Image tool help | select Image | the help asked to click in the view, but the tool opens the upload dialog at once | fixed in `65ff32d` |
| Tool group corner mark | load Classic, look at the toolbar | the mark (Locus design) only appeared after a group had been opened once, because the submenu is built lazily | fixed in `8d79ebf` |

## Constructions with every 2D tool (Classic, real clicks)

Each case: fresh page, setup objects by command, `setMode`, the listed
clicks, dialog value typed where the tool asks, then the object list compared.
All cases produced identical names, types, definitions and values in both
apps unless noted, and the console stayed clean.

| Tool (mode) | Clicks (world coordinates) | Result in both | Status |
| --- | --- | --- | --- |
| Move (0) | drag A from (1, 1) to (3, 2) | A = (3, 2) | works |
| Point (1) | (1, 1), (3, 2); on line f; inside a polygon | free points; `Point(f)`; `PointIn(p)` | works |
| Point on Object (501) | on circle x²+y²=9 | point on c | works |
| Intersect (5) | two lines; circle and line; click near one intersection | `Intersect(a, b)`; both circle-line points | works |
| Midpoint or Center (19) | two points; segment; circle; polygon | `Midpoint(A, B)`, `Midpoint(s)`, `Center(c)`, `Centroid(p)` | works |
| Attach / Detach Point (67) | drag A onto f; click A then f; click `Point(f)` | attached `Point(f)`; detached free point | works |
| Complex Number (72) | (2, 3) | z₁ = 2 + 3i | works |
| Extremum (75), Roots (76) | click the graph of x²−2x, x²−4 | `Extremum(f)`; two `Root(f)` points | works |
| Line, Segment, Ray, Vector (2, 15, 18, 7) | (−2, −1), (2, 1) | `Line`, `Segment`, `Ray`, `Vector` of A, B | works |
| Vector from Point (37) | A, then vector u | A′ = `Translate(A, u)`, v = `Vector(A, A′)` | works |
| Polyline (65) | three points, then the first again | `PolyLine(A, B, C)` (clicking the last point again does not finish, in both) | works |
| Segment with Given Length (45) | click, dialog "3" | B = `Point(Circle(A, 3))`, f = 3 | works |
| Perpendicular, Parallel Line (4, 3) | A, then line | `OrthogonalLine(A, f)`, `Line(A, f)` | works |
| Perpendicular Bisector (8), Angle Bisector (9) | two points; three points | `LineBisector`, `AngularBisector` | works |
| Tangents (13) | point and circle; point and function | two `Tangent(A, c)`; `Tangent(A, f)` | works |
| Polar or Diameter Line (44) | point and circle | `Polar(A, c)` | works |
| Best Fit Line (58) | selection rectangle around 4 points | `FitLineY({A, B, C, D})` | works |
| Locus (47) | dependent point, then point on path | `Locus(B, A)` (default name loc1 since `5f8740e`) | works |
| Polygon, Rigid, Vector Polygon (16, 64, 70) | three vertices, first again | same polygons, segments, and the rigid/vector constructions | works |
| Regular Polygon (51) | two points, dialog "5" | `Polygon(A, B, 5)` with C, D, E | works |
| Circle tools (10, 34, 11, 53, 24, 20, 21, 22, 23) | center/points; radius dialog "3"; compass from segment | `Circle`, `Circle(A, 3)`, three-point circle, `Circle(C, Segment(A, B))`, `Semicircle`, `CircleArc`, `CircleSector`, `CircumcircleArc`, `CircumcircleSector` | works |
| Ellipse, Hyperbola, Parabola, Conic through 5 Points (55, 56, 57, 12) | foci and point; focus and directrix; five points | same equations | works |
| Angle (36) | three points; two lines | `Angle(A, B, C)` = 291.8°, `Angle(f, g)` = 45° | works |
| Angle with Given Size (46) | leg point, vertex, dialog "45" | A′ = `Rotate(A, 45°, B)`, α = 45° | works |
| Distance or Length (38) | two points; point and line | `Distance` plus the "AB = 5" text | works |
| Area (49) | polygon; circle | area texts and points | works |
| Slope (50) | line | m = `Slope(f)` | works |
| List (71) | selection rectangle | l1 = {A, B, C} | works |
| Reflect about Line, Point, Circle (30, 29, 54) | object, then mirror | `Mirror(A, f)`, `Mirror(A, B)`, `Mirror(A, c)` | works |
| Rotate around Point (32) | object, center, dialog "90" | `Rotate(A, 90°, B)` | works |
| Translate by Vector (31) | object and vector; polygon and two points | `Translate(A, u)`; `Vector(A, B)` and `Translate(p, u)` | works |
| Dilate from Point (33) | object, center, dialog "2" | `Dilate(A, 2, B)` | works |
| Text (17) | click, type "Hello", OK | text1 = "Hello" | works |
| Image (26) | select tool, choose a PNG in the upload dialog | image with corner points A, B; default name pic1 | fixed in `5df3fb9` (was picture1) |
| Pen (62) | drag | one `PenStroke` (name stroke1 since `5f8740e`) | works |
| Freehand Shape (73) | drag a line; drag a circle | `Segment(A, B)`; `Circle(A, 2.98)` | works |
| Relation (14) | two parallel lines | dialog "f and g are parallel" with "Check Symbolically" | works |
| Function Inspector (68) | click the graph | inspector view with Interval and Points tabs | fixed in `78953cf` (see below) |
| Slider, Checkbox, Button, Input Box (25, 52, 60, 61) | click, fill the dialog, OK | a = 1 slider; checkbox b hiding A; button1 with script; InputBox1 linked to a (see "Action objects") | works |
| Move Graphics View (40) | drag | view origin moved by the drag | works |
| Zoom In, Zoom Out (41, 42) | click (1, 1); drag a rectangle from (−2, −2) to (2, 2) | same new view (xMin −6.33 / −15.5; rectangle: xMin −1.996, scale 0.0038) | works |
| Move Graphics View on an axis | drag the x-axis 100 px | same x scale change (0.0190 → 0.0138 units per pixel) | works |
| Show / Hide Object, Label (27, 28) | click A, switch tool | A hidden; label hidden | works |
| Copy Visual Style (35) | red size-8 A, then B | B red, size 8 | works |
| Delete (6) | click A | A deleted | works |
| Rotate around Point (39, Move group) | center, then drag the segment | segment rotated around A | works |
| Select (77) | click A | selected | works |
| Probability Calculator (66) | setMode | opens the view (probability worker covers its content) | works |

### The same sweep in the Geometry app

All 87 cases were repeated in `geometry.html` (axes hidden, so no points on
axes). Object names, types and definitions are identical in both apps; the
coordinates of clicked points differ in the third decimal because the
GeoGebra page has a 64 px header, so the canvas and its pixel grid are not
the same size (for example y = 1.0048 in GeoGebra and y = 1 in Locus for
the same world coordinate). Console clean in every Locus case.

## Dialogs of the tools

| Dialog | Check | Status |
| --- | --- | --- |
| Segment with Given Length, Circle with Center and Radius, Regular Polygon, Angle with Given Size (with counterclockwise/clockwise), Rotate around Point, Dilate from Point | open by clicking, title, field label, typing and Enter create the object | works |
| Slider | Name, number/angle toggle, Min, Max, Step; OK creates the slider | fixed in `bef20a1`, `897445e` ("min"/"max" were lower case next to "Step") |
| Button | caption field, CodeMirror script editor with suggestion chips and "Objects"; typing `SetValue(k,7)` and clicking the button runs it (k = 7) | works |
| Checkbox to Show/Hide Objects | caption, object list, choose "Point A", OK: checkbox b is the condition of A, unchecking hides A | works |
| Input Box | caption, linked object list (a, k, A); OK creates InputBox1 = `InputBox(a)` | works |
| Text | formatting bar, preview, LaTeX switch; "Hello" creates text1 | works |
| Dialogs in German | `?lang=de`: Schieberegler, Schaltfläche, Kontrollkästchen, Eingabefeld, Text | all labels German; the text dialog's "Preview" button stayed English (literal in `PreviewPanel`, also in GeoGebra) | fixed in `ce665df` |
| Image | Upload / Camera tabs, Browse opens the file chooser, PNG inserted | works (camera: not testable headless, no camera) |
| Relation | message and "Check Symbolically" | works |

## Function inspector

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Look of the view | Function Inspector tool, click f(x) = x² | Locus had no styles: tabs as plain text ("IntervalPoints"), table without grid, add-column and copy buttons collapsed to a few pixels, no close button | fixed in `78953cf` |
| Close button | click the X in the top right corner | Locus hid it: views without a style bar get a 0 px title bar layer that clipped the button; it now floats in the corner and closes the view | fixed in `78953cf` |
| Interval tab | Min, Max, Root, Integral, Area, Mean, Length for the default interval | same values | works |
| Points tab | add column Derivative from the + popup, table of points, the four toggles (table, xy lines, tangent, osculating circle) | same columns, values and toggle states; tangent and circle drawn | works |
| Copy to spreadsheet | options button, "Copy to Spreadsheet" | same cells A1…C10 | works |

## Object properties (Classic settings view)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Tabs per object type | right click > Settings for point, segment, line, polygon, circle, text, slider, function, vector, angle | Basic, Style, Advanced, Scripting for all; same controls per tab (counts of check boxes, drop-downs, fields, sliders) | works |
| Basic | name, definition, caption, label mode, Show Object, Show Trace, Fix Object, Auxiliary Object; set caption "My Caption", fix, trace | same XML (`caption`, `fixed`, `trace`) | works |
| Style | colour, size/point style, line style, thickness, opacity, filling, text style, slider style | same sections | works |
| Advanced | Selection Allowed, Increment, Vertical Increment, Coordinates, Condition to Show Object, Location, Dynamic Colors (RGB/HSV/HSL), Layer; set condition `k>2`, red `k/5`, layer 3, selection off | same XML; A hidden at k = 1, shown and red at k = 5 | works |
| "Increment" label | Advanced > Interaction | Locus said "Animation Step" for the arrow-key and animation step next to "Vertical Increment" | fixed in `95e709f` |
| Scripting: GGBScript | On Click `SetValue(k, k+1)`, On Update `SetValue(j, x(A))`; click A, move A | k = 1, j follows x(A); XML `ggbscript val/onUpdate` | works |
| Scripting: JavaScript | language drop-down "JavaScript", `ggbApplet.setValue('k', 42)` and a probe of `document` | k = 42; the script has no `document` (runs in the sandbox), same as GeoGebra | works |
| Global settings | menu Settings: General (rounding, coordinates, angle unit, font size), Algebra, Graphics (grid, axes, dimensions, point snapping, labelling, construction step bar) | same sections; rounding "5 Decimal Places" gives r = 1.41421 | works |

## Action objects, animation, trace

| Feature | Steps | Status |
| --- | --- | --- |
| Button colour | create a button | Locus gave new buttons GeoGebra's purple; now the Locus teal | fixed in `599c66d` |
| Slider animation | right click slider > Animation | value runs (0.2 → 0.9 in 1.5 s), animation pause button shown | works |
| Point on path animation | right click `Point(c)` > Animation | point moves along the circle | works |
| Trace | right click Q = (a, −3) > Show Trace while a animates | trace drawn, `isTracing` true | works |
| Fix / lock | Fix Object in settings; Lock Object in a text's context menu, then drag it | `fixed` true, the text does not move | works |

## Classic style bar and context menus

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Style bar position | open the graphics style bar with a slider at its default place | Locus floated the bar at the top left over the slider and its label | fixed in `702ca42` (top right, toggle at the right end, like the reference) |
| Point style bar | select A: colour, point style (with size slider), label style, fix, settings, view menu | same buttons; choosing blue, point style ×, label "Name and Value" writes the same XML | works |
| Line style bar | select a segment: colour, line style (12 choices), line start, line end, label style | same buttons and XML | works |
| Text, angle, function style bars | select a text (background, colour, bold, italic, 7 text sizes, absolute position, fix), an angle (colour, line style, angle interval, label), a function | same buttons and popups | works |
| Angle interval choices | angle style bar "Angle Between", angle context menu | Locus read "0°°–360°°": the string added a degree sign to values that already have one | fixed in `70ba3e4` (string; in the compiled bundle from the next full build) |
| Empty selection | axes, grid (3 types), point snapping (Automatic, Snap to Grid, Fixed to Grid, Off), standard view, view menu | same | works |
| Point capturing | snap to grid, off, fixed to grid; click near grid points | (1, 1), (3.12, 0.9), (−3, 2) in both | works |
| Data analysis style bar | open One-Variable Analysis | the floating bar covered the display type select | fixed in `ecf7f72` |
| Geometry quick style bar | select a point, a segment; open colour, point or line style, line start, line end, label, delete, more | same buttons and popups (48 colours with custom colour, thickness slider, 12 arrow styles, Name / Show Label / Show Value, Duplicate / Fix Object / Show Trace / Settings); delete removes the object | works |
| Context menus | right click point, segment, line, circle, text, function, vector, angle, empty view | same entries (equation forms, Polar Coordinates, Show Trace, Animation, Lock, Pin to Screen, Rename, Delete, Settings; Show Axes/Grid/Settings on the view) | works |
| Perspectives popup at start | load `classic.html` | open at start in both, closes on a click in the view (the click also acts), not on Escape. Locus has an "Exam Mode" entry (offline exam enabled on purpose) and no Download entry or help button (services removed) | works / by design |

## Construction protocol (Classic)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| View | graphics view menu > Construction Protocol with a triangle, midpoint, segment | same rows, numbers, colours | works |
| Narrow panel | default width of about 290 px | Locus split words ("Poi / nt"), header columns drifted out of line with the body, and the navigation bar cut off its first button | fixed in `a783f61` |
| Navigation | first, previous, next, last | 1/6, 2/6, 3/6, 2/6, 6/6 in both | works |
| Columns | column menu: Name, Toolbar Icon, Description, Definition, Value, Caption, Breakpoint, Show Only Breakpoints | same entries and XML (`consProtColumns`) | works |
| Breakpoints | show the column, tick two rows, Show Only Breakpoints, navigate | 1/2, 2/2; XML `breakpoint val="true"`, `showOnlyBreakpoints="true"` | works |
| Play | play button with 2 s delay | steps advance, button toggles | works |

## Custom tools

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Create New Tool | menu Tools > Create New Tool; output F (foot of perpendicular), inputs A, B, C found automatically, name "Foot", help text, Finish | tool 100001 added to the toolbar | works |
| Use the tool | select it, click three points | H = `Foot(D, E, G)` with the same value | works |
| Manage Tools | menu Tools > Manage Tools | list "Foot: Point, Point, Point", Open, Save, name, command, help, icon, Show in Toolbar | works; the "Icon …" button was unstyled, fixed in `f7da55a` |
| Saved with the file | `getBase64`, new construction, `setBase64` | `geogebra_macro.xml` with the macro; tool back in the toolbar | works |

## Focus and keyboard

| Feature | Steps | Status |
| --- | --- | --- |
| Focus ring on the canvas | press Escape (or Delete, arrows) in the view, then keep clicking | the canvas kept `:focus-visible` and showed the teal ring through every later click; now no ring on the canvas, keyboard focus shows as the highlight of the object Tab selects | fixed in `2cfa8e7` |
| Tab through objects | click the view, Tab | first object highlighted | works |

## Phone (390 x 844, touch)

| Feature | Steps | Status |
| --- | --- | --- |
| Geometry tools | tap the Tools tab, tap Segment, tap two positions | bottom sheet with the tools, segment A–B created | works |
| Classic tool groups | tap a group in the Classic toolbar | Locus showed only a back arrow after the header buttons: the styles expected the "visible" class on the tool list and put the list under the toolbar. The group's tools now fill the tool row after the back button, as in GeoGebra; picking Polyline from the scrolled row and going back work | fixed in `97217e1` |
| Settings from the quick style bar | geometry: select A, ⋮ > Settings | properties view with Basic, Style, Advanced, Scripting | works |

## Default object names

`Button`, `Text`, `Slider`, `Checkbox`, lists, matrices, polygons (t, q,
poly), conics (eq), vectors, angles, complex numbers and slope fields get
the same default names as in GeoGebra. Input boxes, strokes and loci were
aligned in `5f8740e` (another worker), images in `5df3fb9`. German default
names are Locus's own translation (for example Richtungsfeld1 where
GeoGebra says Steigungsfeld1).

## Open or upstream

- Upstream: the Distance tool on a segment and the Angle tool on a polygon
  interior created nothing with the click positions used, in both apps.
- Upstream: in the headless runs the box plot of the second data analysis
  panel stayed empty in both apps.
- Not testable headless: the Image tool's Camera tab (no camera device).
