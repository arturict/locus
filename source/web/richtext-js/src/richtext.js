/*
 * Locus rich text: an editable document (model, selection, undo, layout, drawing).
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 *
 * The public methods implement the API that the Java classes CarotaDocument and
 * CarotaRange (source/web/carota-web) call. The object has no DOM of its own; the
 * editor and the table attach keyboard and pointer input to it.
 */
import { EMPTY_FORMAT, isMultipleValues, resolve, withFormat } from './format.js';
import { layoutText } from './layout.js';
import { charsFromRuns, codeType, isTerminator, makeCode, NEWLINE, TextModel } from './model.js';
import { drawLayout } from './render.js';
import { textStyle } from './style.js';

const WORD_CHAR = /[\p{L}\p{N}_]/u;
const MAX_UNDO = 100;

export class Range {
	constructor(doc, start, end) {
		this.doc = doc;
		this.start = Math.min(start, end);
		this.end = Math.max(start, end);
	}

	plainText() {
		return this.doc.model.plainText(this.start, this.end);
	}

	save() {
		return this.doc.model.save(this.start, this.end);
	}

	setText(text) {
		this.doc.replace(this.start, this.end, text, 'insert');
	}

	clear() {
		this.setText('');
	}

	/** Resolved formatting; keys with different values are `murok.runs.multipleValues`. */
	getFormatting() {
		const doc = this.doc;
		if (this.start === this.end) {
			const pos = this.start > 0 ? this.start - 1 : 0;
			const result = doc.model.formatting(pos, pos + 1);
			if (this.start === doc.selection.start && this.end === doc.selection.end) {
				Object.assign(result, doc.nextInsertFormatting);
			}
			return result;
		}
		return doc.model.formatting(this.start, this.end);
	}

	getFormattingValue(key, fallback) {
		const value = this.getFormatting()[key];
		return value === undefined || value === null || isMultipleValues(value) ? fallback : value;
	}

	setFormatting(key, value) {
		const doc = this.doc;
		let start = this.start;
		let end = this.end;
		if (key === 'align') {
			const paragraphs = doc.model.paragraphRange(start, end);
			start = paragraphs.start;
			end = paragraphs.end;
		}
		if (start === end) {
			doc.nextInsertFormatting[key] = value;
			doc.fireSelectionChanged();
			return;
		}
		doc.edit(() => doc.model.format(start, end, key, value), 'format');
		doc.fireSelectionChanged();
	}

	getListStyle() {
		return this.doc.model.listStyle(this.start, this.end);
	}
}

function sameChars(a, b) {
	if (a.length !== b.length) {
		return false;
	}
	for (let i = 0; i < a.length; i++) {
		if (a[i] !== b[i]) {
			return false;
		}
	}
	return true;
}

export class RichText {
	constructor() {
		this.model = new TextModel();
		this.selection = { start: 0, end: 0 };
		this.anchor = 0;
		this.nextInsertFormatting = {};
		this.insertFilters = [];
		this.undoStack = [];
		this.redoStack = [];
		this.wrap = true;
		this.defaultAlign = 'left';
		this.scale = 1;
		this.cachedLayout = null;
		this.widthValue = 0;
		this.listeners = { selection: [], content: [], escape: [] };
		/** hooks set by the editor or table that hosts this document */
		this.hooks = {
			isActive: () => false,
			hasFocus: () => false,
			focus: () => {},
			changed: () => {}
		};
		this.lastEditKind = null;
		this.lastEditTime = 0;
	}

	// --- events (Java: HasContent) ---

	selectionChanged(callback) {
		this.listeners.selection.push(callback);
	}

	contentChanged(callback) {
		this.listeners.content.push(callback);
	}

	onEscape(callback) {
		this.listeners.escape.push(callback);
	}

	fireSelectionChanged() {
		this.hooks.changed('selection');
		for (const callback of this.listeners.selection.slice()) {
			callback();
		}
	}

	fireContentChanged() {
		this.hooks.changed('content');
		for (const callback of this.listeners.content.slice()) {
			callback();
		}
	}

	fireEscape() {
		for (const callback of this.listeners.escape.slice()) {
			callback();
		}
	}

	// --- layout ---

	get length() {
		return this.model.chars.length;
	}

	/** Largest caret position: before the final terminator. */
	get maxCaret() {
		return this.model.chars.length - 1;
	}

	layout() {
		if (!this.cachedLayout) {
			this.cachedLayout = layoutText(this.model.chars, {
				width: this.widthValue,
				wrap: this.wrap,
				defaultAlign: this.defaultAlign
			});
		}
		return this.cachedLayout;
	}

	invalidate() {
		this.cachedLayout = null;
	}

