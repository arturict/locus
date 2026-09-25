/*
 * Locus rich text, exposed as `window.murok` for the Java classes in
 * source/web/carota-web (org.geogebra.web.richtext.impl.Carota and friends).
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 * Based on the design of Carota by Daniel Earwicker (MIT).
 */
import { defaultFormatting, FORMAT_KEYS, isMultipleValues, multipleValues } from './format.js';
import { createEditor } from './editor.js';
import { createTable } from './table.js';
import { textStyle } from './style.js';

const murok = {
	editor: { create: createEditor },
	table: { create: createTable },
	text: textStyle,
	runs: {
		defaultFormatting,
		multipleValues,
		isMultipleValues,
		formattingKeys: FORMAT_KEYS
	}
};

if (typeof window !== 'undefined') {
	window.murok = murok;
}

export default murok;
