pluginManagement {
    repositories {
        gradlePluginPortal()
    }
    includeBuild("../build-logic")
}

plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

dependencyResolutionManagement {
    repositories {
        // Free libraries that are only published on GeoGebra's Maven server, vendored
        // so the build does not depend on it (see vendor/README.md).
        maven { url = uri(settingsDir.resolve("../../vendor/maven")) }
        mavenCentral()
    }
    versionCatalogs {
        create("libs") {
            from(files("../../gradle/libs.versions.toml"))
        }
    }
}

include("canvas-web")
include("carota-web")
include("editor-web")
include("gwt-generator")
include("gwtutil")
include("keyboard-web")
include("renderer-web")
include("uitest")
include("web")
include("web-common")
include("web-dev")
includeBuild("../shared")
