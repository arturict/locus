/*
 * Locus rich text: line layout.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 *
 * Words are a run of non-space characters followed by their trailing spaces, as in
 * Carota (MIT, Daniel Earwicker). A line breaks before a word that does not fit; a word
 * wider than the whole line is broken between characters.
 */
import { resolve } from './format.js';
import { codeType, NEWLINE } from './model.js';
import { fontMetrics, fontString, textWidth } from './measure.js';

const SPACE = /[ \t ]/;

/** Indentation of list items relative to the font size of the list marker. */
export function listIndent(format) {
	return Math.round((Number(resolve(format, 'size')) || 16) * 1.75);
}

export function markerText(marker, number) {
	return marker === 'bullet' ? '•' : number + '.';
}

function isSpace(ch) {
	return typeof ch.c === 'string' && SPACE.test(ch.c);
}

/**
 * Measures the characters [from, to) of a paragraph: returns one width per character.
 * Characters with the same formatting inside a word are measured together so that
 * kerning is respected and caret positions match the drawn text.
 */
function measureChars(chars, from, to) {
	const widths = new Array(to - from).fill(0);
	let i = from;
	while (i < to) {
		const ch = chars[i];
		if (typeof ch.c !== 'string') {
			i++;
			continue;
		}
		const font = fontString(ch.f);
		if (isSpace(ch)) {
			widths[i - from] = textWidth(font, ch.c === '\t' ? '    ' : ' ');
			i++;
			continue;
		}
		let j = i;
		let chunk = '';
		let previous = 0;
		while (j < to && typeof chars[j].c === 'string' && chars[j].f === ch.f && !isSpace(chars[j])) {
			chunk += chars[j].c;
			const width = textWidth(font, chunk);
			widths[j - from] = width - previous;
			previous = width;
			j++;
		}
		i = j;
	}
	return widths;
}

class Line {
	constructor(indent) {
		this.glyphs = [];
		this.indent = indent;
		this.ascent = 0;
		this.descent = 0;
		this.top = 0;
		this.height = 0;
		this.baseline = 0;
		this.marker = null;
		this.endsParagraph = false;
		this.contentWidth = 0;
	}

	get start() {
		return this.glyphs[0].ord;
	}

	get end() {
		return this.glyphs[this.glyphs.length - 1].ord + 1;
	}

	add(glyph) {
		this.glyphs.push(glyph);
		const metrics = fontMetrics(glyph.f);
		this.ascent = Math.max(this.ascent, metrics.ascent);
		this.descent = Math.max(this.descent, metrics.descent);
	}
}

/**
 * Lays out characters for a given width.
 * @param {Array} chars document characters
 * @param {{width: number, wrap?: boolean, defaultAlign?: string}} options
 */
