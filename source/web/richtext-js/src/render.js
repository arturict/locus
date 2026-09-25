/*
 * Locus rich text: drawing a layout on a canvas.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 */
import { resolve } from './format.js';
import { drawnSize, fontString, scriptShift } from './measure.js';
import { textStyle } from './style.js';

function drawDecorations(ctx, format, x, baseline, width) {
	const size = drawnSize(format);
	const thickness = Math.max(1, size / 14);
	if (resolve(format, 'underline')) {
		ctx.fillRect(x, baseline + Math.max(1, size / 10), width, thickness);
	}
	if (resolve(format, 'strikeout')) {
		ctx.fillRect(x, baseline - size * 0.3, width, thickness);
	}
}

function drawSegment(ctx, glyphs, baseline) {
	const first = glyphs[0];
	const format = first.f;
	const last = glyphs[glyphs.length - 1];
	const width = last.x + last.w - first.x;
	const text = glyphs.map((g) => (g.ch === '\t' ? ' ' : g.ch)).join('');
	const shiftedBaseline = baseline + scriptShift(format);
	ctx.font = fontString(format);
	ctx.fillStyle = resolve(format, 'color');
	if (text.trim().length) {
		ctx.fillText(text, first.x, shiftedBaseline);
	}
	drawDecorations(ctx, format, first.x, shiftedBaseline, width);
}

/**
 * Draws a layout with its origin at (0, 0) of the current transform.
 * @param {CanvasRenderingContext2D} ctx
 * @param {import('./layout.js').Layout} layout
 * @param {{selection?: {start: number, end: number}, caret?: boolean, scale?: number}} state
 */
export function drawLayout(ctx, layout, state = {}) {
	ctx.save();
	ctx.textAlign = 'left';
	ctx.textBaseline = 'alphabetic';
	const scale = state.scale > 0 ? state.scale : 1;

	// highlighted text (bgcolor)
	for (const line of layout.lines) {
		for (const g of line.glyphs) {
			const bg = resolve(g.f, 'bgcolor');
			if (g.ch !== null && bg && bg !== 'transparent') {
				ctx.fillStyle = bg;
				ctx.fillRect(g.x, line.top, g.w + 0.5, line.height);
			}
		}
	}

	const selection = state.selection;
	if (selection && selection.start !== selection.end) {
		ctx.fillStyle = textStyle.selectionColor;
		for (const r of layout.rects(selection.start, selection.end)) {
			ctx.fillRect(r.x, r.y, r.w, r.h);
		}
	}

	for (const line of layout.lines) {
		if (line.marker) {
			const format = line.marker.f;
			ctx.font = fontString(format);
			ctx.fillStyle = resolve(format, 'color');
			ctx.textAlign = 'right';
			const gap = Math.max(4, drawnSize(format) * 0.4);
			ctx.fillText(line.marker.text, line.marker.indent - gap, line.baseline);
			ctx.textAlign = 'left';
		}
		let segment = [];
		for (const g of line.glyphs) {
			if (g.ch === null) {
				continue;
			}
			if (segment.length && segment[0].f !== g.f) {
				drawSegment(ctx, segment, line.baseline);
				segment = [];
			}
			segment.push(g);
		}
		if (segment.length) {
			drawSegment(ctx, segment, line.baseline);
		}
	}

	if (state.caret && selection && selection.start === selection.end) {
		const caret = layout.caret(selection.start);
		ctx.fillStyle = textStyle.caretColor;
		ctx.fillRect(caret.x, caret.y, Math.max(1, 1.5 / scale), caret.h);
	}
	ctx.restore();
}
