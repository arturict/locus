import Gwt_conventions_gradle.MinifyLibTask
import de.aaschmid.gradle.plugins.cpd.Cpd
import groovy.json.JsonOutput
import io.miret.etienne.gradle.sass.CompileSass
import org.apache.tools.ant.taskdefs.condition.Os
import org.docstr.gwt.AbstractBaseTask
import org.docstr.gwt.GwtDevModeTask

plugins {
    alias(libs.plugins.geogebra.java)
    alias(libs.plugins.geogebra.gwt)
    alias(libs.plugins.geogebra.pmd)
    alias(libs.plugins.geogebra.spotbugs)
    alias(libs.plugins.geogebra.webjars)
    alias(libs.plugins.cpd)
    alias(libs.plugins.sass)
    alias(libs.plugins.geogebra.version) apply false
}

description = "Web app of Locus, based on the web platform code of GeoGebra"

dependencies {
    implementation(project(":carota-web"))
    implementation(project(":web-dev"))
    implementation(project(":web-common"))
    implementation(project(":editor-web"))
    implementation(project(":keyboard-web"))
    implementation(libs.pdfJs)
    implementation(files(file("build/generated/sources/annotationProcessor/java/main/")))

    testImplementation(libs.junit)
    testImplementation(libs.gwt.user)
    testImplementation(libs.gwt.mockito)

    annotationProcessor(project(":gwt-generator"))
    annotationProcessor(libs.gwt.resources.processor)
    compileOnly(libs.jakarta.servlet.api)
}

val warDirRel = "war"

gwt {
    modules = if (project.hasProperty("gmodule")) {
        project.property("gmodule").toString().split(",")
    } else {
        listOf("org.geogebra.web.SuperWeb", "org.geogebra.web.WebSimple",
            "org.geogebra.web.Web")
    }

    sourceLevel = "17"

    war = layout.projectDirectory.dir(warDirRel)

    devMode {
        bindAddress = project.findProperty("gbind")?.toString() ?: "localhost"
        superDevMode = true

        val devModule = project.findProperty("gmodule")?.toString()?.replace(",.*$".toRegex(), "") ?: "org.geogebra.web.SuperWeb"
        modules = listOf(devModule)
        startServer = true
    }
}

tasks.compileJava {
    options.sourcepath = files(tasks.processResources.get().destinationDir).builtBy(tasks.processResources)
}

tasks.compileSass {
    // Directory where to output generated CSS:
    outputDir = file("${projectDir}/war/css")

    // Source directory containing sass to compile:
    sourceDir = file("${projectDir}/src/main/resources/scss")

    // Set the output style:
    // Possible values are “expanded” and “compressed”, default is “expanded”.
    style = compressed

    // Source map style:
    //  - file: output source map in a separate file (default)
    //  - embed: embed source map in CSS
    //  - none: do not emit source map.
    sourceMap = none
}

tasks.register<CompileSass>("watchSass") {
    outputDir = file("${projectDir}/war/css")
    sourceDir = file("${projectDir}/src/main/resources/scss")
    style = compressed
    sourceMap = embed

    // Watch sass files in sourceDir for changes
    // (Default is to not watch, compile once and terminate)
    watch()
}

tasks.withType<AbstractBaseTask>().configureEach {
    jvmArgs = listOf("-Xss512M")
}

// Annotation processor scans classpath inefficiently, just increase memory for now
tasks.withType<JavaCompile>().configureEach {
    options.forkOptions.jvmArgs = listOf("-Xmx4g")
}

tasks.withType<Test>().configureEach {
    jvmArgs("--add-opens", "java.base/java.lang=ALL-UNNAMED")
}

tasks.register("run") {
    dependsOn(tasks.gwtDevMode)
}

tasks.withType<Test>().configureEach {
    jvmArgs("--add-opens", "java.base/java.lang=ALL-UNNAMED")
}

val cleanWar by tasks.registering(Delete::class) {
    val deleteTargets = listOf("web", "web3d", "webSimple", "tablet3d", "tabletWin")
    delete(deleteTargets.map { layout.projectDirectory.dir("$warDirRel/$it") })
}

val copyHtml by tasks.registering {
    dependsOn(tasks.compileSass)
    description = "Generate app.html, app-release.html, graphing.html and others"
    group = "application"

    doLast {
        createHtml()
    }
}

val copyDevHtml by tasks.registering {
    dependsOn(tasks.compileSass)
    description = "Generate app.html, app-release.html, graphing.html and others without inlined css"
    group = "application"

    doLast {
        createHtml()
    }
}

tasks.register<Copy>("deployIntoWar") {
    dependsOn(copyHtml, tasks.gwtCompile)
    description = "Copies/updates the GWT production compilation directory (web3d, ...) to the war directory."
    into("web3d/sourcemaps/") {
        from(layout.buildDirectory.file("gwt/deploy/web3d/symbolMaps/").get().asFile)
    }
}

tasks.named<GwtDevModeTask>("gwtDevMode") {
    dependsOn(tasks.jar, copyDevHtml)
    args("-style", "PRETTY")
    description = "Starts a codeserver, and a simple webserver for development"

    var sassCompilation: Process? = null
    doFirst {
        val pb = ProcessBuilder(if (Os.isFamily(Os.FAMILY_WINDOWS))
            listOf("cmd", "/c", "START", "/MIN", file("..\\..\\..\\gradlew.bat").absolutePath, "watchSass")
        else
            listOf(file("../../../gradlew").absolutePath, "watchSass")
        )
        pb.directory(file("."))
        sassCompilation = pb.start()
    }
    doLast {
        sassCompilation?.destroy()
    }
}

