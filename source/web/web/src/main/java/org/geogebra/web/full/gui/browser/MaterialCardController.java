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

package org.geogebra.web.full.gui.browser;

import org.geogebra.common.main.OpenFileListener;
import org.geogebra.common.move.ggtapi.models.Material;
import org.geogebra.common.util.debug.Log;
import org.geogebra.web.full.gui.openfileview.MaterialCardI;
import org.geogebra.web.full.gui.openfileview.RemoveDialog;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.shared.components.dialog.ComponentDialog;
import org.geogebra.web.shared.components.dialog.DialogData;

/**
 * Controller for the cards of locally stored materials (the exam's temporary
 * files). Locus has no online materials, so nothing here contacts a server.
 */
public final class MaterialCardController implements OpenFileListener {
	/** application */
	private final AppW app;

	private Material material;
	/** callback for deleting materials */
	private final Runnable deleteCallback;

	/**
	 * @param app
	 *            application
	 */
	public MaterialCardController(AppW app) {
		this.app = app;
		deleteCallback = () -> {
			Log.debug("DELETE finished");
			app.getGuiManager().getBrowseView().setMaterialsDefaultStyle();
		};
	}

	/**
	 * @return current material
	 */
	public Material getMaterial() {
		return material;
	}

	/**
	 * @param material
	 *            current material
	 */
	public void setMaterial(Material material) {
		this.material = material;
	}

	/**
	 * Remove the material from the device and its card from the UI.
	 *
	 * @param card
	 *            card to be deleted
	 */
	public void onConfirmDelete(final MaterialCardI card) {
		card.setVisible(false);
		app.getGuiManager().getBrowseView().setMaterialsDefaultStyle();
		final Material toDelete = this.getMaterial();
		Log.debug("DELETE permanent");
		this.app
				.getFileManager()
				.delete(toDelete, toDelete.getSharingKey() == null, this.deleteCallback);
	}

	/**
	 * @return callback for deleting materials
	 */
	public Runnable getDeleteCallback() {
		return deleteCallback;
	}

	@Override
	public boolean onOpenFile() {
		app.getKernel().getConstruction().setTitle(null);
		app.setActiveMaterial(material);
		return true; // one time only
	}

	/**
	 * show confirmation dialog for delete
	 * @param card material/template/temporary card
	 */
	public void showDeleteConfirmDialog(MaterialCardI card) {
		DialogData data = new DialogData(null, "Cancel", "Delete");
		ComponentDialog removeDialog = new RemoveDialog(app, data, card);
		removeDialog.show();
		removeDialog.setOnPositiveAction(() -> onConfirmDelete(card));
	}
}
