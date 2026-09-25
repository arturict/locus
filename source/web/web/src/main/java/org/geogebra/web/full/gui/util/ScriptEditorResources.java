/*
 * Locus - free software under the EUPL 1.2, based on GeoGebra.
 * Copyright (c) 2026 Locus contributors
 *
 * This file is licensed under the EUPL 1.2.
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package org.geogebra.web.full.gui.util;

import org.gwtproject.resources.client.ClientBundle;
import org.gwtproject.resources.client.Resource;
import org.gwtproject.resources.client.TextResource;

/**
 * CodeMirror 6 script editor (window.GeoGebraCodeMirror), built from
 * source/web/codemirror-js.
 */
@Resource
public interface ScriptEditorResources extends ClientBundle {

	ScriptEditorResources INSTANCE = new ScriptEditorResourcesImpl();

	@Source("locus-codemirror.js")
	TextResource codemirror();
}
