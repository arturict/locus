/*
 * Locus rich text: the document model.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 *
 * A document is an array of characters. Each character is a code point string or an
 * inline code object ({$: 'listStart' | 'listNext' | 'listEnd'}) together with a shared
 * formatting object. The saved form is Carota's list of runs
 * (https://github.com/danielearwicker/carota, MIT), which GeoGebra files store.
 *
 * Invariants kept by normalize():
 * - every listNext/listEnd belongs to an open list, every list is closed;
 * - the last character is a terminator, '\n' or listEnd; it marks the end of the
 *   document and a caret cannot be placed after it;
 * - a final '\n' has the formatting of the character before it.
 */
import { cleanFormat, EMPTY_FORMAT, merge, withFormat } from './format.js';

export const NEWLINE = '\n';

export function codeType(ch) {
	return ch && typeof ch.c === 'object' && ch.c !== null ? ch.c.$ : null;
}

export function isListCode(ch) {
	const type = codeType(ch);
	return type === 'listStart' || type === 'listNext' || type === 'listEnd';
}

/** Characters that end a line: newline, listNext (ends the previous item) and listEnd. */
export function isTerminator(ch) {
	const type = codeType(ch);
	return ch.c === NEWLINE || type === 'listNext' || type === 'listEnd';
}

function markerOf(code) {
	const marker = code && code.marker;
	if (marker === 'bullet' || (marker && typeof marker === 'object' && marker.$ === 'bullet')) {
		return 'bullet';
	}
	return 'number';
}

export function makeCode(type, format, marker) {
	const code = { $: type };
	if (type === 'listStart' && marker === 'bullet') {
		code.marker = 'bullet';
	}
	return { c: code, f: format, m: marker || 'number' };
}

function pushText(text, format, out) {
	if (typeof text === 'string') {
		for (const cp of text.replace(/\r\n?/g, NEWLINE)) {
			out.push({ c: cp, f: format });
		}
	} else if (Array.isArray(text)) {
		for (const piece of text) {
			pushText(piece, format, out);
		}
	} else if (text && typeof text === 'object' && typeof text.$ === 'string') {
		const code = Object.assign({}, text);
		out.push({ c: code, f: format, m: markerOf(code) });
	}
}

/** Converts saved runs into characters (without normalizing). */
export function charsFromRuns(runs) {
	const out = [];
	if (!Array.isArray(runs)) {
		return out;
	}
	for (const run of runs) {
		if (run && typeof run === 'object') {
			pushText(run.text, cleanFormat(run), out);
		}
	}
	return out;
}

/** Converts characters back into consolidated runs. */
export function runsFromChars(chars, start = 0, end = chars.length) {
	const runs = [];
	let current = null;
	for (let i = Math.max(0, start); i < Math.min(end, chars.length); i++) {
		const ch = chars[i];
		if (typeof ch.c === 'string') {
			if (current && current.f === ch.f) {
				current.text += ch.c;
			} else {
				current = { text: ch.c, f: ch.f };
				runs.push(current);
			}
		} else {
			current = null;
			runs.push({ text: saveCode(ch), f: ch.f });
		}
	}
	return runs.map((run) => Object.assign({ text: run.text }, run.f));
}

function saveCode(ch) {
	const type = codeType(ch);
	if (type === 'listStart') {
		const code = Object.assign({}, ch.c);
		delete code.marker;
		if (ch.m === 'bullet') {
			code.marker = 'bullet';
		}
		return code;
	}
	return Object.assign({}, ch.c);
}

/**
 * Repairs list structure (like Carota's list edit filter): a listNext outside a list
 * starts a new list, a listEnd outside a list is removed, open lists are closed.
 */
export function fixLists(chars) {
	for (;;) {
		const stack = [];
		let changed = false;
		for (let i = 0; i < chars.length; i++) {
			const type = codeType(chars[i]);
			if (type === 'listStart') {
				stack.push(chars[i].m);
			} else if (type === 'listNext' && !stack.length) {
				chars[i] = makeCode('listStart', chars[i].f, chars[i].m);
				changed = true;
				break;
			} else if (type === 'listEnd') {
				if (!stack.length) {
					chars.splice(i, 1);
					changed = true;
					break;
				}
				stack.pop();
			}
		}
		if (!changed) {
			if (stack.length) {
				let at = chars.length;
				if (at > 0 && chars[at - 1].c === NEWLINE) {
					at--;
				}
				const format = at > 0 ? chars[at - 1].f : EMPTY_FORMAT;
				while (stack.length) {
					chars.splice(at, 0, makeCode('listEnd', format, stack.pop()));
				}
			}
			return;
		}
	}
}

