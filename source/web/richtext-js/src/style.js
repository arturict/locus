/*
 * Locus rich text: colours used for editing feedback (docs/design.md tokens).
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 *
 * This object is exposed as `murok.text`; the Java side may replace `selectionColor`.
 */
import { clearCache } from './measure.js';

export const textStyle = {
	/** fill for selected text and selected table cells */
	selectionColor: 'rgba(14, 124, 134, 0.25)',
	caretColor: '#1C2024',
	/** colour given to inserted hyperlinks (stored in the content) */
	hyperlinkColor: '#0E7C86',
	/** outline of the table cell being edited */
	activeCellColor: '#0E7C86',
	/** default table grid colour */
	tableBorderColor: '#5B6470',
	cache: {
		clear() {
			clearCache();
		}
	}
};
