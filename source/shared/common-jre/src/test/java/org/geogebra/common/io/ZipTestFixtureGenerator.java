/*
 * Locus test fixture generator.
 * SPDX-License-Identifier: EUPL-1.2
 */

package org.geogebra.common.io;

import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

import org.geogebra.common.BaseUnitTest;
import org.geogebra.common.awt.GColor;
import org.geogebra.common.factories.AwtFactoryCommon;
import org.geogebra.common.jre.headless.AppCommon;
import org.geogebra.common.jre.io.MyXMLioCommon;
import org.geogebra.common.kernel.ConstructionDefaults;
import org.geogebra.common.kernel.geos.GeoElement;
import org.geogebra.common.main.AppCommon3D;
import org.geogebra.common.main.settings.config.AppConfigDefault;
import org.geogebra.test.LocalizationCommonUTF;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;

/**
 * Writes {@code src/test/resources/org/geogebra/common/io/ziptest.ggb}, the complete .ggb
 * file that {@link MyXMLioTest#loadCompleteZip()} reads. GeoGebra's own fixture was a
 * GeoGebra material and is not part of Locus, so Locus builds an equivalent file with its
 * own writer: a construction with the free points A and B, a global JavaScript library that
 * calls {@code console.log}, an orange default for free points in the 2D defaults and the
 * colour (216, 27, 96) as default for polyhedra in the 3D defaults.
 *
 * <p>The test is skipped in normal runs. Regenerate the file with
 * {@code LOCUS_REGENERATE_FIXTURES=true ./gradlew -p source/shared :common-jre:test
 * --tests '*ZipTestFixtureGenerator'}.
 */
class ZipTestFixtureGenerator extends BaseUnitTest {

	static final GColor POLYHEDRON_COLOR = GColor.newColor(216, 27, 96);

	@Override
	public AppCommon createAppCommon() {
		return new AppCommon3D(
				new LocalizationCommonUTF(3), new AwtFactoryCommon(), new AppConfigDefault());
	}

	@Test
	@EnabledIfEnvironmentVariable(named = "LOCUS_REGENERATE_FIXTURES", matches = "true")
	void writeZipTestFixture() throws IOException {
		ConstructionDefaults defaults = getConstruction().getConstructionDefaults();
		GeoElement freePoint = defaults.getDefaultGeo(ConstructionDefaults.DEFAULT_POINT_FREE);
		GeoElement polyhedron = defaults.getDefaultGeo(ConstructionDefaults.DEFAULT_POLYHEDRON);
		// the fixture is only meaningful if it changes the defaults of a fresh app
		assertNotEquals(GColor.ORANGE, freePoint.getObjectColor());
		assertNotEquals(POLYHEDRON_COLOR, polyhedron.getObjectColor());
		freePoint.setObjColor(GColor.ORANGE);
		polyhedron.setObjColor(POLYHEDRON_COLOR);

		add("A=(0,0)");
		add("B=(1,0)");
		getKernel().setLibraryJavaScript(
				"function ggbOnInit() {\n\tconsole.log(\"ziptest loaded\");\n}");

		Path target = Path.of("src/test/resources/org/geogebra/common/io/ziptest.ggb");
		try (OutputStream os = Files.newOutputStream(target)) {
			new MyXMLioCommon(getKernel(), getConstruction()).writeGeoGebraFile(os, false);
		}
	}
}