function assignMarkers(chars) {
	const stack = [];
	for (let i = 0; i < chars.length; i++) {
		const type = codeType(chars[i]);
		if (type === 'listStart') {
			stack.push(chars[i].m || 'number');
		} else if (type === 'listNext' || type === 'listEnd') {
			const marker = stack.length ? stack[stack.length - 1] : 'number';
			if (chars[i].m !== marker) {
				chars[i] = { c: chars[i].c, f: chars[i].f, m: marker };
			}
			if (type === 'listEnd') {
				stack.pop();
			}
		}
	}
}

export class TextModel {
	constructor() {
		this.chars = [];
		this.normalize();
	}

	load(runs) {
		this.chars = charsFromRuns(runs);
		this.normalize();
	}

	save(start, end) {
		return runsFromChars(this.chars, start, end);
	}

	get length() {
		return this.chars.length;
	}

	normalize() {
		const chars = this.chars;
		fixLists(chars);
		// a paragraph directly before a list ends with a newline
		for (let i = 1; i < chars.length; i++) {
			if (codeType(chars[i]) === 'listStart' && !isTerminator(chars[i - 1])
					&& codeType(chars[i - 1]) !== 'listStart') {
				chars.splice(i, 0, { c: NEWLINE, f: chars[i - 1].f });
				i++;
			}
		}
		const last = chars[chars.length - 1];
		if (!last || !(last.c === NEWLINE || codeType(last) === 'listEnd')) {
			chars.push({ c: NEWLINE, f: last ? last.f : EMPTY_FORMAT });
		} else if (last.c === NEWLINE && chars.length > 1 && last.f !== chars[chars.length - 2].f) {
			chars[chars.length - 1] = { c: NEWLINE, f: chars[chars.length - 2].f };
		}
		assignMarkers(chars);
	}

	/** Replaces characters [start, end) and normalizes. */
	splice(start, end, inserted) {
		this.chars.splice(start, Math.max(0, end - start), ...inserted);
		this.normalize();
	}

	/** Sets one formatting key on characters [start, end). */
	format(start, end, key, value) {
		const replaced = new Map();
		for (let i = start; i < end && i < this.chars.length; i++) {
			const ch = this.chars[i];
			let format = replaced.get(ch.f);
			if (!format) {
				format = withFormat(ch.f, key, value);
				replaced.set(ch.f, format);
			}
			if (format !== ch.f) {
				this.chars[i] = Object.assign({}, ch, { f: format });
			}
		}
		this.normalize();
	}

	/** Resolved formatting of [start, end), keys with different values are multipleValues. */
	formatting(start, end) {
		const formats = [];
		for (let i = start; i < end && i < this.chars.length; i++) {
			formats.push(this.chars[i].f);
		}
		return merge(formats);
	}

	plainText(start, end) {
		let text = '';
		for (let i = Math.max(0, start); i < end && i < this.chars.length; i++) {
			const ch = this.chars[i];
			if (typeof ch.c === 'string') {
				text += ch.c;
			} else if (codeType(ch) === 'listNext' || codeType(ch) === 'listEnd') {
				text += NEWLINE;
			}
		}
		return text;
	}

	/**
	 * Splits the document into paragraphs and list items. Every unit owns the characters
	 * [start, end): an item owns its listStart/listNext code, its content and a closing
	 * listEnd; a paragraph owns its content and its newline (if any).
	 * `term` is the index of the character that ends the unit visually (-1 if none) and
	 * `first`..`last` are the caret positions that lie in the unit.
	 */
	units() {
		const chars = this.chars;
		const units = [];
		const stack = [];
		let nextListId = 1;
		let unit = null;
		const close = (end, term) => {
			if (unit) {
				unit.end = end;
				unit.term = term;
				units.push(unit);
				unit = null;
			}
		};
		for (let i = 0; i < chars.length; i++) {
			const ch = chars[i];
			const type = codeType(ch);
			if (type === 'listStart' || type === 'listNext') {
				close(i, type === 'listNext' ? i : -1);
				if (type === 'listStart') {
					stack.push({ id: nextListId++, marker: ch.m || 'number' });
				}
				const list = stack[stack.length - 1] || { id: 0, marker: 'number' };
				unit = { type: 'item', start: i, contentStart: i + 1, marker: list.marker,
					listId: list.id, depth: stack.length };
			} else if (type === 'listEnd') {
				if (unit) {
					close(i + 1, i);
				}
				stack.pop();
			} else if (ch.c === NEWLINE && !(unit && unit.type === 'item')) {
				if (!unit) {
					unit = { type: 'para', start: i, contentStart: i, depth: stack.length };
				}
				close(i + 1, i);
			} else if (!unit) {
				unit = { type: stack.length ? 'item' : 'para', start: i, contentStart: i,
					depth: stack.length, continuation: stack.length > 0 };
				if (stack.length) {
					const list = stack[stack.length - 1];
					unit.marker = list.marker;
					unit.listId = list.id;
				}
			}
		}
		close(chars.length, -1);
		for (let k = 0; k < units.length; k++) {
			const u = units[k];
			u.first = u.type === 'item' && !u.continuation ? u.contentStart : u.start;
			if (u.term >= 0) {
				u.last = u.term;
			} else {
				u.last = u.end;
			}
			if (u.first > u.last) {
				u.first = u.last;
			}
		}
		return units;
	}