val libDir = "src/main/resources/org/geogebra/web"

val minifyRewritePHYs by tasks.registering(MinifyLibTask::class) {
    sourceFile = project(":web-common").file("${libDir}/resources/js/rewrite_pHYs.js")
}

val minifyCanvas2Pdf by tasks.registering(MinifyLibTask::class) {
    sourceFile = file("${libDir}/pub/js/canvas2pdf.js")
}

val minifyWhammy by tasks.registering(MinifyLibTask::class) {
    sourceFile = file("${libDir}/pub/js/whammy.js")
}

tasks.register("minifyLibs") {
    dependsOn(minifyRewritePHYs, minifyWhammy, minifyCanvas2Pdf)
}

tasks.register("collectFaIcons") {
    description = "Collect all parameters of the instantiations of the FaIconSpec class"
    doLast {
        val srcDirs = listOf("src/main/java", "../web-common/src/main/java")
        val pattern = """new\s+FaIconSpec\((['"])(.*?)\1\)""".toRegex()
        val parameters = mutableListOf<String>()

        srcDirs.forEach { srcDir ->
            fileTree(srcDir).filter { it.extension == "java" }.forEach { file ->
                val content = file.readText()

                pattern.findAll(content).forEach {
                    val param = it.groupValues[2]
                    parameters.add(param.removePrefix("fa-"))
                }
            }
        }

        if (parameters.isEmpty()) {
            logger.error("No instances for FaIconSpec found!")
        } else {
            val styles = listOf("light", "regular", "solid", "thin")
            val file = file("$projectDir/build/fontAwesomeIcons.txt")
            file.writeText(JsonOutput.prettyPrint(JsonOutput.toJson(mapOf(styles[0] to parameters))))
            logger.lifecycle("File \"fontAwesomeIcons.txt\" created at: ${file.absolutePath}")
        }
    }
}

tasks.test {
    ignoreFailures = System.getenv("CI") != null
    maxHeapSize = "1024m"
}

cpd {
    isIgnoreFailures = System.getenv("CI") != null
    minimumTokenCount = 100
}

tasks.withType<Cpd>().configureEach {
    exclude("**/*.html", "**/*.jj", "**/*.xml", "**/*.svg")
}

/**
 * One entry per app page; the id is the app name passed to the GWT module.
 * [params] are extra data-param attributes for that app (without the "data-param-" prefix).
 */
data class LocusApp(
    val id: String,
    val title: String,
    val description: String,
    val params: Map<String, String> = emptyMap(),
)

/** Apps with a graphics view get the zoom, home and fullscreen buttons. */
val graphicsParams = mapOf("showZoomButtons" to "true", "showFullscreenButton" to "true")

val locusApps = listOf(
    LocusApp("graphing", "Graphing", "Plot functions, explore sliders and find special points.", graphicsParams),
    LocusApp("geometry", "Geometry", "Construct points, lines, circles and polygons with compass-and-ruler tools.", graphicsParams),
    LocusApp("3d", "3D Graphing", "Plot surfaces, solids and 3D constructions.", graphicsParams),
    LocusApp("cas", "CAS", "Solve, factor, differentiate and integrate symbolically.", graphicsParams),
    LocusApp("scientific", "Scientific Calculator", "Everyday calculations with fractions, statistics and more."),
    LocusApp("suite", "Calculator Suite", "Graphing, geometry, 3D, CAS and probability in one app.", graphicsParams),
    LocusApp("notes", "Notes", "A whiteboard for math with pages, pens, text and embedded apps.",
        mapOf("showSlides" to "true")),
    // Classic offers the perspectives picker when it starts
    LocusApp("classic", "Classic", "Every view at once: algebra, graphics, spreadsheet, CAS and 3D.",
        graphicsParams + mapOf("showAppsPicker" to "true")),
)

fun template(fileName: String): String =
    file("src/main/resources/org/geogebra/web/resources/html/$fileName").readText()

fun escapeHtml(text: String): String =
    text.replace("&", "&amp;").replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;")

fun appParams(app: LocusApp): String =
    app.params.entries.joinToString("") { (name, value) ->
        "\n  data-param-$name=\"${escapeHtml(value)}\""
    }

fun fillApp(text: String, app: LocusApp): String =
    text.replace("%APP_ID%", app.id)
        .replace("%APP_TITLE%", escapeHtml(app.title))
        .replace("%APP_DESCRIPTION%", escapeHtml(app.description))
        .replace("%APP_PARAMS%", appParams(app))

fun createHtml() {
    delete {
        delete(fileTree(warDirRel) { include("*.html") })
    }
    copy {
        from(file("src/main/resources/org/geogebra/web/resources/war"))
        into(warDirRel)
    }
    val appTemplate = template("app.html")
    locusApps.forEach { app ->
        file("$warDirRel/${app.id}.html").writeText(fillApp(appTemplate, app))
    }
    val cards = locusApps.joinToString("\n") { app -> fillApp(template("index-card.html"), app) }
    file("$warDirRel/index.html").writeText(template("index.html").replace("%APP_CARDS%", cards))
}
