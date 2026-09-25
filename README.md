# Locus

Locus is free software for dynamic mathematics in the browser: graphing,
geometry, 3D, a computer algebra system, a scientific calculator, probability
and statistics, a spreadsheet and a Notes whiteboard. It runs entirely in the
browser. There are no accounts and no tracking, and it does not depend on any
server.

Live: <https://opengebra.arturf.ch>

## Origin and licence

Locus is built from the source code of [GeoGebra](https://www.geogebra.org)
by GeoGebra GmbH, which is published under the
[EUPL 1.2](https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12).
Locus is distributed under the same licence (see `LICENSE`).

GeoGebra's language files, documentation, icons, images and style sheets are
not free software (CC BY-NC-SA 4.0), so Locus does not include them. Its
strings, icons, styles and page templates were written anew for Locus under
the rules in [`docs/clean-room.md`](docs/clean-room.md).
`tools/import-upstream.sh` shows exactly what is removed on import.
Third-party components and their licences are listed in `THIRD_PARTY.md`.

Locus is not affiliated with or endorsed by GeoGebra GmbH. "GeoGebra" is a
registered trademark of GeoGebra GmbH and is used here only to name the
origin of the source code and the `.ggb` file format that Locus can open.

## Building

Requirements: JDK 17 or newer, and about 6 GB of free memory for the GWT
compiler.

```sh
./gradlew -p source/web :web:gwtCompile :web:copyHtml -Pgmodule=org.geogebra.web.SuperWeb
python3 -m http.server 8000 --directory source/web/web/war
```

Then open <http://localhost:8000/>. `tools/build-css.sh` rebuilds only the
style sheets. `tools/build-translations.py` regenerates the web translation
bundles from the `.properties` files in
`source/shared/common-jre/src/main/resources/org/geogebra/common/jre/properties`.

## Updating from upstream

```sh
git clone https://github.com/geogebra/geogebra.git ../geogebra-upstream
tools/import-upstream.sh ../geogebra-upstream .
```

Review the diff: the script overwrites code with upstream's and removes the
non-free files again, and Locus-specific code changes must be re-applied where
upstream touched the same lines.
