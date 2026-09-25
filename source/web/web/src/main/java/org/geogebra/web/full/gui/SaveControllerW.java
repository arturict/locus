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

package org.geogebra.web.full.gui;

import java.util.function.Consumer;

import org.geogebra.common.main.MaterialVisibility;
import org.geogebra.common.main.MaterialsManager;
import org.geogebra.common.main.SaveController;
import org.geogebra.common.move.ggtapi.models.Material;
import org.geogebra.common.move.ggtapi.models.Material.MaterialType;
import org.geogebra.common.util.AsyncOperation;
import org.geogebra.common.util.StringUtil;
import org.geogebra.common.util.debug.AccessibilityAnalytics;
import org.geogebra.common.util.debug.AccessibilityAnalyticsContext;
import org.geogebra.common.util.debug.Log;
import org.geogebra.gwtutil.FileSystemAPI;
import org.geogebra.web.full.gui.dialog.DialogManagerW;
import org.geogebra.web.full.main.FileManager;
import org.geogebra.web.html5.main.AppW;

import jsinterop.base.JsPropertyMap;

/**
 * Saves constructions. Locus has no online storage, so every save writes a
 * file to the user's device: through the browser's file system access API when
 * available, otherwise as a download.
 */
public final class SaveControllerW implements SaveController {

	private final AppW app;
	private MaterialType saveType = null;
	private AsyncOperation<Boolean> runAfterSave = null;

	private final LocalSaveOptions localSaveOptions;

	/**
	 * @param app application
	 */
	public SaveControllerW(AppW app) {
		this.app = app;
		localSaveOptions = new LocalSaveOptions(app);
	}

	/**
	 * Saves the active construction to the device under its current title.
	 * @param autoSaveCB called after the file was written
	 */
	@Override
	public void saveActiveMaterial(AsyncOperation<Boolean> autoSaveCB) {
		Material mat = app.getActiveMaterial();
		if (mat != null) {
			setSaveType(mat.getType());
		}
		showLocalSaveDialog(() -> autoSaveCB.callback(true));
	}

	@Override
	public void ensureTypeOtherThan(MaterialType type) {
		Material activeMaterial = app.getActiveMaterial();
		if (activeMaterial != null && activeMaterial.getType() == type) {
			app.getKernel().getConstruction().setTitle(null);
			app.setActiveMaterial(null);
		}
	}

	@Override
	public void showDialogIfNeeded(AsyncOperation<Boolean> saveCallback, boolean addTempCheckBox) {
		showDialogIfNeeded(saveCallback, !app.isSaved(), true, addTempCheckBox);
	}

	@Override
	public void showLocalSaveDialog(Runnable afterSave) {
		logSaveDialogShownIfNeeded();
		if (!FileSystemAPI.isSupported()) {
			app.getFileManager().export(app);
			logSaveCompleted();
			return;
		}

		JsPropertyMap<Object> options = localSaveOptions.asPropertyMap();

		FileSystemAPI.showSaveFilePicker(options).then(handle -> {
			((FileManager) app.getFileManager()).saveAs(handle, () -> {
				afterSave.run();
				logSaveCompleted();
			});
			return null;
		}).catch_(error -> {
			// the user closed the file picker without choosing a file
			Log.debug("Save to device cancelled: " + error);
			return null;
		});
	}

