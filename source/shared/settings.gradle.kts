pluginManagement {
    includeBuild("../build-logic")
}

plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

dependencyResolutionManagement {
    versionCatalogs {
        create("libs") {
            from(files("../../gradle/libs.versions.toml"))
        }
    }
    repositories {
        // Free libraries that are only published on GeoGebra's Maven server, vendored
        // so the build does not depend on it (see vendor/README.md).
        maven { url = uri(settingsDir.resolve("../../vendor/maven")) }
        mavenCentral()
    }
}

include("canvas-base")
include("common")
include("common-jre")
include("ggbjdk")
include("giac-jni")
include("xr-base")
include("renderer-base")
include("editor-base")
include("keyboard-base")
include("keyboard-scientific")
includeBuild("../openrewrite")
