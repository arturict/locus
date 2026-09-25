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

package org.geogebra.web.shared;

import static org.geogebra.common.gui.AccessibilityGroup.REDO_SCI_CALC;
import static org.geogebra.common.gui.AccessibilityGroup.SETTINGS;
import static org.geogebra.common.gui.AccessibilityGroup.UNDO_SCI_CALC;

import java.util.ArrayList;

import org.geogebra.common.exam.ExamController;
import org.geogebra.common.exam.ExamListener;
import org.geogebra.common.exam.ExamState;
import org.geogebra.common.exam.ExamType;
import org.geogebra.common.gui.AccessibilityGroup;
import org.geogebra.common.main.OptionType;
import org.geogebra.common.main.undo.UndoRedoButtonsController;
import org.geogebra.common.ownership.GlobalScope;
import org.geogebra.gwtutil.JavaScriptInjector;
import org.geogebra.gwtutil.SafeExamBrowser;
import org.geogebra.web.full.css.MaterialDesignResources;
import org.geogebra.web.full.gui.exam.ExamUtil;
import org.geogebra.web.full.gui.menu.icons.DefaultMenuIconResources;
import org.geogebra.web.full.gui.toolbar.mow.toolbox.components.IconButton;
import org.geogebra.web.full.gui.toolbarpanel.MenuToggleButton;
import org.geogebra.web.html5.GeoGebraGlobal;
import org.geogebra.web.html5.gui.util.Dom;
import org.geogebra.web.html5.gui.view.ImageIconSpec;
import org.geogebra.web.html5.gui.zoompanel.FocusableWidget;
import org.geogebra.web.html5.main.AppW;
import org.geogebra.web.html5.util.StringConsumer;
import org.geogebra.web.shared.view.button.ActionButton;
import org.gwtproject.animation.client.AnimationScheduler;
import org.gwtproject.animation.client.AnimationScheduler.AnimationCallback;
import org.gwtproject.dom.client.Document;
import org.gwtproject.dom.client.Element;
import org.gwtproject.dom.style.shared.Display;
import org.gwtproject.resources.client.TextResource;
import org.gwtproject.user.client.DOM;
import org.gwtproject.user.client.ui.FlowPanel;
import org.gwtproject.user.client.ui.HTML;
import org.gwtproject.user.client.ui.Image;
import org.gwtproject.user.client.ui.Label;
import org.gwtproject.user.client.ui.RootPanel;
import org.gwtproject.user.client.ui.Widget;
import org.jspecify.annotations.Nullable;

import elemental2.core.Function;
import elemental2.core.JsArray;
import elemental2.dom.DomGlobal;
import jsinterop.base.Js;

/**
 * Singleton representing external header bar of unbundled apps.
 */
public final class GlobalHeader implements ExamListener {
	/**
	 * Singleton instance.
	 */
	public static final GlobalHeader INSTANCE = new GlobalHeader();

	private MenuToggleButton menuBtn;
	private AppW app;
	private Label timer;
	private IconButton examInfoBtn;

	private ActionButton undoButton;
	private ActionButton redoButton;
	private ActionButton settingsButton;
	private @Nullable FlowPanel examTypeHolder;
	private String examHash;
	private ExamController examController;

	private final ArrayList<FocusableWidget> focusableWidgets = new ArrayList<>();

	/**
	 * Singleton constructor
	 */
	private GlobalHeader() {}

	public static String getExamHash() {
		return INSTANCE.examHash;
	}

	/**
	 * Get element, NOT panel to make sure root panels are not nested
	 *
	 * @return element containing the buttons in header
	 */
	public static Element getButtonElement() {
		return Document.get().getElementById("buttonsID");
	}

	/**
	 * @return panel of exam timer
	 */
	public RootPanel getExamPanel() {
		return RootPanel.get("examId");
	}

	/**
	 * @return application
	 */
	public AppW getApp() {
		return app;
	}

	/**
	 * @return exam timer
	 */
	public Label getTimer() {
		return timer;
	}

	/**
	 * Initialize the settings, undo and redo buttons if they are on the header
	 */
	public void initButtonsIfOnHeader() {
		if (app != null) {
			initSettingButtonIfOnHeader();
			initUndoRedoButtonsIfOnHeader();
		}
	}

