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

import org.geogebra.common.gui.menu.Icon;
import org.geogebra.common.main.Localization;
import org.geogebra.common.ownership.GlobalScope;
import org.geogebra.editor.share.util.Unicode;
import org.geogebra.web.full.css.MaterialDesignResources;
import org.geogebra.web.full.gui.menu.icons.DefaultMenuIconProvider;
import org.geogebra.web.full.gui.menu.icons.MenuIconResource;
import org.geogebra.web.full.gui.menubar.action.ClearAllAction;
import org.geogebra.web.full.gui.menubar.action.ExitExamAction;
import org.geogebra.web.full.gui.menubar.action.ExportImage;
import org.geogebra.web.full.gui.menubar.action.SaveLocalAction;
import org.geogebra.web.html5.gui.menu.AriaMenuItem;
import org.geogebra.web.html5.gui.view.ImageIconSpec;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.resources.SVGResource;

/**
 * Web implementation of FileMenu
 */
public final class FileMenuW extends Submenu {

	private final Localization loc;
	private final MenuIconResource iconProvider;

	/**
	 * @param app
	 *            application
	 */
	public FileMenuW(final AppW app) {
		super("file", app);
		addExpandableStyleWithColor(false);
		this.loc = app.getLocalization();
		iconProvider = new MenuIconResource(new DefaultMenuIconProvider());
		initActions();
	}

	private void initActions() {
		if (GlobalScope.isExamActive(getApp())) {
			addItem("exam_menu_exit", new ExitExamAction(), iconProvider.getImageResource(Icon.SIGN_OUT));
			return;
		}

		buildFileMenu();
	}

	private void buildFileMenu() {
		// Locus has no online storage: open and save work with files on the device
		addFileNewItem();
		addOpenFileItem();
		addSaveItems();
		addSeparator();
		addExportImageItem();
		addDownloadAsItem();
		addPrintItem();
	}

	@Override
	public SVGResource getImage() {
		return MaterialDesignResources.INSTANCE.fileMenu();
	}

	@Override
	protected String getTitleTranslationKey() {
		return "File";
	}

	private void addFileNewItem() {
		addItem(
				"New",
				new ClearAllAction(true),
				new ImageIconSpec(MaterialDesignResources.INSTANCE.newFileMenu()));
	}

	private void addExportImageItem() {
		addItem("exportImage", new ExportImage(), iconProvider.getImageResource(Icon.EXPORT_IMAGE));
	}

	private void addSaveItems() {
		if (getApp().getLAF().undoRedoSupported()) {
			addItem("SaveToYourPC", new SaveLocalAction(), iconProvider.getImageResource(Icon.SAVE));
		}
	}

	private void addOpenFileItem() {
		addItem(MainMenu.getMenuBarItem(
				MaterialDesignResources.INSTANCE.openFileMenu(),
				loc.getMenu("Open"),
				new MenuCommand(getApp()) {

					@Override
					void doExecute() {
						app.openSearch(null);
					}
				}));
	}

	private void addDownloadAsItem() {
		if (getApp().getLAF().exportSupported()) {
			AriaMenuItem export = addItem(new AriaMenuItem(
					loc.getMenu("DownloadAs") + Unicode.ELLIPSIS,
					MaterialDesignResources.INSTANCE.file_download_black(),
					new ExportMenuW(getApp())));
			export.setScheduledCommand(getSubmenuCommand(export, true));
		}
	}

	private void addPrintItem() {
		if (getApp().getLAF().printSupported()) {
			AriaMenuItem printItem = MainMenu.getMenuBarItem(
					MaterialDesignResources.INSTANCE.print_black(),
					loc.getMenu("PrintPreview"),
					new MenuCommand(getApp()) {
						@Override
						void doExecute() {
							getApp().getDialogManager().showPrintPreview();
						}
					});
			// updatePrintMenu();
			addItem(printItem);
		}
	}
}
