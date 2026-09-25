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


import org.geogebra.common.euclidian.EmbedManager;
import org.geogebra.common.kernel.geos.GeoElement;
import org.geogebra.common.kernel.geos.GeoEmbed;
import org.geogebra.common.media.MediaURLParser;
import org.geogebra.common.move.ggtapi.operations.URLChecker;
import org.geogebra.common.move.ggtapi.operations.URLStatus;
import org.geogebra.common.util.AsyncOperation;
import org.geogebra.web.full.gui.dialog.MediaDialog;
import org.geogebra.web.full.gui.dialog.MediaInputPanel;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.shared.ggtapi.MarvlURLChecker;
import org.gwtproject.dom.client.Element;
import org.gwtproject.dom.client.NodeList;
import org.gwtproject.user.client.DOM;

/**
 * Adds web pages as embedded elements. Links to GeoGebra materials used to be
 * resolved through GeoGebra's materials server; Locus treats them like any
 * other web page.
 */
public final class EmbedFactory implements AsyncOperation<URLStatus> {
	private URLChecker urlChecker;
	final AppW app;
	private Runnable hideDialogCallback;
	private MediaInputPanel mediaInputPanel;

	/**
	 * constructor
	 * @param app see {@link AppW}
	 * @param mediaInputPanel input text field
	 */
	public EmbedFactory(AppW app, MediaInputPanel mediaInputPanel) {
		this.app = app;
		this.mediaInputPanel = mediaInputPanel;
		initURLChecker();
	}

	/**
	 * @return url checker
	 */
	public URLChecker getUrlChecker() {
		return urlChecker;
	}

	private void initURLChecker() {
		// checks the URL locally, without asking a server
		urlChecker = new MarvlURLChecker();
	}

	/**
	 * Adds the GeoEmbed instance.
	 */
	public void addEmbed() {
		String input = mediaInputPanel.getInput();
		mediaInputPanel.resetError();
		String url = extractURL(input);
		if (!input.startsWith("<")) {
			mediaInputPanel.setText(url);
		}
		urlChecker.check(MediaURLParser.toEmbeddableUrl(url), this);
	}

	private static String extractURL(String input) {
		if (input.startsWith("<")) {
			Element el = DOM.createDiv();
			el.setInnerHTML(input);
			NodeList<Element> frames = el.getElementsByTagName("iframe");
			if (frames.getLength() > 0) {
				return MediaDialog.addProtocol(frames.getItem(0).getAttribute("src"));
			}
		}
		return MediaDialog.addProtocol(input);
	}

	private GeoElement createAndShowEmbeddedElement(String url) {
		GeoEmbed ge = new GeoEmbed(app.getKernel().getConstruction());
		ge.setUrl(url);
		ge.setAppName("extension");
		ge.initDefaultPosition(app.getActiveEuclidianView());
		EmbedManager embedManager = app.getEmbedManager();
		if (embedManager != null) {
			ge.setEmbedId(embedManager.nextID());
		}
		ge.setLabel(null);
		app.storeUndoInfo();

		return ge;
	}

	@Override
	public void callback(URLStatus obj) {
		if (obj.getErrorKey() == null) {
			GeoElement geo = createAndShowEmbeddedElement(obj.getUrl());
			runHideCallback();
			app.getActiveEuclidianView().getEuclidianController().selectAndShowSelectionUI(geo);
		} else {
			mediaInputPanel.showError(obj.getErrorKey());
		}
	}

	public void setHideDialogCallback(Runnable callback) {
		hideDialogCallback = callback;
	}

	/**
	 * hide dialog and set defined mode
	 */
	public void runHideCallback() {
		if (hideDialogCallback != null) {
			hideDialogCallback.run();
		}
	}
}
