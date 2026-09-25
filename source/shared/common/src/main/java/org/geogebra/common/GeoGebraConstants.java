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

package org.geogebra.common;

/**
 * Application-wide constants (version strings, URLs)
 */
public interface GeoGebraConstants {

	// GeoGebra version
	// DO NOT CHANGE the format of VERSION_STRING (or add commented out version)
	// as it is read by the build system
	// and updated automatically by the "Version Bump" task
	/** last build date */
	String BUILD_DATE = "18 September 2026";
	/** complete version string */
	String VERSION_STRING = "5.4.931.0";
	/** proper noun, should NOT be translated / transliterated */
	String APPLICATION_NAME = "Locus";

	/** App versions */
	enum Version {
		CAS,
		GRAPHING,
		GRAPHING_3D,
		GEOMETRY,
		SCIENTIFIC,
		SUITE,
		MIXED_REALITY,
		NOTES,
		PROBABILITY,
		CLASSIC;

		/**
		 * @return translatable name of this app type
		 */
		public String getTransKey() {
			switch (this) {
				case GRAPHING:
					return "GeoGebraGraphingCalculator";
				case GRAPHING_3D:
					return "GeoGebra3DGrapher";
				case SCIENTIFIC:
					return "GeoGebraScientificCalculator";
				case CAS:
					return "GeoGebraCASCalculator";
				case GEOMETRY:
					return "GeoGebraGeometry";
				case NOTES:
					return "GeoGebraNotes";
				case SUITE:
					return "GeoGebraCalculatorSuite";
				default:
					return null;
			}
		}
	}

	/**
	 * Platform
	 */
	enum Platform {
		DESKTOP("d"),

		/** GeoGebra Graphing Calculator */
		ANDROID("a"),

		WEB("w"),

		IOS("i"),

		IOS_WEBVIEW("iw"),

		WEB_FOR_BROWSER_2D("w2d"),

		OFFLINE("offline"),

		SMART("smart"),

		POWERPOINT("p");

		private final String name;

		Platform(String name) {
			this.name = name;
		}

		public String getName() {
			return name;
		}

		/**
		 * @param prerelease
		 *            whether we run prerelease
		 * @return eg X.Y.Zd-prerelease
		 */
		public String getVersionString(boolean prerelease, String appCode) {

			StringBuilder suffix = new StringBuilder(10);
			suffix.append(name);
			if (!"classic".equals(appCode)) {
				suffix.append(appCode);
			}
			if (prerelease) {
				suffix.append("-prerelease");
			}

			// everything except old Java desktop version should be version
			// 6.0.x.x
			// change 5.4.274.0 to 6.0.274.0
			return (this == DESKTOP ? VERSION_STRING : getVersionString6()) + "-" + suffix;
		}

		/**
		 *
		 * @return true if this is a phone version.
		 */
		public boolean isPhone() {
			return "i".equals(name);
		}

		/**
		 * @return true if the current platform is either Android or iOS.
		 */
		public boolean isMobile() {
			return this == ANDROID || this == IOS;
		}
	}

	String SUITE_APPNAME = "GeoGebraCalculatorSuite";

	String GRAPHING_APPCODE = "graphing";
	String GEOMETRY_APPCODE = "geometry";
	String G3D_APPCODE = "3d";
	String SCIENTIFIC_APPCODE = "scientific";
	String CAS_APPCODE = "cas";
	String SUITE_APPCODE = "suite";
	String CLASSIC_APPCODE = "classic";
	String EVALUATOR_APPCODE = "evaluator";
	String NOTES_APPCODE = "notes";
	String PROBABILITY_APPCODE = "probability";
	String BAYERN_GRAPHING_APPCODE = "bayern_gr";
	String WTR_APPCODE = "wtr";

	String SUITE_SHORT_NAME = "CalculatorSuite.short";

	String SUITE_URL_NAME = "calculator";

	/**
	 * used by version checker, so that sys admins can disable version checking
	 * for *all* ggb versions with
	 * HKEY_LOCAL_MACHINE/Software/JavaSoft/Prefs/geogebra/version_check_allow =
	 * false
	 */
	String PREFERENCES_ROOT_GLOBAL = "/geogebra";

	/** root preferences node, eg HKEY_CURRENT_USER/Software/JavaSoft/Prefs/geogebra42/ */
	String PREFERENCES_ROOT = "/geogebra50";
	/** File format version */
	String XML_FILE_FORMAT = "5.0";

	// archive
	/** short version, for online archive */
	String SHORT_VERSION_STRING = "5.4";
	// File format versions
	/** XSD for ggb files */
	String GGB_XSD_FILENAME = "ggb.xsd";
	/** XSD for ggt (macro) files */
	String GGT_XSD_FILENAME = "ggt.xsd";
	// URLs

	/** http prefix */
	String HTTP = "http://";
	/** https prefix */
	String HTTPS = "https://";
	/** mailto prefix */
	String MAILTO = "mailto:";

	/** Website of GeoGebra GmbH, credited as the origin of Locus (link only, never fetched) */
	String GEOGEBRA_WEBSITE = "https://www.geogebra.org/";

	/** Source code repository of Locus */
	String LOCUS_SOURCE_URL = "https://github.com/arturict/locus";

	/** Where Locus users report problems */
	String LOCUS_ISSUES_URL = LOCUS_SOURCE_URL + "/issues";

	/** Public web address of Locus */
	String LOCUS_WEBSITE = "https://opengebra.arturf.ch/";

	/** Text of the EUPL 1.2, the licence of Locus */
	String EUPL_URL = "https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12";

	/**
	 * minimal precision in LocusEquation: by default rounding is at least 4
	 * decimals (this changes dynamically when zooming in)
	 */
	long PROVER_MIN_PRECISION = 10000;

	/** CSS class name for GeoGebraWeb container tag */
	String GGM_CLASS_NAME = "geogebraweb";
	/** mimetype of GGB files */
	String GGW_MIME_TYPE = "application/vnd.geogebra.file";
	String BYCS_LICENCE_URL = "https://www.bycs.de/rechtliche-dokumente/board/impressum/index.html";

	String REPORT_BUG_URL = LOCUS_ISSUES_URL;

	String EDIT_URL_BASE = "https://www.geogebra.org/material/edit/id/";

	/**
	 * Get the version string for versions 6.0.*
	 *
	 * @return version string
	 */
	static String getVersionString6() {
		return VERSION_STRING.replace("5.4.", "6.0.");
	}
}
