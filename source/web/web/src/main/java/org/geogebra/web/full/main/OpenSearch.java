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

package org.geogebra.web.full.main;

import org.geogebra.common.euclidian.EuclidianController;
import org.geogebra.common.ownership.GlobalScope;
import org.geogebra.web.full.gui.GuiManagerW;
import org.geogebra.web.full.gui.applet.GeoGebraFrameFull;
import org.geogebra.web.full.gui.layout.panels.AnimatingPanel;
import org.geogebra.web.full.gui.menubar.FileChooser;
import org.geogebra.web.full.gui.openfileview.HeaderFileView;
import org.geogebra.web.full.gui.openfileview.OpenTemporaryFileView;
import org.geogebra.web.html5.util.AppletParameters;

/**
 * Opens a file. Locus has no online materials, so outside of exams (which list
 * their temporary files) this shows the device's file picker.
 */
public final class OpenSearch {
	private final GeoGebraFrameFull frame;
	private final AppWFull app;
	private final GuiManagerW guiManager;
	private final AppletParameters appletParameters;
	private FileChooser fileChooser;

	/**
	 * @param app application
	 */
	public OpenSearch(AppWFull app) {
		this.app = app;
		frame = app.getAppletFrame();
		guiManager = app.getGuiManager();
		appletParameters = app.getAppletParameters();
	}

	/**
	 * @param query ignored; there is no online search
	 */
	public void show(String query) {
		app.hideMenu();
		if (hasSearchPerspective()) {
			clearPerspective();
		}
		if (GlobalScope.isExamActive(app)) {
			openInExamMode();
		} else {
			openFromDevice();
		}
	}

	private void openFromDevice() {
		if (fileChooser == null) {
			fileChooser = new FileChooser(app);
		}
		app.getAppletFrame().add(fileChooser);
		fileChooser.open();
	}

	private boolean hasSearchPerspective() {
		return appletParameters.getDataParamPerspective().startsWith("search:");
	}

	private void showBrowser(HeaderFileView fileView) {
		showBrowser(fileView.getPanel());
	}

	private void showBrowser(AnimatingPanel headerPanel) {
		EuclidianController evController = app.getActiveEuclidianView().getEuclidianController();
		if (evController != null) {
			evController.hideDynamicStylebar();
		}
		frame.setApplication(app);
		frame.showPanel(headerPanel);
	}

	private void clearPerspective() {
		appletParameters.setAttribute("perspective", "");
	}

	/**
	 * Show the temporary files of the running exam.
	 */
	public void openInExamMode() {
		app.hideMenu();
		OpenTemporaryFileView openFileView = (OpenTemporaryFileView) guiManager.getBrowseView();
		if (guiManager.isOpenFileViewLoaded()) {
			openFileView.loadAllMaterials(0);
		}
		showBrowser(openFileView);
	}
}