	get frame() {
		const layout = this.layout();
		return { height: Math.ceil(layout.height), width: Math.ceil(layout.width),
			length: this.length + 1 };
	}

	setWidth(width) {
		const value = Number(width) > 0 ? Number(width) : 0;
		if (value !== this.widthValue) {
			this.widthValue = value;
			this.invalidate();
		}
	}

	width(value) {
		if (value === undefined) {
			return this.widthValue;
		}
		this.setWidth(value);
		return value;
	}

	// --- content ---

	load(content) {
		this.model.load(Array.isArray(content) ? content : []);
		this.undoStack = [];
		this.redoStack = [];
		this.invalidate();
		this.fireContentChanged();
		this.select(this.selection.start, this.selection.end, false);
	}

	save() {
		return this.model.save();
	}

	/**
	 * Runs a change and records an undo step if the characters changed. Consecutive
	 * typing is merged into one step.
	 */
	edit(change, kind) {
		const before = { chars: this.model.chars.slice(), selection: Object.assign({}, this.selection) };
		change();
		if (sameChars(before.chars, this.model.chars)) {
			return false;
		}
		const now = Date.now();
		if (!(kind === 'type' && this.lastEditKind === 'type' && now - this.lastEditTime < 1500)) {
			this.undoStack.push(before);
			if (this.undoStack.length > MAX_UNDO) {
				this.undoStack.shift();
			}
		}
		this.redoStack = [];
		this.lastEditKind = kind;
		this.lastEditTime = now;
		this.invalidate();
		this.fireContentChanged();
		return true;
	}

	performUndo(redo) {
		const from = redo ? this.redoStack : this.undoStack;
		const to = redo ? this.undoStack : this.redoStack;
		const state = from.pop();
		if (!state) {
			return false;
		}
		to.push({ chars: this.model.chars.slice(), selection: Object.assign({}, this.selection) });
		this.model.chars = state.chars.slice();
		this.model.normalize();
		this.lastEditKind = null;
		this.invalidate();
		this.fireContentChanged();
		this.select(state.selection.start, state.selection.end);
		return true;
	}

	canUndo(redo) {
		return redo ? this.redoStack.length > 0 : this.undoStack.length > 0;
	}

	insertFormat(position) {
		const chars = this.model.chars;
		const sample = chars[Math.max(0, Math.min(position - 1, chars.length - 1))];
		let format = sample ? sample.f : EMPTY_FORMAT;
		for (const key of Object.keys(this.nextInsertFormatting)) {
			format = withFormat(format, key, this.nextInsertFormatting[key]);
		}
		return format;
	}

	/** Characters for inserted text or runs at `position`. */
	charsFor(content, position) {
		if (typeof content === 'string') {
			const format = this.insertFormat(position);
			return [...content.replace(/\r\n?/g, NEWLINE)].map((c) => ({ c, f: format }));
		}
		if (Array.isArray(content)) {
			return charsFromRuns(content);
		}
		if (content && typeof content === 'object') {
			return charsFromRuns([content]);
		}
		return [];
	}

	/** Replaces [start, end) by text or runs and puts the caret after the insertion. */
	replace(start, end, content, kind, takeFocus) {
		const inserted = this.charsFor(content, start);
		const lengthBefore = this.length;
		const changed = this.edit(() => this.model.splice(start, end, inserted), kind || 'insert');
		const caret = start + inserted.length + Math.min(0, this.length - lengthBefore
			- (inserted.length - (end - start)));
		this.select(caret, caret, takeFocus);
		return changed;
	}

	insert(text, takeFocus) {
		this.replace(this.selection.start, this.selection.end, text, 'insert', takeFocus);
	}

	/** Text typed or pasted by the user: runs the insert filters first. */
	typeText(text, kind) {
		let value = text;
		for (const filter of this.insertFilters) {
			value = filter(value);
			if (value === null || value === undefined) {
				return false;
			}
		}
		if (typeof value !== 'string') {
			return false;
		}
		if (value.includes(NEWLINE) && this.inListItem(this.selection.start)) {
			const format = this.insertFormat(this.selection.start);
			const marker = this.unitAt(this.selection.start).marker;
			const chars = [];
			for (const c of value.replace(/\r\n?/g, NEWLINE)) {
				chars.push(c === NEWLINE ? makeCode('listNext', format, marker) : { c, f: format });
			}
			const start = this.selection.start;
			this.edit(() => this.model.splice(start, this.selection.end, chars), 'insert');
			this.select(start + chars.length, start + chars.length);
			return true;
		}
		return this.replace(this.selection.start, this.selection.end, value, kind || 'type');
	}

	// --- selection ---

	range(start, end) {
		return new Range(this, start, end);
	}

	documentRange() {
		return this.range(0, this.length);
	}

