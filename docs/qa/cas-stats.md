# QA checklist: CAS, Scientific Calculator, probability, statistics and commands

Area: `cas.html`, the classic CAS view, the command set, `scientific.html`,
the probability calculator (suite and classic), the classic data analysis
views and German locale behaviour. Tested on 2026-09-25 against the untouched
GeoGebra build (reference, `127.0.0.1:8930`) and Locus (`127.0.0.1:8974`,
same `source/web/web/war`), with Playwright and Chrome at 1400 x 900 and as a
phone at 390 x 844. Steps ran through real clicks and typing where the UI
mattered and through `ggbApplet` (`evalCommandGetLabels`, `evalCommandCAS`,
`getValueString`, `getObjectType`, `getXML`) for bulk comparisons. Console
and page errors were captured in every run; unless noted, Locus logged none.

Status: **works** = same result as GeoGebra; **fixed** = was broken or
different, fixed in the named commit; **upstream** = same behaviour or bug in
GeoGebra, left as is; **explained** = a difference with a known, accepted
cause.

## Command coverage (scripted comparison)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Kernel commands, all tables | Every string-literal input of upstream `CommandsTest`, `CommandsUsingCASTest` and `CommandsUsingMockedCasTest` (556 test methods, 1710 inputs: algebra, geometry, statistics, probability, lists, text, logic, functions and calculus, conics, vectors and matrices, transformations, charts, spreadsheet, scripting, discrete, optimisation, financial, CAS-backed commands), each method in a fresh construction of `classic.html`; compared object count, type, defined state and value string | 1561 identical at first pass; every remaining difference re-run and explained: `Random*`, `Sample`, `Shuffle` (random), `DotPlot` and `ClosestPoint` (depend on the graphics view size, which differs), harness timing (lazy command modules or Giac not loaded yet in one app), and a Giac state that both apps reach after hundreds of heavy CAS calls in one page (re-run in fresh pages: identical). Text output differs only where Locus wrote its own strings: `ContingencyTable` says "Column Percent" for "Column %", the `StemPlot` key reads "3\|1 means 3.1" without a "Key:" prefix | works |
| CAS command table (Giac) | All 2719 inputs of upstream `giacTests.js` through `evalCommandCAS` in 25-input chunks, same order in both apps | identical except random commands and `Cauchy` (fixed, below). After about 2500 heavy inputs in one page Giac runs out of memory in Locus (`Aborted(OOM)`) and hangs in GeoGebra; the affected chunks re-run in fresh pages are identical | works |
| Syntax lines match the processors | `./gradlew -p source/shared :common-jre:test` with `CommandsValidationTest` (every `.Syntax` arity is accepted: calling it with wrong types gives an argument-type error, not an argument-count error), `CommandsTest` (519 tests, also checks that no command has more syntax lines than tested calls), `CommandsUsingMockedCasTest`, `SyntaxLocalizationTest` | all pass | works |
| Every command has a name and syntax | Script over `Commands.java` against `command.properties` and `command_de.properties` | every command has an English and German name; 15 CAS-only commands have only `.SyntaxCAS`, as they should; the key sets of both languages match | works |
| `Cauchy.SyntaxCAS` argument order (flagged in the command notes) | `Cauchy(20,3,2)` in the CAS and in the algebra view | GeoGebra's CAS read (scale, median), the algebra command (median, scale): 0.484 vs 0.05 (upstream bug). Now both give 0.0526; syntax lists Median, Scale | fixed in f47229a |
| CAS vs algebra for other distributions | 54 distribution and statistics commands evaluated with `Numeric(…)` in the CAS and in the algebra view | agree (differences are only rounding of the CAS fallback) | works |
| Syntax in the input help | graphing and CAS app: type `Cauchy`, `Solve`, hover the suggestion | the syntax submenu lists the same forms; the CAS app uses `.SyntaxCAS`. GeoGebra's reference build also offers `SolveQuartic`, a preview feature switched on only in test builds | works |

## CAS app (`cas.html`)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Solve, Factor, Expand, Derivative, Integral (definite), Limit, TaylorPolynomial, roots, NSolve | typed with the physical keyboard, Enter | identical results; functions plotted, definite integral shaded | works |
| Exact vs numeric | ≈ button on result rows | same toggle | works |
| Phone 390 x 844 | same inputs | graph above, algebra and keyboard below, results readable | works |

## Classic CAS view

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Solve, systems, Factor, assignments `:=`, row references `$1`, `#1`, Derivative, Integral | typed in the CAS view of `classic.html` (perspective CG) | identical rows and outputs; `f(x):=…` is plotted and its marble filled | works |
| Toolbar tools: Evaluate, Numeric, Keep Input, Factor, Expand, Substitute, Solve, NSolve, Derivative, Integral | type an expression, click the tool | identical outputs including the "Solve:", "NSolve:", "Derivative:" captions | works |
| Substitute dialog | `x^2+y`, Substitute tool, With = 3, OK | dialog lists x and y; result `3² + y` | works |
| Row context menu | right-click an output and a row header | Copy Input, Paste, Insert Above/Below, Delete Row, Use as Text, Copy, Copy as LaTeX in both; Copy as LaTeX puts `\left(x + 1 \right) \; \left(x - 1 \right)` on the clipboard; Delete Row removes the row | works |
| CAS keyboard | focus a row | keyboard with x, y, z, π, e and brackets | works |
| CAS style bar | toggle at the top right of the view | was clipped by the 0 px title bar, so the style bar could not be opened | fixed in f01cd56 |
| Active row | edit a row | a rounded second teal edge looked like a stray bracket before the caret | fixed in e9cd4d1 |

