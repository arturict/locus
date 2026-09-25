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

package org.geogebra.common.main;

import org.geogebra.common.GeoGebraConstants;

/**
 * Creates an HTML page with an interactive Locus app showing the current construction.
 * The page loads Locus from its public website; it never refers to GeoGebra's servers.
 */
public class HTML5Export {

	/** Script that starts Locus on every element with the class "geogebraweb" */
	private static final String LOCUS_SCRIPT = GeoGebraConstants.LOCUS_WEBSITE
			+ "web3d/web3d.nocache.js";

	/**
	 * @param app
	 *            application
	 * @return complete HTML page
	 */
	public static String getFullString(App app) {
		StringBuilder sb = new StringBuilder();
		sb.append("<!DOCTYPE html>\n");
		sb.append("<html>\n");
		sb.append("<head>\n");

		// make sure scaling works
		sb.append("<meta name=viewport content=\"width=device-width,initial-scale=1\">\n");

		// make sure translation files loaded OK
		sb.append("<meta charset=\"utf-8\"/>\n");
		sb.append("<title>").append(GeoGebraConstants.APPLICATION_NAME).append("</title>\n");
		sb.append("</head>\n");
		sb.append("<body>\n");

		sb.append("<div class=\"").append(GeoGebraConstants.GGM_CLASS_NAME).append("\"");
		appendParam(sb, "id", "ggbApplet");
		appendParam(sb, "width", String.valueOf((int) app.getWidth()));
		appendParam(sb, "height", String.valueOf((int) app.getHeight()));
		appendParam(sb, "showMenuBar", String.valueOf(app.showMenuBar));
		appendParam(sb, "showAlgebraInput", String.valueOf(app.showAlgebraInput));
		appendParam(sb, "showToolBar", String.valueOf(app.showToolBar));
		GuiManagerInterface gui = app.getGuiManager();
		if (app.showToolBar) {
			if (gui != null) {
				appendParam(sb, "customToolBar", gui.getToolbarDefinition());
			}
			appendParam(sb, "showToolBarHelp", String.valueOf(app.showToolBarHelp));
		}
		appendParam(sb, "showResetIcon", "false");
		appendParam(sb, "enableLabelDrags", "false");
		appendParam(sb, "enableShiftDragZoom", "true");
		appendParam(sb, "enableRightClick", "false");
		appendParam(sb, "errorDialogsActive", "false");
		appendParam(sb, "useBrowserForJS", "false");
		appendParam(sb, "allowStyleBar", "false");
		appendParam(sb, "preventFocus", "false");
		appendParam(sb, "showZoomButtons", "true");
		appendParam(sb, "capturingThreshold", "3");
		appendParam(sb, "showFullscreenButton", "true");
		appendParam(sb, "scale", "1");
		appendParam(sb, "disableAutoScale", "false");
		appendParam(sb, "allowUpscale", "false");
		appendParam(sb, "appName", app.getConfig().getAppCode());
		appendParam(sb, "buttonRounding", "0.7");
		appendParam(sb, "buttonShadows", "false");
		appendParam(sb, "language", app.getLocalization().getLanguageTag());
		// don't include preview bitmap
		appendParam(sb, "ggbBase64", app.getGgbApi().getBase64(false));
		sb.append("></div>\n");

		sb.append("<script src=\"").append(LOCUS_SCRIPT).append("\"></script>\n");
		sb.append("</body>\n");
		sb.append("</html>\n");

		return sb.toString();
	}

	private static void appendParam(StringBuilder sb, String name, String value) {
		sb.append("\n  data-param-").append(name).append("=\"")
				.append(value == null ? "" : value.replace("&", "&amp;").replace("\"", "&quot;"))
				.append('"');
	}
}
