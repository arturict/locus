/*
 * Locus - free mathematics software based on the source code of GeoGebra
 *
 * This file is part of Locus and licensed under the EUPL 1.2.
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package org.geogebra.web.full.gui.dialog;

import org.geogebra.common.GeoGebraConstants;
import org.geogebra.common.main.Localization;
import org.geogebra.web.html5.gui.BaseWidgetFactory;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.shared.components.dialog.ComponentDialog;
import org.geogebra.web.shared.components.dialog.DialogData;
import org.gwtproject.user.client.ui.FlowPanel;

import elemental2.dom.DomGlobal;
import elemental2.dom.HTMLAnchorElement;
import jsinterop.base.Js;

/**
 * About dialog of Locus: licence notice, credit to GeoGebra GmbH as the origin
 * of the source code, and links to the licence text and the source code. The
 * EUPL requires this attribution; it works offline because it is built in.
 */
public class AboutDialog extends ComponentDialog {

	/**
	 * @param app application
	 */
	public AboutDialog(AppW app) {
		super(app, new DialogData("AboutLicense", null, "OK"), true, true);
		addStyleName("aboutDialog");
		Localization loc = app.getLocalization();
		BaseWidgetFactory widgets = BaseWidgetFactory.INSTANCE;

		addDialogContent(widgets.newPrimaryText(GeoGebraConstants.APPLICATION_NAME + " "
				+ loc.getPlainDefault("VersionA", "Version %0",
				GeoGebraConstants.getVersionString6()), "aboutName"));
		addDialogContent(widgets.newSecondaryText(loc.getMenuDefault("Locus.AboutNotice",
				"Locus is free software under the EUPL 1.2, based on the source code of "
						+ "GeoGebra by GeoGebra GmbH (https://www.geogebra.org). Locus is not "
						+ "affiliated with or endorsed by GeoGebra GmbH."), "aboutNotice"));

		FlowPanel links = new FlowPanel();
		links.addStyleName("aboutLinks");
		addLink(links, loc.getMenuDefault("Locus.LicenceText", "Licence text (EUPL 1.2)"),
				GeoGebraConstants.EUPL_URL);
		addLink(links, loc.getMenuDefault("Locus.SourceCode", "Source code"),
				GeoGebraConstants.LOCUS_SOURCE_URL);
		addLink(links, loc.getMenuDefault("Locus.OriginalProject", "GeoGebra"),
				GeoGebraConstants.GEOGEBRA_WEBSITE);
		addDialogContent(links);
	}

	private static void addLink(FlowPanel parent, String text, String url) {
		HTMLAnchorElement link = Js.uncheckedCast(DomGlobal.document.createElement("a"));
		link.href = url;
		link.target = "_blank";
		link.rel = "noopener noreferrer";
		link.textContent = text;
		link.className = "aboutLink";
		parent.getElement().appendChild(Js.uncheckedCast(link));
	}
}
