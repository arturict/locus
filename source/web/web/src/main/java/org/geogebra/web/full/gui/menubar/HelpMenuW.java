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

package org.geogebra.web.full.gui.menubar;

import org.geogebra.common.GeoGebraConstants;
import org.geogebra.common.main.Localization;
import org.geogebra.web.full.css.MaterialDesignResources;
import org.geogebra.web.full.gui.menubar.action.ShowLicenseAction;
import org.geogebra.web.html5.gui.BaseWidgetFactory;
import org.geogebra.web.html5.gui.view.ImageIconSpec;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.resources.SVGResource;
import org.geogebra.web.shared.SharedResources;
import org.gwtproject.user.client.ui.Label;

/**
 * The help menu for Classic. Tutorials, manual, forum and privacy policy were
 * pages on geogebra.org, so Locus only offers its issue tracker and its own
 * About dialog.
 */
public final class HelpMenuW extends Submenu {

	/**
	 * @param app
	 *            application
	 */
	public HelpMenuW(final AppW app) {
		super("help", app);
		addExpandableStyleWithColor(false);
		Localization loc = app.getLocalization();
		addReportBugItem(app, loc);
		addAboutItem();
		addVersionNumber(app);
	}

	private void addReportBugItem(final AppW app, Localization loc) {
		addItem(MainMenu.getMenuBarItem(
				MaterialDesignResources.INSTANCE.bug_report_black(),
				loc.getMenu("ReportProblem"),
				new MenuCommand(app) {

					@Override
					void doExecute() {
						app.getFileManager().open(GeoGebraConstants.REPORT_BUG_URL);
					}
				}));
	}

	private void addAboutItem() {
		addItem(
				"AboutLicense",
				new ShowLicenseAction(),
				new ImageIconSpec(MaterialDesignResources.INSTANCE.info_black()));
	}

	private void addVersionNumber(AppW appW) {
		String versionNr = GeoGebraConstants.getVersionString6();
		String versionStr = appW.getLocalization().getPlainDefault("VersionA", "Version %0", versionNr);
		Label version = BaseWidgetFactory.INSTANCE.newDisabledText(versionStr, "versionNr");
		add(version);
	}

	@Override
	public SVGResource getImage() {
		return SharedResources.INSTANCE.icon_help_black();
	}

	@Override
	protected String getTitleTranslationKey() {
		return "HelpAndFeedback";
	}
}
