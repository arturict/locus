/*
 * GeoGebra - Dynamic Mathematics for Everyone
 * Copyright (c) GeoGebra GmbH, Altenbergerstr. 69, 4040 Linz, Austria
 * https://www.geogebra.org
 *
 * This file is licensed by GeoGebra GmbH under the EUPL 1.2 licence and
 * may be used under the EUPL 1.2 in compatible projects (see Article 5
 * and the Appendix of EUPL 1.2 for details).
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 *
 * Note: The overall GeoGebra software package is free to use for
 * non-commercial purposes only.
 * See https://www.geogebra.org/license for full licensing details
 */

package org.geogebra.web.html5.main;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.util.Objects;
import java.util.TreeSet;

import org.geogebra.common.util.lang.Language;
import org.junit.Test;

public class LocalizationWTest {

	private static final String BUNDLE_PREFIX = "properties_keys_";

	/** Every offered language has a bundle and every bundle is offered. */
	@Test
	public void bundledLanguagesShouldMatchTranslationFiles() {
		File dir = new File("src/main/resources/org/geogebra/web/pub/js/");
		TreeSet<String> available = new TreeSet<>();
		for (File f : Objects.requireNonNull(dir.listFiles())) {
			String name = f.getName();
			if (name.startsWith(BUNDLE_PREFIX) && name.endsWith(".js")) {
				available.add(name.substring(BUNDLE_PREFIX.length(), name.length() - 3));
			}
		}
		assertEquals(available, new TreeSet<>(LocalizationW.BUNDLED_LANGUAGE_TAGS));
		for (String tag : LocalizationW.BUNDLED_LANGUAGE_TAGS) {
			assertEquals(tag, Language.fromLanguageTagOrLocaleString(tag).toLanguageTag());
		}
	}

	@Test
	public void englishShouldAlwaysBeBundled() {
		assertTrue(LocalizationW.BUNDLED_LANGUAGE_TAGS.contains("en"));
	}

	@Test
	public void unbundledLanguagesShouldFallBackToBundledOnes() {
		assertEquals(Language.English_US, LocalizationW.toBundledLanguage(Language.English_UK));
		for (Language language : Language.values()) {
			assertTrue(language.name(), LocalizationW.BUNDLED_LANGUAGE_TAGS.contains(
					LocalizationW.toBundledLanguage(language).toLanguageTag()));
		}
	}
}
