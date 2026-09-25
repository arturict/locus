plugins {
    alias(libs.plugins.geogebra.java.library)
    alias(libs.plugins.geogebra.pmd)
}

dependencies {
    implementation(libs.elemental2.core)
    implementation(libs.elemental2.dom)
    implementation(libs.gwt.timer)
    implementation(project(":gwtutil"))
    // RichTextResourcesImpl is generated from the bundle built in source/web/richtext-js
    api(files(file("build/generated/sources/annotationProcessor/java/main/")))
    annotationProcessor(libs.gwt.resources.processor)
}

tasks.compileJava.get().options.sourcepath = files(tasks.processResources.get().destinationDir)
        .builtBy(tasks.processResources)
