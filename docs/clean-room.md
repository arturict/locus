# Clean-room rules for Locus assets

Locus is built from GeoGebra's source code, which GeoGebra GmbH licenses under
the EUPL 1.2. GeoGebra's language files, documentation, and user-interface
images and style files (logos, icons, style sheets) are licensed CC BY-NC-SA 4.0
(https://www.geogebra.org/license) and are **not** part of Locus.
`tools/import-upstream.sh` removes them on every import. Locus writes its own
replacements under the EUPL 1.2.

Anyone writing a replacement asset follows these rules:

1. **Do not look at GeoGebra's version of the asset you are replacing.** That
   covers `.properties` translation files, `properties_keys_*.js` bundles,
   `.scss`/`.css` style sheets (including compiled CSS in a build or served by
   geogebra.org), images and icons, HTML templates and documentation or manual
   pages. This applies to any checkout, build output, website or cache.
2. **Derive behaviour from the code.** The Java and Kotlin sources are EUPL
   and may be read freely: key names and how they are used, CSS class names
   the widgets set, command argument signatures in the command processors,
   and the image paths the resource bundles expect.
3. **Third-party assets come from their upstream source**, with their licence
   recorded in `THIRD_PARTY.md`: for example Material Symbols (Apache 2.0)
   from Google's repository and Font Awesome Free icons (CC BY 4.0).
4. **Functional names are not creative text.** Command names, which must equal
   the internal command names for file compatibility, and standard
   mathematical terms such as "Circle" or "Midpoint" may be the obvious words.
   Sentences, tooltips, help texts and error messages are written fresh.
5. Watching the running GeoGebra app to understand *what a feature does* is
   fine. Copying its look (colours, spacing values, icon drawings) is not;
   Locus has its own visual design (`docs/design.md`).