	/** Units whose caret positions intersect the range [start, end]. */
	unitsIn(start, end, units = this.units()) {
		const collapsed = start === end;
		return units.filter((u) => u.first <= end && u.last >= start
			&& (collapsed || u.first !== end || u.first === start));
	}

	/** Character range of the paragraphs and items touched by [start, end). */
	paragraphRange(start, end) {
		const units = this.unitsIn(start, end);
		if (!units.length) {
			return { start, end };
		}
		const last = units[units.length - 1];
		return {
			start: units[0].start,
			end: Math.min(this.chars.length, Math.max(last.end, last.term + 1))
		};
	}

	/** 'bullet' or 'number' if every unit in the range is an item of that kind, else null. */
	listStyle(start, end) {
		const units = this.unitsIn(start, end);
		if (!units.length || units.some((u) => u.type !== 'item')) {
			return null;
		}
		const marker = units[0].marker;
		return units.every((u) => u.marker === marker) ? marker : null;
	}

	/**
	 * Turns the paragraphs in the range into a list of the given type, or back into
	 * plain paragraphs if they already are one. Returns a function that maps old caret
	 * positions to new ones.
	 */
	switchList(start, end, listType) {
		const marker = listType === 'bullet' ? 'bullet' : 'number';
		const units = this.units();
		const selected = new Set(this.unitsIn(start, end, units));
		if (!selected.size) {
			return (p) => p;
		}
		const removing = [...selected].every((u) => u.type === 'item' && u.marker === marker);
		const chars = this.chars;
		const logical = units.map((u) => {
			const hasCode = u.type === 'item' && !u.continuation;
			const contentEnd = u.term >= 0 && u.term < u.end ? u.term : u.end;
			let content = chars.slice(u.contentStart, contentEnd);
			if (u.type === 'item' && codeType(chars[u.end - 1]) === 'listEnd') {
				content = chars.slice(u.contentStart, u.end - 1);
			}
			const endChar = u.term >= 0 ? chars[u.term] : null;
			return {
				unit: u,
				type: u.type,
				listId: u.listId,
				marker: u.marker,
				codeFormat: hasCode ? chars[u.start].f : (content[0] || endChar || { f: EMPTY_FORMAT }).f,
				content,
				termFormat: endChar ? endChar.f
					: (content.length ? content[content.length - 1].f : EMPTY_FORMAT),
				implicitEnd: u.type === 'para' && u.term < 0
			};
		});
		let newListId = -1;
		for (let k = 0; k < logical.length; k++) {
			const item = logical[k];
			if (!selected.has(item.unit)) {
				continue;
			}
			if (removing) {
				item.type = 'para';
				item.implicitEnd = false;
			} else {
				item.type = 'item';
				item.marker = marker;
				const previous = logical[k - 1];
				item.listId = previous && previous.type === 'item' && previous.marker === marker
					? previous.listId : newListId--;
			}
		}
		const out = [];
		const newStarts = [];
		let open = null;
		for (let k = 0; k < logical.length; k++) {
			const item = logical[k];
			if (item.type === 'item') {
				if (open && open.listId === item.listId) {
					out.push(makeCode('listNext', item.codeFormat, item.marker));
				} else {
					if (open) {
						out.push(makeCode('listEnd', open.termFormat, open.marker));
					}
					out.push(makeCode('listStart', item.codeFormat, item.marker));
				}
				newStarts.push(out.length);
				out.push(...item.content);
				open = item;
			} else {
				if (open) {
					out.push(makeCode('listEnd', open.termFormat, open.marker));
					open = null;
				}
				newStarts.push(out.length);
				out.push(...item.content);
				const next = logical[k + 1];
				if (!(item.implicitEnd && next && next.type === 'item')) {
					out.push({ c: NEWLINE, f: item.termFormat });
				}
			}
		}
		if (open) {
			out.push(makeCode('listEnd', open.termFormat, open.marker));
		}
		this.chars = out;
		this.normalize();
		return (p) => {
			for (let k = 0; k < logical.length; k++) {
				const u = logical[k].unit;
				if (p <= u.last || k === logical.length - 1) {
					const offset = Math.max(0, Math.min(p - u.contentStart, logical[k].content.length));
					return Math.min(newStarts[k] + offset, this.chars.length - 1);
				}
			}
			return p;
		};
	}
}
