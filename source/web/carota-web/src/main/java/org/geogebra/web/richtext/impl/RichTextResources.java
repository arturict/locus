/*
 * Locus - free software under the EUPL 1.2, based on GeoGebra.
 * Copyright (c) 2026 Locus contributors
 *
 * This file is licensed under the EUPL 1.2.
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package org.geogebra.web.richtext.impl;

import org.gwtproject.resources.client.ClientBundle;
import org.gwtproject.resources.client.Resource;
import org.gwtproject.resources.client.TextResource;

/**
 * Script of the Locus rich text editor (window.murok), built from
 * source/web/richtext-js.
 */
@Resource
public interface RichTextResources extends ClientBundle {

	RichTextResources INSTANCE = new RichTextResourcesImpl();

	@Source("locus-richtext.js")
	TextResource richTextJs();
}