export function layoutText(chars, options) {
	const width = options.wrap === false || !(options.width > 0) ? Infinity : options.width;
	const defaultAlign = options.defaultAlign || 'left';
	const lines = [];
	const lists = [];
	let pendingMarker = null;
	let i = 0;
	const n = chars.length;

	while (i < n) {
		// codes at the start of a paragraph
		let startGlyph = null;
		const type = codeType(chars[i]);
		if (type === 'listStart') {
			lists.push({ marker: chars[i].m || 'number', count: 0, format: chars[i].f });
			lists[lists.length - 1].count++;
			pendingMarker = lists[lists.length - 1];
			startGlyph = { ord: i, x: 0, w: 0, ch: null, f: chars[i].f };
			i++;
		}
		const indent = lists.reduce((sum, list) => sum + listIndent(list.format), 0);
		const available = width === Infinity ? Infinity : Math.max(1, width - indent);

		// paragraph content up to its terminator
		let j = i;
		while (j < n && !(chars[j].c === NEWLINE || codeType(chars[j]) === 'listNext'
			|| codeType(chars[j]) === 'listEnd' || codeType(chars[j]) === 'listStart')) {
			j++;
		}
		const terminator = j < n && codeType(chars[j]) !== 'listStart' ? j : -1;
		const widths = measureChars(chars, i, j);

		const paragraphLines = [];
		let line = new Line(indent);
		let x = 0;
		if (startGlyph) {
			line.add(startGlyph);
		}
		const newLine = () => {
			paragraphLines.push(line);
			line = new Line(indent);
			x = 0;
		};
		let k = i;
		while (k < j) {
			// one word: non-space characters, then spaces
			let wordEnd = k;
			while (wordEnd < j && !isSpace(chars[wordEnd])) {
				wordEnd++;
			}
			let spaceEnd = wordEnd;
			while (spaceEnd < j && isSpace(chars[spaceEnd])) {
				spaceEnd++;
			}
			let wordWidth = 0;
			for (let m = k; m < wordEnd; m++) {
				wordWidth += widths[m - i];
			}
			const hasContent = line.glyphs.some((g) => g.ch !== null);
			if (hasContent && x + wordWidth > available) {
				newLine();
			}
			for (let m = k; m < spaceEnd; m++) {
				const w = widths[m - i];
				const isCharOfWord = m < wordEnd;
				if (isCharOfWord && x + w > available && line.glyphs.some((g) => g.ch !== null)
						&& wordWidth > available) {
					newLine();
				}
				line.add({ ord: m, x, w, ch: typeof chars[m].c === 'string' ? chars[m].c : null,
					f: chars[m].f });
				x += w;
			}
			k = spaceEnd;
		}
		if (terminator >= 0) {
			line.add({ ord: terminator, x, w: 0, ch: null, f: chars[terminator].f, terminator: true });
		}
		if (line.glyphs.length) {
			paragraphLines.push(line);
		}
		if (paragraphLines.length) {
			paragraphLines[paragraphLines.length - 1].endsParagraph = true;
			if (pendingMarker) {
				paragraphLines[0].marker = {
					text: markerText(pendingMarker.marker, pendingMarker.count),
					f: pendingMarker.format,
					indent
				};
				pendingMarker = null;
			}
		}
		lines.push(...paragraphLines);

		// what follows the terminator
		if (terminator >= 0) {
			const endType = codeType(chars[terminator]);
			if (endType === 'listNext' && lists.length) {
				lists[lists.length - 1].count++;
				pendingMarker = lists[lists.length - 1];
			} else if (endType === 'listEnd') {
				lists.pop();
			}
			i = terminator + 1;
		} else {
			i = j;
		}
	}
	return new Layout(lines, width, defaultAlign);
}

function lineAlign(line, defaultAlign) {
	const glyph = line.glyphs.find((g) => g.ch !== null)
		|| line.glyphs.find((g) => g.terminator) || line.glyphs[0];
	const align = glyph && glyph.f.align;
	return align || defaultAlign;
}

export class Layout {
	constructor(lines, width, defaultAlign) {
		this.lines = lines;
		let y = 0;
		let maxWidth = 0;
		for (const line of lines) {
			let contentWidth = 0;
			for (const g of line.glyphs) {
				if (g.ch !== null && !SPACE.test(g.ch)) {
					contentWidth = g.x + g.w;
				}
			}
			line.contentWidth = contentWidth;
			const available = width === Infinity ? contentWidth : width - line.indent;
			const align = lineAlign(line, defaultAlign);
			let offset = 0;
			if (align === 'right') {
				offset = Math.max(0, available - contentWidth);
			} else if (align === 'center') {
				offset = Math.max(0, (available - contentWidth) / 2);
			} else if (align === 'justify' && !line.endsParagraph && width !== Infinity) {
				const spaces = line.glyphs.filter((g, idx) => g.ch !== null && SPACE.test(g.ch)
					&& idx < line.glyphs.length - 1 && g.x + g.w < contentWidth);
				if (spaces.length) {
					const extra = (available - contentWidth) / spaces.length;
					let shift = 0;
					for (const g of line.glyphs) {
						g.x += shift;
						if (spaces.includes(g)) {
							g.w += extra;
							shift += extra;
						}
					}
				}
			}
			for (const g of line.glyphs) {
				g.x += line.indent + offset;
			}
			if (line.ascent === 0 && line.descent === 0) {
				line.ascent = 12;
				line.descent = 4;
			}
			line.top = y;
			line.height = line.ascent + line.descent;
			line.baseline = y + line.ascent;
			y += line.height;
			maxWidth = Math.max(maxWidth, line.indent + offset + contentWidth);
		}
		this.height = y;
		this.width = maxWidth;
	}

