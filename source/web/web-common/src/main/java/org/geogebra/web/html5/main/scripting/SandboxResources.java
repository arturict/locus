/*
 * Locus - free software under the EUPL 1.2, based on GeoGebra.
 * Copyright (c) 2026 Locus contributors
 *
 * This file is licensed under the EUPL 1.2.
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package org.geogebra.web.html5.main.scripting;

import org.gwtproject.resources.client.ClientBundle;
import org.gwtproject.resources.client.Resource;
import org.gwtproject.resources.client.TextResource;

/**
 * QuickJS compiled to WebAssembly (window.QJS), built from source/web/quickjs-js.
 */
@Resource
public interface SandboxResources extends ClientBundle {

	SandboxResources INSTANCE = new SandboxResourcesImpl();

	@Source("locus-quickjs.js")
	TextResource quickJs();
}
