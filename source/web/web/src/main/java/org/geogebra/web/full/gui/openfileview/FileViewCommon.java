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

package org.geogebra.web.full.gui.openfileview;

import org.geogebra.common.exam.ExamController;
import org.geogebra.common.ownership.GlobalScope;
import org.geogebra.web.full.gui.HeaderView;
import org.geogebra.web.full.gui.exam.ExamLogAndExitDialog;
import org.geogebra.web.full.gui.layout.panels.AnimatingPanel;
import org.geogebra.web.full.gui.layout.scientific.SettingsAnimator;
import org.geogebra.web.full.gui.toolbar.mow.toolbox.components.IconButton;
import org.geogebra.web.html5.gui.laf.LoadSpinner;
import org.geogebra.web.html5.gui.util.Dom;
import org.geogebra.web.html5.gui.view.ImageIconSpec;
import org.geogebra.web.html5.gui.view.button.StandardButton;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.html5.main.LocalizationW;
import org.geogebra.web.html5.util.CSSEvents;
import org.geogebra.web.html5.util.Persistable;
import org.geogebra.web.shared.SharedResources;
import org.geogebra.web.shared.components.infoError.ComponentInfoErrorPanel;
import org.geogebra.web.shared.components.infoError.InfoErrorData;
import org.gwtproject.animation.client.AnimationScheduler;
import org.gwtproject.user.client.ui.FlowPanel;
import org.gwtproject.user.client.ui.Label;
import org.gwtproject.user.client.ui.Widget;

public final class FileViewCommon extends AnimatingPanel implements Persistable {

	private final AppW app;
	private final String title;
	// header
	private HeaderView headerView;

	// content panel
	private FlowPanel contentPanel;
	// material panel
	private FlowPanel materialPanel;
	private final LocalizationW loc;
	private IconButton examInfoBtn;
	private Label timer;
	private FlowPanel emptyListNotificationPanel;
	private LoadSpinner spinner;
	private final ExamController examController;

	/**
	 * @param app the application
	 * @param title the header title key.
	 */
	public FileViewCommon(AppW app, String title) {
		loc = app.getLocalization();
		this.app = app;
		this.title = title;
		this.examController = GlobalScope.getExamController(app);
		setAnimator(new SettingsAnimator(app.getAppletFrame(), this));
		initGUI();
	}

	private void initGUI() {
		this.setStyleName("openFileView");
		addStyleName("panelFadeIn");
		initHeader();
		initContentPanel();
		initSpinner();
		initMaterialPanel();
		setLabels();
	}

	private void initMaterialPanel() {
		materialPanel = new FlowPanel();
		materialPanel.addStyleName("materialPanel");
	}

	private void initHeader() {
		headerView = new HeaderView(app);
		headerView.setCaption(title);
		IconButton backButton = headerView.getBackButton();
		backButton.addFastClickHandler(source -> {
			updateAnimateOutStyle();
			CSSEvents.runOnAnimation(this::close, getElement(), getAnimateOutStyle());
		});

		if (!examController.isIdle()) {
			addExamPanel();
		}
		this.setHeaderWidget(headerView);
	}

	private void addExamPanel() {
		addExamTimeLabel();
		addExamInfoButton();
	}

	private void addExamTimeLabel() {
		timer = new Label("0:00");
		timer.setStyleName("examTimer");
		// run timer
		AnimationScheduler.get().requestAnimationFrame(new AnimationScheduler.AnimationCallback() {
			@Override
			public void execute(double timestamp) {
				if (!examController.isIdle()) {
					timer.setText(examController.getDurationFormatted(loc));
					AnimationScheduler.get().requestAnimationFrame(this);
				}
			}
		});
		headerView.add(timer);
	}

	private void addExamInfoButton() {
		examInfoBtn = new IconButton(
				app, () -> {}, new ImageIconSpec(SharedResources.INSTANCE.info_black()), "exam_log_header");
		examInfoBtn.addStyleName("examInfoBtn");
		examInfoBtn.addFastClickHandler(source -> showExamDialog(examInfoBtn));
		headerView.add(examInfoBtn);
	}

