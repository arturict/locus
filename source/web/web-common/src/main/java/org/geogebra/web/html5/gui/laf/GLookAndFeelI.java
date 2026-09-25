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

package org.geogebra.web.html5.gui.laf;

import org.geogebra.common.GeoGebraConstants.Platform;
import org.geogebra.common.move.ggtapi.models.ResourceAction;
import org.geogebra.web.html5.main.AppW;

import elemental2.promise.Promise;

/**
 * Look and feel properties.
 */
public interface GLookAndFeelI {
	int COMMAND_LINE_HEIGHT = 43;
	int TOOLBAR_HEIGHT = 53;

	/**
	 * @return whether this is SMART Notebook integration
	 */
	boolean isSmart();

	/**
	 * @return whether this is for tablets
	 */
	boolean isTablet();

	/**
	 * @return whether GeoGebra's own undo stack is supported
	 */
	boolean undoRedoSupported();

	/**
	 * Add window closing handler to prevent losing unsaved changes.
	 * @param app application
	 */
	void addWindowClosingHandler(AppW app);

	/**
	 * Remove window closing handler if supported.
	 * @see #addWindowClosingHandler(AppW)
	 */
	void removeWindowClosingHandler();

	/**
	 * @return whether copy to clipboard is supported
	 */
	boolean copyToClipboardSupported();

	/**
	 * @return whether auto-save is supported
	 */
	boolean autosaveSupported();

	/**
	 * @return whether export functionality is supported
	 */
	boolean exportSupported();

	/**
	 * @return whether the app is embedded in another system (SMART Notebook, PowerPoint)
	 */
	boolean isEmbedded();

	/**
	 * @return whether print is supported
	 */
	boolean printSupported();

	/**
	 * @param dim dimension
	 * @param appName app name
	 * @return platform
	 */
	Platform getPlatform(int dim, String appName);

	/**
	 * Store language code for next app start.
	 * @param language language code
	 */
	void storeLanguage(String language);

	/**
	 * @return user preferred language as promise (async in Chrome app)
	 */
	Promise<String> loadLanguage();

	/**
	 * Toggle fullscreen mode
	 * @param b whether to go fullscreen
	 */
	void toggleFullscreen(boolean b);

	/**
	 * @return whether we're in a browser that supports exam mode (ChromeOS app, Electron)
	 */
	boolean isOfflineExamSupported();

	/**
	 * Override action for a resource.
	 * @param action basic action
	 * @return overridden action
	 */
	ResourceAction getDisplayAction(ResourceAction action);

	/**
	 * Should be combined with app.isExamLocked() to check that the environment is
	 * currently locked.
	 * @return whether this environment supports locking
	 */
	default boolean hasLockedEnvironment() {
		return false;
	}

	/**
	 * @return whether help and feedback should be shown in main menu or not
	 */
	default boolean hasHelpMenu() {
		return true;
	}
}
