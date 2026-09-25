# Vendored Maven artifacts

These free libraries are needed by the build but are published only on
GeoGebra's Maven server (`repo.geogebra.net`). They are copied here unchanged
so Locus builds without that server. Licences and sources are listed in
`THIRD_PARTY.md` (section "Build-time libraries from GeoGebra's Maven
repository" and "Giac").

| Artifact | Licence | Source |
| --- | --- | --- |
| `fr.ujf-grenoble:giac-gwt:70501` | GPL 3.0+ | Giac, <https://github.com/geogebra/giac> |
| `org.gwtproject.core:gwt-core:1.0.1-GGB` | Apache 2.0 | <https://github.com/zbynek/gwt-core> (sources jar included) |
| `org.treblereel.gwt.gwtproject.resources:gwt-resources-api/-processor:202602114`, `...widgets:gwt-widgets` | Apache 2.0 | treblereel GWT modules (sources jar included) |
| `org.javacc:core:8.0.3-GGB`, `org.javacc.generator:java:8.0.5-GGB` | BSD 3-Clause | <https://github.com/zbynek/javacc-8-java> |
| `org.apache:math-cross-platform:3.6.3` | Apache 2.0 | <https://github.com/geogebra/apache-math-cross-platform> |
| `com.google.j2objc:annotations:7e76bfd` | Apache 2.0 | J2ObjC annotations |
| `com.google.gwt.gwtmockito:gwtmockito:1.1.11-SNAPSHOT` (tests) | Apache 2.0 | <https://github.com/zbynek/gwtmockito> commit c206d12 |