	selectedRange() {
		return this.range(this.selection.start, this.selection.end);
	}

	/** Positions directly before a list start show at the same place as after it. */
	validPosition(position, direction) {
		const chars = this.model.chars;
		let p = Math.max(0, Math.min(position, this.maxCaret));
		if (codeType(chars[p]) === 'listStart' && (p === 0 || isTerminator(chars[p - 1]))) {
			p = direction < 0 && p > 0 ? p - 1 : Math.min(p + 1, this.maxCaret);
		}
		return p;
	}

	select(start, end, takeFocus) {
		const max = this.maxCaret;
		let s = Math.max(0, Math.min(Number(start) || 0, max));
		let e = typeof end === 'number' ? Math.max(0, Math.min(end, max)) : s;
		if (s === e) {
			s = e = this.validPosition(s, 1);
		}
		this.anchor = s;
		this.selection = { start: Math.min(s, e), end: Math.max(s, e) };
		this.focusPosition = e;
		this.nextInsertFormatting = {};
		this.fireSelectionChanged();
		if (takeFocus !== false) {
			this.hooks.focus();
		}
	}

	/** Moves the focus end of the selection, keeping the anchor (shift + arrow keys). */
	extendTo(position) {
		const p = Math.max(0, Math.min(position, this.maxCaret));
		this.focusPosition = p;
		this.selection = { start: Math.min(this.anchor, p), end: Math.max(this.anchor, p) };
		this.nextInsertFormatting = {};
		this.fireSelectionChanged();
	}

	byCoordinate(x, y) {
		return { ordinal: this.validPosition(this.layout().ordinalAt(x, y), 1) };
	}

	urlByCoordinate(x, y) {
		const glyph = this.layout().glyphAt(x, y);
		return glyph ? resolve(glyph.f, 'url') || '' : '';
	}

	// --- structure helpers ---

	unitAt(position) {
		return this.model.unitsIn(position, position)[0] || null;
	}

	inListItem(position) {
		const unit = this.unitAt(position);
		return !!unit && unit.type === 'item';
	}

	// --- editing commands (keyboard) ---

	deleteSelection() {
		const { start, end } = this.selection;
		if (start !== end) {
			this.replace(start, end, '', 'delete');
			return true;
		}
		return false;
	}

	deleteBackward(word) {
		if (this.deleteSelection()) {
			return;
		}
		const p = this.selection.start;
		if (p === 0) {
			return;
		}
		const chars = this.model.chars;
		const before = codeType(chars[p - 1]);
		if (before === 'listStart') {
			// remove the list marker of the first item; later items stay a list
			const unit = this.unitAt(p);
			this.edit(() => {
				if (unit && unit.term >= 0 && codeType(chars[unit.term]) === 'listNext') {
					chars.splice(unit.term, 1, makeCode('listStart', chars[unit.term].f, unit.marker));
				}
				this.model.splice(p - 1, p, []);
			}, 'delete');
			this.select(p - 1, p - 1);
			return;
		}
		const from = word ? this.wordStart(p) : p - 1;
		this.edit(() => this.model.splice(from, p, []), 'delete');
		this.select(from, from);
	}

	deleteForward(word) {
		if (this.deleteSelection()) {
			return;
		}
		const p = this.selection.start;
		if (p >= this.maxCaret) {
			return;
		}
		const to = word ? Math.max(p + 1, this.wordEnd(p)) : p + 1;
		this.edit(() => this.model.splice(p, Math.min(to, this.maxCaret), []), 'delete');
		this.select(p, p);
	}

	/** Enter: a new paragraph, or a new list item, or leaves the list on an empty item. */
	newline(soft) {
		this.deleteSelectionSilently();
		const p = this.selection.start;
		const unit = this.unitAt(p);
		const chars = this.model.chars;
		if (!soft && unit && unit.type === 'item' && !unit.continuation) {
			const empty = unit.contentStart === unit.term;
			if (empty) {
				const k = unit.start;
				const code = chars[k];
				const isStart = codeType(code) === 'listStart';
				const format = code.f;
				const replacement = isStart ? [{ c: NEWLINE, f: format }]
					: [makeCode('listEnd', format, unit.marker), { c: NEWLINE, f: format }];
				const nextType = codeType(chars[k + 1]);
				if (nextType === 'listNext') {
					replacement.push(makeCode('listStart', chars[k + 1].f, unit.marker));
				}
				this.edit(() => this.model.splice(k, k + 2, replacement), 'insert');
				const caret = isStart ? k : k + 1;
				this.select(caret, caret);
				return;
			}
			const format = this.insertFormat(p);
			this.edit(() => this.model.splice(p, p, [makeCode('listNext', format, unit.marker)]),
				'insert');
			this.select(p + 1, p + 1);
			return;
		}
		this.replace(p, p, NEWLINE, 'insert');
	}

