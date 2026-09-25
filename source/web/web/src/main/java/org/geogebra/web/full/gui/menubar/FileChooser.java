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

import org.geogebra.web.html5.main.AppW;
import org.gwtproject.dom.style.shared.Display;
import org.gwtproject.event.dom.client.ChangeEvent;
import org.gwtproject.event.dom.client.ChangeHandler;
import org.gwtproject.user.client.ui.FileUpload;

import elemental2.dom.File;
import elemental2.dom.HTMLInputElement;
import jsinterop.base.Js;

/**
 * Invisible file input that lets the user open a construction from the device.
 */
public final class FileChooser extends FileUpload implements ChangeHandler {
	/** File types that {@link AppW#openFile(File)} can open */
	private static final String ACCEPTED_TYPES = ".ggb,.ggs,.ggt,.csv,.off";

	private AppW app;

	/**
	 * Constructor
	 * @param app AppW
	 */
	public FileChooser(AppW app) {
		super();
		this.app = app;
		addChangeHandler(this);
		getElement().setAttribute("accept", ACCEPTED_TYPES);
		// the input is only opened programmatically and must never show up in the layout
		getElement().getStyle().setDisplay(Display.NONE);
	}

	/**
	 * Open the system file chooser.
	 */
	public void open() {
		click();
	}

	@Override
	public void onChange(ChangeEvent event) {
		File selectedFile = getSelectedFile();
		app.checkSaved(success -> app.openFile(selectedFile));
		this.removeFromParent();
	}

	private File getSelectedFile() {
		HTMLInputElement fileInput = Js.uncheckedCast(getElement());
		File fileToHandle = fileInput.files.getAt(0);
		fileInput.value = "";
		return fileToHandle;
	}
}