	/**
	 * Show the "do you want to save" dialog (or the save dialog) if needed,
	 * otherwise run the callback right away.
	 * @param runnable callback, receives whether the construction was saved
	 * @param needed whether there are unsaved changes
	 * @param doYouWantSaveChanges whether to ask before saving
	 * @param addTempCheckBox ignored; templates were an online feature
	 */
	public void showDialogIfNeeded(
			final AsyncOperation<Boolean> runnable,
			boolean needed,
			boolean doYouWantSaveChanges,
			boolean addTempCheckBox) {
		if (needed && !app.getLAF().isEmbedded()) {
			final Material oldActiveMaterial = app.getActiveMaterial();
			final String oldTitle = app.getKernel().getConstruction().getTitle();
			ensureTypeOtherThan(Material.MaterialType.ggsTemplate);
			setRunAfterSave(saved -> {
				if (!saved) {
					app.setActiveMaterial(oldActiveMaterial);
					app.getKernel().getConstruction().setTitle(oldTitle);
				}
				runnable.callback(saved);
			});
			DialogManagerW dm = (DialogManagerW) app.getDialogManager();
			logSaveDialogShownIfNeeded();
			if (doYouWantSaveChanges) {
				dm.getSaveCheckDialog().show();
			} else {
				dm.getSaveDialog().show();
			}
		} else {
			setRunAfterSave(null);
			runnable.callback(true);
		}
	}

	private void logSaveDialogShownIfNeeded() {
		AccessibilityAnalyticsContext context = app.getAccessibilityAnalyticsContext();
		if (context.isSaveDialogShown()) {
			return;
		}
		if (AccessibilityAnalytics.Value.UNSET.equals(context.getFlow())) {
			context.setFlow(AccessibilityAnalytics.Value.DIRECT);
		}
		context.markSaveDialogShown();
		AccessibilityAnalytics.logSaveShown(context.getTrigger(), context.getFlow());
	}

	private void logSaveCompleted() {
		AccessibilityAnalyticsContext context = app.getAccessibilityAnalyticsContext();
		if (context.isSaveDialogShown()) {
			AccessibilityAnalytics.logSaveCompleted(context.getTrigger(), context.getFlow());
			context.resetSave();
		}
	}

	/**
	 * Saves the construction to the device under the given title.
	 * @param name title of the construction, used as the suggested file name
	 * @param visibility ignored; there is no online visibility
	 * @param listener dialog to hide once the file picker takes over, may be null
	 */
	@Override
	public void saveAs(String name, MaterialVisibility visibility, SaveListener listener) {
		if (!StringUtil.empty(name)) {
			app.getKernel().getConstruction().setTitle(name);
		}
		if (listener != null) {
			listener.hide();
		}
		showLocalSaveDialog(() -> runAfterSaveCallback(true));
	}

	private static String getTitleOnly(String key) {
		return key.substring(key.indexOf("_", key.indexOf("_") + 1) + 1);
	}

	@Override
	public boolean isWorksheet() {
		return MaterialType.ggb == saveType || MaterialType.ggs == saveType;
	}

	@Override
	public void setSaveType(MaterialType saveType) {
		this.saveType = saveType;
	}

	@Override
	public MaterialType getSaveType() {
		return saveType;
	}

	@Override
	public boolean savedAsTemplate() {
		return MaterialType.ggsTemplate == getSaveType();
	}

	@Override
	public void runAfterSaveCallback(boolean activeMaterial) {
		if (runAfterSave != null) {
			AsyncOperation<Boolean> callback = runAfterSave;
			runAfterSave = null;
			callback.callback(activeMaterial);
		}
	}

	@Override
	public void dontSave() {
		app.getAccessibilityAnalyticsContext().reset();
		if (isWorksheet()) {
			app.setSaved();
			// run only if material active/created
			runAfterSaveCallback(app.getActiveMaterial() != null);
		}
	}

	@Override
	public void cancel() {
		app.getAccessibilityAnalyticsContext().reset();
		if (isWorksheet()) {
			// run only if material active/created
			runAfterSaveCallback(app.getActiveMaterial() != null);
		}
	}

	@Override
	public void setRunAfterSave(AsyncOperation<Boolean> runAfterSave) {
		this.runAfterSave = runAfterSave;
	}

	@Override
	public void updateSaveTitle(Consumer<String> title, String fallback) {
		String consTitle = app.getKernel().getConstruction().getTitle();
		if (!StringUtil.empty(consTitle)) {
			if (consTitle.startsWith(MaterialsManager.FILE_PREFIX)) {
				consTitle = getTitleOnly(consTitle);
			}
			title.accept(consTitle);
		} else {
			title.accept(fallback);
		}
	}
}