	deleteSelectionSilently() {
		const { start, end } = this.selection;
		if (start !== end) {
			this.edit(() => this.model.splice(start, end, []), 'delete');
			this.select(start, start, false);
		}
	}

	toggleFormat(key) {
		const range = this.selectedRange();
		range.setFormatting(key, range.getFormatting()[key] !== true);
	}

	wordStart(p) {
		const chars = this.model.chars;
		let i = p;
		while (i > 0 && !this.isWordChar(chars[i - 1])) {
			i--;
		}
		while (i > 0 && this.isWordChar(chars[i - 1])) {
			i--;
		}
		return i;
	}

	wordEnd(p) {
		const chars = this.model.chars;
		let i = p;
		while (i < this.maxCaret && this.isWordChar(chars[i])) {
			i++;
		}
		while (i < this.maxCaret && !this.isWordChar(chars[i]) && !isTerminator(chars[i])) {
			i++;
		}
		return i;
	}

	isWordChar(ch) {
		return !!ch && typeof ch.c === 'string' && WORD_CHAR.test(ch.c);
	}

	/** Range of the word (or space run) at a position, for double click. */
	wordRangeAt(p) {
		const chars = this.model.chars;
		const pos = Math.min(p, this.maxCaret);
		const ch = chars[pos];
		if (!ch || typeof ch.c !== 'string' || ch.c === NEWLINE) {
			return { start: pos, end: pos };
		}
		const same = this.isWordChar(ch) ? (c) => this.isWordChar(c)
			: (c) => !!c && typeof c.c === 'string' && c.c !== NEWLINE && !this.isWordChar(c);
		let s = pos;
		let e = pos;
		while (s > 0 && same(chars[s - 1])) {
			s--;
		}
		while (e < this.maxCaret && same(chars[e])) {
			e++;
		}
		return { start: s, end: e };
	}

	// --- hyperlinks ---

	linkAround(position) {
		const chars = this.model.chars;
		const urlOf = (i) => (i >= 0 && i < chars.length ? resolve(chars[i].f, 'url') : '');
		let at = -1;
		if (urlOf(position - 1)) {
			at = position - 1;
		} else if (position < this.maxCaret && urlOf(position)) {
			at = position;
		}
		if (at < 0) {
			return null;
		}
		const url = urlOf(at);
		let s = at;
		let e = at + 1;
		while (s > 0 && urlOf(s - 1) === url) {
			s--;
		}
		while (e < this.maxCaret && urlOf(e) === url) {
			e++;
		}
		return { start: s, end: e, url };
	}

	hyperlinkRange() {
		const { start, end } = this.selection;
		if (start === end) {
			const link = this.linkAround(start);
			return link ? this.range(link.start, link.end) : this.selectedRange();
		}
		const link = this.linkAround(start + 1);
		if (link && link.start <= start && link.end >= end) {
			return this.range(link.start, link.end);
		}
		return this.selectedRange();
	}

	insertHyperlink(url, text) {
		const { start, end } = this.selection;
		let format = this.insertFormat(start);
		format = withFormat(format, 'color', textStyle.hyperlinkColor);
		format = withFormat(format, 'underline', true);
		format = withFormat(format, 'url', url);
		const shown = text || url || '';
		const inserted = [...shown].map((c) => ({ c, f: format }));
		this.edit(() => this.model.splice(start, end, inserted), 'insert');
		this.select(start + inserted.length, start + inserted.length);
	}

	setHyperlinkUrl(url) {
		const range = this.hyperlinkRange();
		if (range.start === range.end) {
			return;
		}
		this.edit(() => {
			this.model.format(range.start, range.end, 'url', url);
			if (url) {
				this.model.format(range.start, range.end, 'underline', true);
				this.model.format(range.start, range.end, 'color', textStyle.hyperlinkColor);
			}
		}, 'format');
		this.fireSelectionChanged();
	}

	// --- lists ---

	switchListTo(range, listType) {
		const target = range || this.selectedRange();
		let mapper = (p) => p;
		const { start, end } = this.selection;
		this.edit(() => {
			mapper = this.model.switchList(target.start, target.end, listType);
		}, 'format');
		this.select(mapper(start), mapper(end), false);
	}

	getListStyle() {
		return this.selectedRange().getListStyle();
	}

	// --- drawing ---

	draw(ctx) {
		const active = this.hooks.isActive();
		drawLayout(ctx, this.layout(), {
			selection: active ? this.selection : null,
			caret: active && this.hooks.hasFocus(),
			scale: this.scale
		});
	}

	isEmpty() {
		return this.length === 1 && this.model.chars[0].c === NEWLINE;
	}
}

export { EMPTY_FORMAT };