	private void initSettingButtonIfOnHeader() {
		if (settingsButton == null) {
			settingsButton = getActionButton("settingsButton", "Settings", SETTINGS);
			if (settingsButton != null) {
				settingsButton.setAction(() -> {
					FocusableWidget focusableWidget = getSettingsFocusableWidget();
					if (focusableWidget != null) {
						app.getAccessibilityManager().setAnchor(focusableWidget);
					}
					app.getDialogManager().showPropertiesDialog(OptionType.GLOBAL, null);
				});
			}
		}
	}

	private @Nullable FocusableWidget getSettingsFocusableWidget() {
		for (FocusableWidget focusableWidget : focusableWidgets) {
			if (focusableWidget.getAccessibilityGroup() == SETTINGS) {
				return focusableWidget;
			}
		}
		return null;
	}

	private void initUndoRedoButtonsIfOnHeader() {
		if (undoButton == null || redoButton == null) {
			undoButton = getUndoButton();
			redoButton = getRedoButton();
			if (undoButton != null && redoButton != null) {
				UndoRedoButtonsController.addUndoRedoFunctionality(undoButton, redoButton, app.getKernel());
			}
		}
	}

	private ActionButton getUndoButton() {
		return getActionButton("undoButton", "Undo", UNDO_SCI_CALC);
	}

	private ActionButton getRedoButton() {
		return getActionButton("redoButton", "Redo", REDO_SCI_CALC);
	}

	private ActionButton getActionButton(String viewId, String title, AccessibilityGroup group) {
		RootPanel view = getViewById(viewId);
		if (view != null) {
			registerFocusable(app, group, view);
			return new ActionButton(app, view, title);
		}
		return null;
	}

	private static RootPanel getViewById(String viewId) {
		return RootPanel.get(viewId);
	}

	/**
	 * remove exam timer and put back button panel
	 */
	public void resetAfterExam() {
		if (getExamPanel() != null) {
			getExamPanel().getElement().removeFromParent();
		}
		if (getButtonElement() == null) {
			return;
		}
		getButtonElement().getStyle().clearDisplay();
		onResize();
	}

	/**
	 * switch right buttons with exam timer and info button
	 */
	public void addExamTimer(AppW app) {
		AnimationScheduler.get().requestAnimationFrame(new AnimationCallback() {
			@Override
			public void execute(double timestamp) {
				if (examController != null && examController.isExamActive()) {
					if (examController.isCheating()) {
						app.getGuiManager().updateUnbundledToolbarStyle();
						if (examTypeHolder != null) {
							examTypeHolder.addStyleName("cheat");
						}
					}
					if (getTimer() != null) {
						getTimer().setText(examController.getDurationFormatted(app.getLocalization()));
					}
					AnimationScheduler.get().requestAnimationFrame(this);
				}
			}
		});
		if (examController == null) {
			initSafeExamBrowser(hash -> {});
			return;
		}

		// exam panel with timer and info btn
		Image timerImg =
				new Image(MaterialDesignResources.INSTANCE.timer().getSafeUri().asString());
		timerImg.addStyleName("timerImg");
		timer = new Label("0:00");
		timer.setStyleName("examTimer");
		examInfoBtn = new IconButton(
				app, () -> {}, new ImageIconSpec(SharedResources.INSTANCE.info_black()), "exam_log_header");
		examInfoBtn.addStyleName("examInfoBtn");
		Element exam = DOM.createDiv();
		exam.setId("examId");
		if (getButtonElement() != null) {
			// page header with buttons: show the exam panel in place of the buttons
			getButtonElement().getStyle().setDisplay(Display.NONE);
			getButtonElement().getParentElement().appendChild(exam);
		} else {
			// Locus app pages have no page header: float the panel over the app so the
			// timer and the exam log stay visible during the exam
			exam.addClassName("examPanelStandalone");
			exam.setAttribute("style", "position:fixed;top:8px;left:50%;transform:translateX(-50%);"
					+ "z-index:1000;height:auto;padding:4px 8px;background:#ffffff;"
					+ "border-radius:999px;box-shadow:0 4px 16px rgba(20,24,28,.16);");
			Document.get().getBody().appendChild(exam);
		}
		// The link should be disabled in all exam-capable apps since APPS-3289, but make sure
		Element logo = Dom.querySelector("#logoID");
		if (logo != null) {
			logo.setAttribute("href", "#");
			logo.addClassName("hideButton");
		}
		RootPanel examId = RootPanel.get("examId");
		examId.addStyleName("examPanel");

		ExamType examType = examController.getExamType();
		if (SafeExamBrowser.get() != null && SafeExamBrowser.get().security != null) {
			initSafeExamBrowser(hash -> addExamType("Safe Exam Browser (" + hash + ")"));
		} else if (examType != ExamType.GENERIC && examType != null) {
			addExamType(examType.getDisplayName(app.getLocalization(), app.getConfig()));
		}

		examId.add(timerImg);
		examId.add(timer);
		examId.add(examInfoBtn);
		examInfoBtn.addFastClickHandler(source -> app.getGuiManager().showExamInfoDialog(examInfoBtn));
		// run timer
		onResize();
	}

