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

package org.geogebra.common.kernel.commands;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.geogebra.common.BaseUnitTest;
import org.geogebra.common.kernel.geos.GeoLine;
import org.junit.jupiter.api.Test;

class GermanCommandNamesTest extends BaseUnitTest {

	@Test
	void germanCommandNameShouldWorkInEnglishInterface() {
		assertEquals("en", getLocalization().getLanguageTag());
		add("A = (1, 4)");
		add("u = Vector((6, 4))");
		GeoLine german = add("f = Gerade(A, u)");
		GeoLine english = add("g = Line(A, u)");
		assertEquals(Commands.Line, german.getParentAlgorithm().getClassName());
		assertTrue(german.isEqual(english));
	}
}
