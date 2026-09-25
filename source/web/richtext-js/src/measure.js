/*
 * Locus rich text: font strings and cached text measurement.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 */
import { resolve } from './format.js';

function canvasBackend() {
	let context = null;
	const ctx = () => {
		if (!context) {
			const canvas = typeof OffscreenCanvas !== 'undefined'
				? new OffscreenCanvas(8, 8) : document.createElement('canvas');
			context = canvas.getContext('2d');
		}
		return context;
	};
	return {
		width(font, text) {
			const c = ctx();
			c.font = font;
			return c.measureText(text).width;
		},
		metrics(font) {
			const c = ctx();
			c.font = font;
			const m = c.measureText('Hg');
			let ascent = m.fontBoundingBoxAscent;
			let descent = m.fontBoundingBoxDescent;
			if (!(ascent >= 0) || !(descent >= 0)) {
				const size = parseFloat(/(\d+(\.\d+)?)px/.exec(font)?.[1] || '16');
				ascent = size * 0.9;
				descent = size * 0.25;
			}
			return { ascent, descent };
		}
	};
}

let backend = null;
const widths = new Map();
const metricsByFont = new Map();

/** Replaces the measuring backend (used by the node tests). */
export function setMeasureBackend(newBackend) {
	backend = newBackend;
	clearCache();
}

export function clearCache() {
	widths.clear();
	metricsByFont.clear();
}

function getBackend() {
	if (!backend) {
		backend = canvasBackend();
	}
	return backend;
}

/** Font size in pixels actually used for drawing (super- and subscript are smaller). */
export function drawnSize(format) {
	const size = Number(resolve(format, 'size')) || 16;
	const script = resolve(format, 'script');
	return script === 'super' || script === 'sub' ? size * 0.8 : size;
}

export function fontString(format) {
	return (resolve(format, 'italic') ? 'italic ' : '')
		+ (resolve(format, 'bold') ? 'bold ' : '')
		+ drawnSize(format) + 'px ' + resolve(format, 'font');
}

export function textWidth(font, text) {
	let byText = widths.get(font);
	if (!byText) {
		byText = new Map();
		widths.set(font, byText);
	}
	let width = byText.get(text);
	if (width === undefined) {
		width = getBackend().width(font, text);
		byText.set(text, width);
	}
	return width;
}

/** Ascent and descent of the line box for a run format. */
export function fontMetrics(format) {
	const font = fontString(format);
	let metrics = metricsByFont.get(font);
	if (!metrics) {
		metrics = getBackend().metrics(font);
		metricsByFont.set(font, metrics);
	}
	const size = Number(resolve(format, 'size')) || 16;
	const script = resolve(format, 'script');
	// shifted scripts still need room in the line box
	if (script === 'super') {
		return { ascent: Math.max(metrics.ascent + size / 3, metrics.ascent), descent: metrics.descent };
	}
	if (script === 'sub') {
		return { ascent: metrics.ascent, descent: metrics.descent + size / 5 };
	}
	return metrics;
}

/** Vertical offset of the baseline for super- and subscript. */
export function scriptShift(format) {
	const size = Number(resolve(format, 'size')) || 16;
	switch (resolve(format, 'script')) {
	case 'super':
		return -size / 3;
	case 'sub':
		return size / 5;
	default:
		return 0;
	}
}