	private void initSafeExamBrowser(StringConsumer onHashChange) {
		if (SafeExamBrowser.get() == null || SafeExamBrowser.get().security == null) {
			return;
		}
		if (Js.isFalsy(GeoGebraGlobal.ggbCallbacks)) {
			GeoGebraGlobal.ggbCallbacks = JsArray.of();
			TextResource globalScript = new TextResource() {
				@Override
				public String getText() {
					return "function runCallbacks() {window.ggbCallbacks.forEach(f=>f());"
							+ "window.ggbCallbacks.splice(0);}";
				}

				@Override
				public String getName() {
					return "seb-global";
				}
			};
			JavaScriptInjector.inject(globalScript);
		}
		SafeExamBrowser.SebSecurity security = SafeExamBrowser.get().security;
		GeoGebraGlobal.ggbCallbacks.push(() -> {
			examHash = security.configKey.substring(0, 8);
			onHashChange.consume(examHash);
		});
		security.updateKeys(GeoGebraGlobal.runCallbacks);
	}

	private void addExamType(String examTypeName) {
		HTML examImg = new HTML(DefaultMenuIconResources.INSTANCE.assignment().getSVG());
		examImg.setStyleName("examTypeIcon");
		Label examType = new Label(examTypeName);
		examType.setStyleName("examType");
		FlowPanel examTypePanel = new FlowPanel();
		examTypePanel.getElement().setId("examTypeId");
		examTypePanel.addStyleName("examTypePanel");
		if (app != null && ExamUtil.hasExternalSecurityCheck(app)) {
			examTypePanel.addStyleName("locked");
		}
		examTypePanel.add(examImg);
		examTypePanel.add(examType);
		this.examTypeHolder = examTypePanel;
		RootPanel.get("examId").add(examTypePanel);
	}

	/**
	 * Show/hide apps picker as needed
	 */
	public static void onResize() {
		Function resize = GeoGebraGlobal.getGgbHeaderResize();
		if (resize != null) {
			resize.call();
		}
	}

	/**
	 * Initialize without creating any buttons.
	 *
	 * @param app
	 *            application
	 */
	public void setApp(AppW app) {
		this.app = app;
		ExamController controller = GlobalScope.getExamController(app);
		if (controller != null && controller != examController) {
			examController = controller;
			examController.addListener(this);
		}
	}

	/**
	 * @return whether there is a header in DOM
	 */
	public static boolean isInDOM() {
		return RootPanel.get("logoID") != null;
	}

	/**
	 * update ui on language change
	 */
	public void setLabels() {
		if (menuBtn != null) {
			menuBtn.setLabel();
		}
	}

	public void setMenuBtn(MenuToggleButton menuBtn) {
		this.menuBtn = menuBtn;
	}

	/**
	 * initialize logo
	 * @param app - application
	 */
	public void initLogo(AppW app) {
		RootPanel logo = RootPanel.get("logoID");
		if (logo != null) {
			registerFocusable(app, AccessibilityGroup.GEOGEBRA_LOGO, logo);
			Dom.addEventListener(logo.getElement(), "click", (e) -> {
				e.stopPropagation();
				e.preventDefault();
				String link = logo.getElement().getAttribute("href");
				DomGlobal.window.open(link, "_self");
			});
		}
	}

	private void registerFocusable(AppW app, AccessibilityGroup group, Widget widget) {
		if (widget != null && app != null) {
			FocusableWidget focusableWidget = new FocusableWidget(group, null, widget);
			focusableWidgets.add(focusableWidget);
			focusableWidget.attachTo(app);
		}
	}

	@Override
	public void examStateChanged(ExamState newState) {
		if (app == null) {
			return;
		}
		if (newState == ExamState.ACTIVE) {
			focusableWidgets.forEach(widget -> widget.detachFrom(app));
		} else if (newState == ExamState.FINISHED) {
			focusableWidgets.forEach(widget -> widget.attachTo(app));
		}
	}
}
