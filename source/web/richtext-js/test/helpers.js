// Test helpers: a deterministic measuring backend (every character is 10 px wide,
// lines are 16 px high) so that layout tests do not need a browser.
import { setMeasureBackend } from '../src/measure.js';

export function useFakeMeasure() {
	setMeasureBackend({
		width: (font, text) => [...text].length * 10,
		metrics: () => ({ ascent: 12, descent: 4 })
	});
}

export function json(value) {
	return JSON.stringify(value);
}