	lineIndexOf(ordinal) {
		const lines = this.lines;
		let lo = 0;
		let hi = lines.length - 1;
		while (lo < hi) {
			const mid = (lo + hi + 1) >> 1;
			if (lines[mid].start <= ordinal) {
				lo = mid;
			} else {
				hi = mid - 1;
			}
		}
		return lo;
	}

	glyphOf(ordinal) {
		const line = this.lines[this.lineIndexOf(ordinal)];
		if (!line) {
			return null;
		}
		return line.glyphs.find((g) => g.ord === ordinal) || null;
	}

	/** Caret rectangle before the character at `ordinal`. */
	caret(ordinal) {
		const index = this.lineIndexOf(ordinal);
		const line = this.lines[index];
		if (!line) {
			return { x: 0, y: 0, h: 16, line: 0 };
		}
		const glyph = line.glyphs.find((g) => g.ord === ordinal);
		let x;
		if (glyph) {
			x = glyph.x;
		} else {
			const last = line.glyphs[line.glyphs.length - 1];
			x = last.x + last.w;
		}
		return { x, y: line.top, h: line.height, line: index };
	}

	lineAt(y) {
		for (let i = 0; i < this.lines.length; i++) {
			if (y < this.lines[i].top + this.lines[i].height) {
				return i;
			}
		}
		return this.lines.length - 1;
	}

	/** Caret position nearest to a point in line `index`. */
	ordinalInLine(index, x) {
		const line = this.lines[index];
		const glyphs = line.glyphs;
		for (const g of glyphs) {
			if (g.terminator) {
				return g.ord;
			}
			if (x < g.x + g.w / 2) {
				return g.ord;
			}
		}
		const last = glyphs[glyphs.length - 1];
		const next = this.lines[index + 1];
		// a wrapped line: stay before its trailing space rather than jump to the next line
		if (next && !line.endsParagraph) {
			return last.ch !== null && SPACE.test(last.ch) ? last.ord : last.ord + 1;
		}
		return last.ord + 1;
	}

	ordinalAt(x, y) {
		if (!this.lines.length) {
			return 0;
		}
		return this.ordinalInLine(this.lineAt(y), x);
	}

	/** The character drawn at a point (not the nearest caret position), or null. */
	glyphAt(x, y) {
		if (!this.lines.length || y < 0 || y > this.height) {
			return null;
		}
		const line = this.lines[this.lineAt(y)];
		return line.glyphs.find((g) => g.ch !== null && x >= g.x && x < g.x + g.w) || null;
	}

	/** Rectangles covering the characters [start, end). */
	rects(start, end) {
		const rects = [];
		if (start >= end) {
			return rects;
		}
		for (const line of this.lines) {
			if (line.end <= start || line.start >= end) {
				continue;
			}
			let x0 = null;
			let x1 = null;
			for (const g of line.glyphs) {
				if (g.ord >= start && g.ord < end) {
					const w = g.terminator ? Math.max(4, (line.ascent + line.descent) / 4) : g.w;
					x0 = x0 === null ? g.x : Math.min(x0, g.x);
					x1 = x1 === null ? g.x + w : Math.max(x1, g.x + w);
				}
			}
			if (x0 !== null) {
				rects.push({ x: x0, y: line.top, w: Math.max(1, x1 - x0), h: line.height });
			}
		}
		return rects;
	}
}