	private void showExamDialog(StandardButton examInfoBtn) {
		new ExamLogAndExitDialog(app, true, examInfoBtn).show();
	}

	private void initContentPanel() {
		contentPanel = new FlowPanel();
		contentPanel.setStyleName("fileViewContentPanel");
		this.setContentWidget(contentPanel);
	}

	/**
	 * adds content if available
	 */
	public void addContent() {
		if (emptyListNotificationPanel != null) {
			emptyListNotificationPanel.removeFromParent();
		}
		contentPanel.add(materialPanel);
	}

	/**
	 * Clear contents
	 */
	public void clearPanels() {
		if (contentPanel != null) {
			contentPanel.clear();
		}
	}

	/**
	 * remove empty notification panel
	 */
	public void removeEmptyInfoPanel() {
		if (emptyListNotificationPanel != null) {
			emptyListNotificationPanel.removeFromParent();
		}
	}

	@Override
	public void setLabels() {
		headerView.setCaption(localize(title));
	}

	@Override
	public AppW getApp() {
		return app;
	}

	@Override
	public void resizeTo(int width, int height) {
		onResize();
	}

	@Override
	public void onResize() {
		super.onResize();
		resizeHeader();
	}

	/**
	 * update header style on resize
	 */
	public void resizeHeader() {
		boolean smallScreen = app.getAppletFrame().hasSmallWindowOrCompactHeader();
		headerView.resizeTo(smallScreen);
		Dom.toggleClass(contentPanel, "compact", smallScreen);
	}

	/**
	 * Clear the materials panel.
	 */
	public void clearMaterials() {
		materialPanel.clear();
	}

	void showEmptyListNotification(InfoErrorData data) {
		if (materialPanel != null) {
			materialPanel.removeFromParent();
		}
		if (emptyListNotificationPanel != null) {
			emptyListNotificationPanel.removeFromParent();
		}
		emptyListNotificationPanel = getEmptyListNotificationPanel(data);
		contentPanel.add(emptyListNotificationPanel);
	}

	private FlowPanel getEmptyListNotificationPanel(InfoErrorData data) {
		return new ComponentInfoErrorPanel(loc, data, null);
	}

	String localize(String key) {
		return loc.getMenu(key);
	}

	/**
	 *
	 * @param card to add.
	 */
	public void addMaterialCard(Widget card) {
		materialPanel.add(card);
	}

	/**
	 * Add to content panel.
	 *
	 * @param widget widget to add
	 */
	public void addToContent(Widget widget) {
		contentPanel.add(widget);
	}

	/**
	 * Clear content panel.
	 */
	public void clearContents() {
		contentPanel.clear();
	}

	/**
	 * @return whether it's empty.
	 */
	public boolean hasNoMaterials() {
		return materialCount() == 0;
	}

	/**
	 * @return Number of widgets (material cards + more button).
	 */
	public int materialCount() {
		return materialPanel.getWidgetCount();
	}

	/**
	 * @param index index
	 * @return material card at given position
	 */
	public Widget materialAt(int index) {
		return materialPanel.getWidget(index);
	}

	/**
	 * Add a widget (material card or more button) to the panel.
	 * @param widget widget
	 */
	public void addMaterialOrLoadMoreFilesPanel(Widget widget) {
		materialPanel.add(widget);
	}

	/**
	 * Insert a material card at given position.
	 * @param widget material card
	 * @param idx index
	 */
	public void insertMaterial(Widget widget, int idx) {
		materialPanel.insert(widget, idx);
	}

	public HeaderView getHeader() {
		return headerView;
	}

	private void initSpinner() {
		spinner = new LoadSpinner();
		addToContent(spinner);
	}

	/**
	 * show loading wheel
	 */
	public void showSpinner() {
		spinner.show();
	}

	/**
	 * hide loading wheel
	 */
	public void hideSpinner() {
		spinner.hide();
	}
}