## Scientific Calculator (`scientific.html`)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Arithmetic, fractions, powers and roots | `1/3+1/6`, `sqrt(8)`, `0.1+0.2`, `2^0.5`, `1/7`, `2^10`, `5!`, `nCr(5,2)` | identical values; fraction/decimal toggle on the same rows | works |
| Trig in degrees and radians | `sin(30)`; settings > Angle Unit > Radian, `sin(pi/6)`, `sin(30)`, `asin(1)` | 0.5; then 0.5, −0.988, 1.5708 in both | works |
| Logs | `ln(e)`, `log(100)` | 1, 2 | works |
| Settings | Language, Rounding, Angle Unit, Font Size, Save, Restore | same options | works |
| Undo, redo, settings buttons | GeoGebra shows them in its page header, which Locus pages do not have: no undo button at all (only Ctrl+Z outside the input) | top bar with undo, redo and settings, also in the suite's Scientific sub-app, desktop and phone | fixed in 834db21 |
| History rows, `ans` | rows numbered, `ans` key | same | works |
| Keyboard | 123, f(x), ABC tabs | same keys | works |
| Phone | 390 x 844 | top bar, rows and keyboard fit | works |
| Exam mode entry | menu | GeoGebra's standalone page links to its online exam; Locus offers exam mode in the suite only (`AppConfigScientific.hasExam`) | explained |

## Probability calculator

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| All 15 distributions × 4 interval modes + cumulative | classic perspective B: choose each distribution in the drop-down, click each interval button and the Cumulative box; read the result row, μ/σ and the probability table | every value identical (Normal … Hypergeometric); names differ only in wording (Student's t, F, Log-normal) | works |
| Probability table of discrete distributions | Binomial, Pascal, Poisson, Hypergeometric | the table took its natural width only after the fix; before, the plot shrank to a sliver (Pascal + cumulative) and the result row fell below the fold | fixed in 2ac0753 |
| Suite Probability sub-app | menu > Switch Calculator > Probability, desktop and phone | same distribution panel and plot; phone: plot above, panel below | works |
| Statistics tab: Z/T tests, Z/T intervals (means, differences, proportions), goodness of fit, chi-square | classic, each of 14 procedures with filled inputs | same numbers; GeoGebra's reference logged `Class$S563` console errors, Locus none. Result labels read N, P, T, Z | fixed in 2081fe8 (now n, p, t, z) |
| Export of the graph | style bar export menu: Copy to Graphics View (creates A, B, f, a), Export Image (dialog, downloads `locus-export.png`) | same | works |

## Data analysis (classic, from a spreadsheet selection)

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| One-variable analysis | select A1:A12 by mouse, One Variable Analysis tool; every display type (Histogram, Bar Chart, Box Plot, Dot Plot, Stem-and-Leaf, Normal Quantile) in both plot selects; Show Statistics, Show Data | all numbers identical (n, mean, σ, s, Σx, Σx², quartiles …) | works |
| Two-variable regression | A1:B12, all 9 regression models, Scatter and Residual plot | identical statistics, R², SSE and equations | works |
| Multi-variable | A1:C12, all display options, stacked box plots | identical; GeoGebra's reference logged a `TypeError` and `Class$S563` errors, Locus none | works |
| Export of plots | export menu: Copy to Graphics View, Export Image | same items; copy creates the chart object | works |

## German locale

| Feature | Steps | GeoGebra vs Locus | Status |
| --- | --- | --- | --- |
| Command names typed in German | browser language de-DE, type `Mittelwert({1,2,3})` in the algebra input | works; the API (`evalCommand`) takes English names only, in both apps | works |
| Output in German | definitions show `Normalverteilung`, `Folge`, `Integral von x²` | German names; decimal point stays "." as in GeoGebra | works |
| Navigation rail | graphing and suite in German | Table and Spreadsheet were both "Tabelle"; spreadsheet is now "Tabellenkalkulation", breaking at a soft hyphen in the rail | fixed in 778a5f8 |
| Returning visitors | reload a German page | the German bundle was cached in localStorage under GeoGebra's fixed version number, so string updates would never reach returning users; now always loaded, cache only as fallback | fixed in 496a801 |
| Lower-case statistics commands | `mean`, `mad`, `stdev`, `stdevp` in German | Locus keeps the English names (GeoGebra translates them), so a German `Mittelwert(...)` in the graphing app is shown as `mean(...)` | open (string choice for the strings owner) |

## Upstream and open items

- Giac exhausts memory after thousands of heavy CAS calls in one page (both apps); not reachable in normal use.
- `LocusEquation(Locus(2*A,A))` can take minutes in both apps.
- The probability export button has no tooltip in both apps.
- The classic perspectives popup opens on start in both apps.
