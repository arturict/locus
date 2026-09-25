/*
 * Locus rich text: tables of rich text cells (`murok.table.create`).
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 *
 * Saved form (stored by GeoInlineTable):
 * {rows: [heights], columns: [widths], content: [[{content: runs | null, bgcolor?,
 *  wrapping?, valign?, halign?, rotation?}]], vborders: null | rows x (cols + 1),
 *  hborders: null | (rows + 1) x cols, bgcolor, wrapping, valign, halign, rotation}
 * Border values are line thicknesses, 0 for no line; null means thickness 1 everywhere.
 * Table-level properties apply to cells that do not set their own.
 */
import { isMultipleValues } from './format.js';
import { createTextArea, TextInput, wordRange } from './input.js';
import { localPoint, paintInto } from './editor.js';
import { Range, RichText } from './richtext.js';
import { textStyle } from './style.js';

export const DEFAULT_ROW_HEIGHT = 36;
export const DEFAULT_COLUMN_WIDTH = 100;
export const MIN_CELL_SIZE = 16;
export const CELL_PADDING = 8;
const CELL_PROPERTIES = ['bgcolor', 'wrapping', 'valign', 'halign', 'rotation'];
const PROPERTY_DEFAULTS = { bgcolor: 'transparent', wrapping: 'wrap', valign: 'top',
	halign: 'left', rotation: 'none' };
const BORDER_TOLERANCE = 4;

function sum(values, from = 0, to = values.length) {
	let total = 0;
	for (let i = from; i < to; i++) {
		total += values[i];
	}
	return total;
}

function round(value) {
	return Math.round(value * 100) / 100;
}

function copyBorders(borders) {
	return borders ? borders.map((line) => line.slice()) : null;
}

class EmptyRange extends Range {
	constructor() {
		super({ model: { plainText: () => '', listStyle: () => null } }, 0, 0);
	}

	plainText() {
		return '';
	}

	getFormattingValue(key, fallback) {
		return fallback;
	}

	setFormatting() {}
}

export class Table {
	constructor() {
		this.rowSizes = [];
		this.colSizes = [];
		this.cells = [];
		this.vborders = null;
		this.hborders = null;
		this.props = {};
		this.sel = null;
		this.scale = 1;
		this.externalPaintValue = false;
		this.insertFilters = [];
		this.listeners = { content: [], size: [], selection: [], escape: [] };
		this.batch = 0;
		this.batchChanged = false;
		this.input = null;
		this.host = { focus: () => {}, repaint: () => {}, hasFocus: () => false };
		this.init(2, 2);
	}

	// --- events (Java: HasContent, sizeChanged) ---

	contentChanged(callback) {
		this.listeners.content.push(callback);
	}

	sizeChanged(callback) {
		this.listeners.size.push(callback);
	}

	selectionChanged(callback) {
		this.listeners.selection.push(callback);
	}

	onEscape(callback) {
		this.listeners.escape.push(callback);
	}

	fire(kind) {
		if (kind === 'content' && this.batch > 0) {
			this.batchChanged = true;
			return;
		}
		this.host.repaint();
		for (const callback of this.listeners[kind].slice()) {
			callback();
		}
	}

	/** Runs several changes and reports one content change. */
	inBatch(change) {
		this.batch++;
		try {
			change();
		} finally {
			this.batch--;
		}
		if (this.batch === 0 && this.batchChanged) {
			this.batchChanged = false;
			this.fire('content');
		}
	}

	// --- structure ---

	get rows() {
		return this.rowSizes.length;
	}

	get cols() {
		return this.colSizes.length;
	}

	get totalWidth() {
		return sum(this.colSizes);
	}

	get totalHeight() {
		return sum(this.rowSizes);
	}

	get selection() {
		return this.sel;
	}

	getMinWidth() {
		return MIN_CELL_SIZE * this.cols;
	}

	getMinHeight() {
		return MIN_CELL_SIZE * this.rows;
	}

	newCell(content, props) {
		const doc = new RichText();
		doc.model.load(Array.isArray(content) ? content : []);
		const cell = { doc, props: Object.assign({}, props) };
		this.wireCell(cell);
		return cell;
	}

	wireCell(cell) {
		const table = this;
		cell.doc.insertFilters = this.insertFilters;
		cell.doc.hooks = {
			isActive: () => table.isEditing(cell),
			hasFocus: () => table.isEditing(cell) && table.host.hasFocus(),
			focus: () => {
				if (table.isEditing(cell)) {
					table.host.focus();
				}
			},
			changed: (what) => table.cellChanged(cell, what)
		};
		cell.doc.listeners.escape.push(() => this.fire('escape'));
	}

	cellChanged(cell, what) {
		if (what === 'content') {
			this.growRowFor(cell);
			this.fire('content');
		} else if (this.isEditing(cell)) {
			if (this.input) {
				this.input.sync();
			}
			this.fire('selection');
		}
	}

	init(rows, cols) {
		this.rowSizes = new Array(Math.max(0, rows)).fill(DEFAULT_ROW_HEIGHT);
		this.colSizes = new Array(Math.max(0, cols)).fill(DEFAULT_COLUMN_WIDTH);
		this.cells = [];
		for (let r = 0; r < rows; r++) {
			const row = [];
			for (let c = 0; c < cols; c++) {
				row.push(this.newCell(null, {}));
			}
			this.cells.push(row);
		}
		this.vborders = null;
		this.hborders = null;
		this.props = {};
		this.sel = null;
		this.updateCellLayouts();
	}

	load(data) {
		if (!data || typeof data !== 'object') {
			return;
		}
		const content = Array.isArray(data.content) ? data.content : [];
		const rows = Array.isArray(data.rows) ? data.rows.length : content.length;
		let cols = Array.isArray(data.columns) ? data.columns.length : 0;
		if (!cols) {
			cols = content.reduce((max, row) => Math.max(max, Array.isArray(row) ? row.length : 0), 0);
		}
		const size = (list, i, fallback) => {
			const value = Array.isArray(list) ? Number(list[i]) : NaN;
			return value > 0 ? value : fallback;
		};
		const editing = this.sel && this.sel.editing ? { r: this.sel.row0, c: this.sel.col0,
			selection: Object.assign({}, this.cellAt(this.sel.row0, this.sel.col0)?.doc.selection) } : null;
		this.stopInput();
		this.rowSizes = [];
		this.colSizes = [];
		for (let r = 0; r < rows; r++) {
			this.rowSizes.push(size(data.rows, r, DEFAULT_ROW_HEIGHT));
		}
		for (let c = 0; c < cols; c++) {
			this.colSizes.push(size(data.columns, c, DEFAULT_COLUMN_WIDTH));
		}
		this.cells = [];
		for (let r = 0; r < rows; r++) {
			const row = [];
			const source = Array.isArray(content[r]) ? content[r] : [];
			for (let c = 0; c < cols; c++) {
				const saved = source[c] && typeof source[c] === 'object' ? source[c] : {};
				const props = {};
				for (const key of Object.keys(saved)) {
					if (key !== 'content' && saved[key] !== null && saved[key] !== undefined) {
						props[key] = saved[key];
					}
				}
				row.push(this.newCell(saved.content, props));
			}
			this.cells.push(row);
		}
		this.vborders = this.validBorders(data.vborders, rows, cols + 1);
		this.hborders = this.validBorders(data.hborders, rows + 1, cols);
		this.props = {};
		for (const key of CELL_PROPERTIES) {
			if (data[key] !== null && data[key] !== undefined) {
				this.props[key] = data[key];
			}
		}
		this.updateCellLayouts();
		if (this.sel) {
			if (this.sel.row0 >= rows || this.sel.col0 >= cols) {
				this.sel = null;
			} else if (editing) {
				const cell = this.cellAt(editing.r, editing.c);
				this.sel = { col0: editing.c, row0: editing.r, editing: true };
				this.startInput(cell);
				cell.doc.select(editing.selection.start, editing.selection.end, false);
			}
		}
	}

	validBorders(borders, rows, cols) {
		if (!Array.isArray(borders) || borders.length !== rows) {
			return null;
		}
		return borders.map((line) => {
			const out = [];
			for (let c = 0; c < cols; c++) {
				const value = Array.isArray(line) ? Number(line[c]) : 1;
				out.push(value >= 0 ? value : 1);
			}
			return out;
		});
	}

	save() {
		const content = this.cells.map((row) => row.map((cell) => {
			const saved = { content: cell.doc.isEmpty() && !Object.keys(cell.doc.model.chars[0].f).length
				? null : cell.doc.save() };
			for (const key of CELL_PROPERTIES) {
				if (cell.props[key] !== undefined && cell.props[key] !== null) {
					saved[key] = cell.props[key];
				}
			}
			for (const key of Object.keys(cell.props)) {
				if (!(key in saved) && cell.props[key] !== null && cell.props[key] !== undefined) {
					saved[key] = cell.props[key];
				}
			}
			return saved;
		}));
		const result = {
			rows: this.rowSizes.map(round),
			columns: this.colSizes.map(round),
			content,
			vborders: copyBorders(this.vborders),
			hborders: copyBorders(this.hborders)
		};
		for (const key of CELL_PROPERTIES) {
			result[key] = this.props[key] === undefined ? null : this.props[key];
		}
		return result;
	}

	cellAt(r, c) {
		return this.cells[r] && this.cells[r][c];
	}

	cellProperty(cell, key) {
		const value = cell.props[key] ?? this.props[key];
		return value === undefined || value === null ? PROPERTY_DEFAULTS[key] : value;
	}

	// --- geometry ---

	colX(c) {
		return sum(this.colSizes, 0, c);
	}

	rowY(r) {
		return sum(this.rowSizes, 0, r);
	}

	cellIndex(x, y) {
		let c = 0;
		let left = 0;
		while (c < this.cols - 1 && x >= left + this.colSizes[c]) {
			left += this.colSizes[c];
			c++;
		}
		let r = 0;
		let top = 0;
		while (r < this.rows - 1 && y >= top + this.rowSizes[r]) {
			top += this.rowSizes[r];
			r++;
		}
		return { r, c };
	}

	getHitCell(x, y) {
		const { r, c } = this.cellIndex(x, y);
		return { col0: c, row0: r };
	}

	/** Width available to the text of a cell. */
	textWidth(r, c) {
		const rotation = this.cellProperty(this.cells[r][c], 'rotation');
		const size = rotation === 'up' || rotation === 'down' ? this.rowSizes[r] : this.colSizes[c];
		return Math.max(1, size - 2 * CELL_PADDING);
	}

	updateCellLayout(r, c) {
		const cell = this.cells[r][c];
		const doc = cell.doc;
		doc.wrap = this.cellProperty(cell, 'wrapping') !== 'clip';
		doc.defaultAlign = this.cellProperty(cell, 'halign');
		doc.scale = this.scale;
		doc.setWidth(this.textWidth(r, c));
		doc.invalidate();
	}

	updateCellLayouts() {
		for (let r = 0; r < this.rows; r++) {
			for (let c = 0; c < this.cols; c++) {
				this.updateCellLayout(r, c);
			}
		}
	}

	/**
	 * Transform between cell coordinates and text coordinates.
	 * Returns {origin, rotation} so that cell = origin + rotate(text).
	 */
	textFrame(r, c) {
		const cell = this.cells[r][c];
		const w = this.colSizes[c];
		const h = this.rowSizes[r];
		const rotation = this.cellProperty(cell, 'rotation');
		const valign = this.cellProperty(cell, 'valign');
		const textHeight = cell.doc.layout().height;
		const across = rotation === 'up' || rotation === 'down' ? w : h;
		let offset = CELL_PADDING;
		if (valign === 'middle') {
			offset = (across - textHeight) / 2;
		} else if (valign === 'bottom') {
			offset = across - CELL_PADDING - textHeight;
		}
		if (rotation === 'up') {
			return { x: offset, y: h - CELL_PADDING, angle: -Math.PI / 2 };
		}
		if (rotation === 'down') {
			return { x: w - offset, y: CELL_PADDING, angle: Math.PI / 2 };
		}
		return { x: CELL_PADDING, y: offset, angle: 0 };
	}

	/** Table coordinates to text coordinates of cell (r, c). */
	toText(r, c, x, y) {
		const frame = this.textFrame(r, c);
		const cx = x - this.colX(c);
		const cy = y - this.rowY(r);
		if (frame.angle < 0) {
			return { x: frame.y - cy, y: cx - frame.x };
		}
		if (frame.angle > 0) {
			return { x: cy - frame.y, y: frame.x - cx };
		}
		return { x: cx - frame.x, y: cy - frame.y };
	}

	/** Grows the row of a cell whose text no longer fits (reported as sizeChanged). */
	growRowFor(cell) {
		for (let r = 0; r < this.rows; r++) {
			const c = this.cells[r].indexOf(cell);
			if (c < 0) {
				continue;
			}
			const rotation = this.cellProperty(cell, 'rotation');
			if (rotation === 'up' || rotation === 'down') {
				return;
			}
			const needed = Math.ceil(cell.doc.layout().height) + 2 * CELL_PADDING;
			if (needed > this.rowSizes[r]) {
				this.rowSizes[r] = needed;
				for (let k = 0; k < this.cols; k++) {
					if (k !== c) {
						this.updateCellLayout(r, k);
					}
				}
				this.fire('size');
			}
			return;
		}
	}

	// --- drawing ---

	borderAt(lines, i, j) {
		return lines ? lines[i][j] : 1;
	}

	draw(ctx) {
		ctx.save();
		const rows = this.rows;
		const cols = this.cols;
		for (let r = 0; r < rows; r++) {
			for (let c = 0; c < cols; c++) {
				const bg = this.cellProperty(this.cells[r][c], 'bgcolor');
				if (bg && bg !== 'transparent') {
					ctx.fillStyle = bg;
					ctx.fillRect(this.colX(c), this.rowY(r), this.colSizes[c], this.rowSizes[r]);
				}
			}
		}
		const region = this.sel && !this.sel.editing && this.sel.row1 ? this.region(this.sel) : null;
		if (region) {
			ctx.fillStyle = textStyle.selectionColor;
			ctx.fillRect(this.colX(region.c0), this.rowY(region.r0),
				sum(this.colSizes, region.c0, region.c1), sum(this.rowSizes, region.r0, region.r1));
		}
		for (let r = 0; r < rows; r++) {
			for (let c = 0; c < cols; c++) {
				const cell = this.cells[r][c];
				const x = this.colX(c);
				const y = this.rowY(r);
				ctx.save();
				ctx.beginPath();
				ctx.rect(x, y, this.colSizes[c], this.rowSizes[r]);
				ctx.clip();
				const frame = this.textFrame(r, c);
				ctx.translate(x + frame.x, y + frame.y);
				if (frame.angle) {
					ctx.rotate(frame.angle);
				}
				cell.doc.draw(ctx);
				ctx.restore();
			}
		}
		this.drawBorders(ctx);
		if (this.sel) {
			const selected = this.region(this.sel);
			ctx.strokeStyle = textStyle.activeCellColor;
			ctx.lineWidth = 2 / this.scale;
			ctx.strokeRect(this.colX(selected.c0), this.rowY(selected.r0),
				sum(this.colSizes, selected.c0, selected.c1), sum(this.rowSizes, selected.r0, selected.r1));
		}
		ctx.restore();
	}

	drawBorders(ctx) {
		ctx.fillStyle = textStyle.tableBorderColor;
		for (let r = 0; r <= this.rows; r++) {
			const y = this.rowY(r);
			for (let c = 0; c < this.cols; c++) {
				const t = this.borderAt(this.hborders, r, c);
				if (t > 0) {
					ctx.fillRect(this.colX(c) - t / 2, y - t / 2, this.colSizes[c] + t, t);
				}
			}
		}
		for (let r = 0; r < this.rows; r++) {
			for (let c = 0; c <= this.cols; c++) {
				const t = this.borderAt(this.vborders, r, c);
				if (t > 0) {
					ctx.fillRect(this.colX(c) - t / 2, this.rowY(r) - t / 2, t, this.rowSizes[r] + t);
				}
			}
		}
	}

	repaint() {
		this.updateCellLayouts();
		this.host.repaint();
	}

	// --- selection and editing ---

	isEditing(cell) {
		return !!(this.sel && this.sel.editing && this.cellAt(this.sel.row0, this.sel.col0) === cell);
	}

	editingCell() {
		return this.sel && this.sel.editing ? this.cellAt(this.sel.row0, this.sel.col0) : null;
	}

	/** Cell rectangle of a selection or range; the whole table without one. */
	region(range) {
		if (!range) {
			return { r0: 0, c0: 0, r1: this.rows, c1: this.cols };
		}
		const r0 = Math.max(0, Math.min(range.row0 | 0, this.rows - 1));
		const c0 = Math.max(0, Math.min(range.col0 | 0, this.cols - 1));
		const r1 = range.row1 ? Math.min(Math.max(range.row1 | 0, r0 + 1), this.rows) : r0 + 1;
		const c1 = range.col1 ? Math.min(Math.max(range.col1 | 0, c0 + 1), this.cols) : c0 + 1;
		return { r0, c0, r1, c1 };
	}

	cellsIn(region) {
		const list = [];
		for (let r = region.r0; r < region.r1; r++) {
			for (let c = region.c0; c < region.c1; c++) {
				list.push({ r, c, cell: this.cells[r][c] });
			}
		}
		return list;
	}

	setHitCell(x, y) {
		const { r, c } = this.cellIndex(x, y);
		if (this.sel && this.sel.editing && this.sel.row0 === r && this.sel.col0 === c) {
			return;
		}
		this.stopInput();
		this.sel = { col0: c, row0: r };
		this.fire('selection');
	}

	startEditing(selection, x, y) {
		const hit = selection || { col0: 0, row0: 0 };
		const r = Math.max(0, Math.min(hit.row0 | 0, this.rows - 1));
		const c = Math.max(0, Math.min(hit.col0 | 0, this.cols - 1));
		if (!this.rows || !this.cols) {
			return;
		}
		this.stopInput();
		this.sel = hit;
		hit.row0 = r;
		hit.col0 = c;
		delete hit.row1;
		delete hit.col1;
		hit.editing = true;
		const cell = this.cells[r][c];
		this.startInput(cell);
		let ordinal = cell.doc.maxCaret;
		if (typeof x === 'number' && typeof y === 'number') {
			const point = this.toText(r, c, x, y);
			ordinal = cell.doc.byCoordinate(point.x, point.y).ordinal;
		}
		cell.doc.select(ordinal, ordinal, true);
		this.fire('selection');
	}

	editCell(r, c, position) {
		this.startEditing({ col0: c, row0: r });
		const doc = this.cells[r][c].doc;
		const p = position === 'end' ? doc.maxCaret : position;
		doc.select(p, p, true);
	}

	startInput(cell) {
		if (this.input) {
			this.input.attach(cell.doc);
		}
	}

	stopInput() {
		const cell = this.editingCell();
		if (cell) {
			cell.doc.select(cell.doc.maxCaret, cell.doc.maxCaret, false);
			this.sel.editing = false;
			delete this.sel.editing;
		}
		if (this.input) {
			this.input.detach();
		}
	}

	stopEditing() {
		if (this.editingCell()) {
			this.stopInput();
			this.host.blur?.();
			this.fire('selection');
		}
	}

	removeSelection() {
		this.stopInput();
		if (this.sel) {
			this.sel = null;
			this.fire('selection');
		}
	}

	/** Keyboard navigation out of the edited cell. */
	navigate(key, doc) {
		const sel = this.sel;
		if (!sel || !sel.editing) {
			return false;
		}
		let r = sel.row0;
		let c = sel.col0;
		let position = 0;
		switch (key) {
		case 'Tab':
		case 'ArrowRight':
			if (c + 1 < this.cols) {
				c++;
			} else if (r + 1 < this.rows) {
				r++;
				c = 0;
			} else {
				return key === 'Tab';
			}
			break;
		case 'ShiftTab':
		case 'ArrowLeft':
			if (c > 0) {
				c--;
			} else if (r > 0) {
				r--;
				c = this.cols - 1;
			} else {
				return key === 'ShiftTab';
			}
			position = 'end';
			break;
		case 'ArrowUp':
			if (r === 0) {
				return false;
			}
			r--;
			position = 'end';
			break;
		case 'ArrowDown':
			if (r + 1 >= this.rows) {
				return false;
			}
			r++;
			break;
		default:
			return false;
		}
		if (key === 'Tab' || key === 'ShiftTab') {
			this.editCell(r, c, 0);
			const target = this.cells[r][c].doc;
			target.select(0, target.maxCaret, true);
		} else {
			this.editCell(r, c, position);
		}
		return doc !== undefined;
	}

	// --- text of the edited cell ---

	insert(text) {
		const cell = this.editingCell();
		if (cell) {
			cell.doc.insert(text);
		}
	}

	selectedRange() {
		const cell = this.editingCell();
		return cell ? cell.doc.selectedRange() : new EmptyRange();
	}

	hyperlinkRange() {
		const cell = this.editingCell();
		return cell ? cell.doc.hyperlinkRange() : new EmptyRange();
	}

	insertHyperlink(url, text) {
		const cell = this.editingCell();
		if (cell) {
			cell.doc.insertHyperlink(url, text);
		}
	}

	setHyperlinkUrl(url) {
		const cell = this.editingCell();
		if (cell) {
			cell.doc.setHyperlinkUrl(url);
		}
	}

	urlByCoordinate(x, y) {
		if (x < 0 || y < 0 || x > this.totalWidth || y > this.totalHeight || !this.rows) {
			return '';
		}
		const { r, c } = this.cellIndex(x, y);
		const point = this.toText(r, c, x, y);
		return this.cells[r][c].doc.urlByCoordinate(point.x, point.y);
	}

	addInsertFilter(filter) {
		this.insertFilters.push(filter);
	}

	// --- formatting ---

	targetCells() {
		return this.cellsIn(this.region(this.sel));
	}

	setFormatting(key, value) {
		const cell = this.editingCell();
		if (cell) {
			const selected = cell.doc.selectedRange();
			const range = selected.start === selected.end ? cell.doc.documentRange() : selected;
			range.setFormatting(key, value);
			return;
		}
		this.inBatch(() => {
			for (const { cell: target } of this.targetCells()) {
				target.doc.documentRange().setFormatting(key, value);
			}
		});
	}

	getFormatting(key, fallback) {
		const cell = this.editingCell();
		if (cell) {
			return cell.doc.selectedRange().getFormattingValue(key, fallback);
		}
		let value;
		let first = true;
		for (const { cell: target } of this.targetCells()) {
			const current = target.doc.documentRange().getFormatting()[key];
			if (first) {
				value = current;
				first = false;
			} else if (current !== value) {
				return fallback;
			}
		}
		return value === undefined || value === null || isMultipleValues(value) ? fallback : value;
	}

	getListStyle() {
		const cell = this.editingCell();
		if (cell) {
			return cell.doc.getListStyle();
		}
		let style;
		let first = true;
		for (const { cell: target } of this.targetCells()) {
			const current = target.doc.documentRange().getListStyle();
			if (first) {
				style = current;
				first = false;
			} else if (current !== style) {
				return null;
			}
		}
		return style ?? null;
	}

	switchListTo(listType) {
		const cell = this.editingCell();
		if (cell) {
			cell.doc.switchListTo(cell.doc.selectedRange(), listType);
			return;
		}
		const turnOff = this.getListStyle() === listType;
		this.inBatch(() => {
			for (const { cell: target } of this.targetCells()) {
				const range = target.doc.documentRange();
				if ((range.getListStyle() === listType) === turnOff) {
					target.doc.switchListTo(range, listType);
				}
			}
		});
	}

	// --- cell properties ---

	setCellProperty(property, value, range) {
		const region = range ? this.region(range) : this.sel ? this.region(this.sel) : null;
		if (region) {
			for (const { cell } of this.cellsIn(region)) {
				if (value === null || value === undefined) {
					delete cell.props[property];
				} else {
					cell.props[property] = value;
				}
			}
		} else if (value === null || value === undefined) {
			delete this.props[property];
		} else {
			this.props[property] = value;
		}
		this.updateCellLayouts();
		this.fire('content');
	}

	getCellProperty(property) {
		if (this.sel && this.rows && this.cols) {
			const region = this.region(this.sel);
			return this.cellProperty(this.cells[region.r0][region.c0], property);
		}
		const value = this.props[property];
		return value === undefined || value === null ? PROPERTY_DEFAULTS[property] : value;
	}

	// --- borders ---

	ensureBorders() {
		if (!this.vborders) {
			this.vborders = this.rowSizes.map(() => new Array(this.cols + 1).fill(1));
		}
		if (!this.hborders) {
			this.hborders = new Array(this.rows + 1).fill(0).map(() => new Array(this.cols).fill(1));
		}
	}

	/** Border lines of a region: [{lines, i, j, outer}] */
	bordersOf(region) {
		const list = [];
		for (let r = region.r0; r <= region.r1; r++) {
			for (let c = region.c0; c < region.c1; c++) {
				list.push({ lines: 'hborders', i: r, j: c, outer: r === region.r0 || r === region.r1 });
			}
		}
		for (let r = region.r0; r < region.r1; r++) {
			for (let c = region.c0; c <= region.c1; c++) {
				list.push({ lines: 'vborders', i: r, j: c, outer: c === region.c0 || c === region.c1 });
			}
		}
		return list;
	}

	borderValue(border) {
		return this.borderAt(this[border.lines], border.i, border.j);
	}

	setBorderThickness(thickness, range) {
		const region = this.region(range || this.sel);
		const borders = this.bordersOf(region);
		this.ensureBorders();
		const anyVisible = borders.some((b) => this.borderValue(b) > 0);
		for (const border of borders) {
			if (!anyVisible || this.borderValue(border) > 0) {
				this[border.lines][border.i][border.j] = thickness;
			}
		}
		this.fire('content');
	}

	getBorderThickness() {
		const borders = this.bordersOf(this.region(this.sel));
		const visible = borders.find((b) => this.borderValue(b) > 0);
		return visible ? this.borderValue(visible) : 0;
	}

	setBorderStyle(style) {
		const region = this.region(this.sel);
		const thickness = this.getBorderThickness() || 1;
		const outer = style === 'all' || style === 'outer' ? thickness : 0;
		const inner = style === 'all' || style === 'inner' ? thickness : 0;
		if (!['all', 'outer', 'inner', 'none'].includes(style)) {
			return;
		}
		this.ensureBorders();
		for (const border of this.bordersOf(region)) {
			this[border.lines][border.i][border.j] = border.outer ? outer : inner;
		}
		this.fire('content');
	}

	getBorderStyle() {
		const borders = this.bordersOf(this.region(this.sel));
		const outer = borders.filter((b) => b.outer).map((b) => this.borderValue(b) > 0);
		const inner = borders.filter((b) => !b.outer).map((b) => this.borderValue(b) > 0);
		const state = (values) => (values.every((v) => v) ? 'on' : values.every((v) => !v) ? 'off'
			: 'mixed');
		const o = state(outer);
		if (!inner.length) {
			return o === 'on' ? 'outer' : o === 'off' ? 'none' : 'mixed';
		}
		const i = state(inner);
		if (o === 'mixed' || i === 'mixed') {
			return 'mixed';
		}
		if (o === 'on') {
			return i === 'on' ? 'all' : 'outer';
		}
		return i === 'on' ? 'inner' : 'none';
	}

	// --- sizes ---

	setWidth(width) {
		this.colSizes = this.scaled(this.colSizes, width);
		this.updateCellLayouts();
	}

	setHeight(height) {
		this.rowSizes = this.scaled(this.rowSizes, height);
		this.updateCellLayouts();
	}

	scaled(sizes, total) {
		const target = Number(total);
		if (!(target > 0) || !sizes.length) {
			return sizes;
		}
		const current = sum(sizes);
		if (current <= 0) {
			return sizes.map(() => target / sizes.length);
		}
		return sizes.map((s) => s * target / current);
	}

	// --- rows and columns ---

	copiedCell(source) {
		const saved = source.doc.save();
		const first = saved[0] && typeof saved[0].text === 'string' ? saved[0] : null;
		const content = !source.doc.isEmpty() && first
			? [Object.assign({}, first, { text: '\n' })] : null;
		return this.newCell(content, source.props);
	}

	addRow(index, source) {
		const i = Math.max(0, Math.min(index, this.rows));
		const src = Math.max(0, Math.min(source, this.rows - 1));
		if (this.rows) {
			this.rowSizes.splice(i, 0, this.rowSizes[src]);
			this.cells.splice(i, 0, this.cells[src].map((cell) => this.copiedCell(cell)));
			if (this.vborders) {
				this.vborders.splice(i, 0, this.vborders[src].slice());
			}
			if (this.hborders) {
				this.hborders.splice(i, 0, this.hborders[src].slice());
			}
		} else {
			this.rowSizes.push(DEFAULT_ROW_HEIGHT);
			this.cells.push(this.colSizes.map(() => this.newCell(null, {})));
		}
		if (this.sel && this.sel.row0 >= i) {
			this.sel.row0++;
		}
		this.updateCellLayouts();
		this.fire('content');
	}

	addColumn(index, source) {
		const j = Math.max(0, Math.min(index, this.cols));
		const src = Math.max(0, Math.min(source, this.cols - 1));
		this.colSizes.splice(j, 0, this.cols ? this.colSizes[src] : DEFAULT_COLUMN_WIDTH);
		this.cells.forEach((row) => row.splice(j, 0, row.length ? this.copiedCell(row[src])
			: this.newCell(null, {})));
		if (this.vborders) {
			this.vborders.forEach((line) => line.splice(j, 0, line[src]));
		}
		if (this.hborders) {
			this.hborders.forEach((line) => line.splice(j, 0, line[src]));
		}
		if (this.sel && this.sel.col0 >= j) {
			this.sel.col0++;
		}
		this.updateCellLayouts();
		this.fire('content');
	}

	removeRow(index) {
		if (index < 0 || index >= this.rows) {
			return;
		}
		const wasEditing = this.editingCell();
		if (wasEditing && this.sel.row0 === index) {
			this.stopInput();
		}
		const last = index === this.rows - 1;
		this.rowSizes.splice(index, 1);
		this.cells.splice(index, 1);
		if (this.vborders) {
			this.vborders.splice(index, 1);
		}
		if (this.hborders) {
			this.hborders.splice(last ? index : index + 1, 1);
		}
		this.fixSelectionAfterRemove();
		this.updateCellLayouts();
		this.fire('content');
	}

	removeColumn(index) {
		if (index < 0 || index >= this.cols) {
			return;
		}
		const wasEditing = this.editingCell();
		if (wasEditing && this.sel.col0 === index) {
			this.stopInput();
		}
		const last = index === this.cols - 1;
		this.colSizes.splice(index, 1);
		this.cells.forEach((row) => row.splice(index, 1));
		if (this.vborders) {
			this.vborders.forEach((line) => line.splice(last ? index : index + 1, 1));
		}
		if (this.hborders) {
			this.hborders.forEach((line) => line.splice(index, 1));
		}
		this.fixSelectionAfterRemove();
		this.updateCellLayouts();
		this.fire('content');
	}

	fixSelectionAfterRemove() {
		if (!this.sel) {
			return;
		}
		if (!this.rows || !this.cols) {
			this.stopInput();
			this.sel = null;
			return;
		}
		this.sel.row0 = Math.min(this.sel.row0, this.rows - 1);
		this.sel.col0 = Math.min(this.sel.col0, this.cols - 1);
		delete this.sel.row1;
		delete this.sel.col1;
		if (this.sel.editing) {
			this.startInput(this.cells[this.sel.row0][this.sel.col0]);
		}
	}

	// --- host settings ---

	setExternalScale(scale) {
		this.scale = Number(scale) > 0 ? Number(scale) : 1;
		for (const row of this.cells) {
			for (const cell of row) {
				cell.doc.scale = this.scale;
			}
		}
	}

	setExternalPaint(value) {
		this.externalPaintValue = !!value;
		this.host.repaint();
	}

	/** Index of an inner column border near x (1..cols-1), or -1. */
	columnBorderAt(x, y) {
		if (y < 0 || y > this.totalHeight) {
			return -1;
		}
		const tolerance = BORDER_TOLERANCE / this.scale;
		for (let c = 1; c < this.cols; c++) {
			if (Math.abs(x - this.colX(c)) <= tolerance) {
				return c;
			}
		}
		return -1;
	}

	rowBorderAt(x, y) {
		if (x < 0 || x > this.totalWidth) {
			return -1;
		}
		const tolerance = BORDER_TOLERANCE / this.scale;
		for (let r = 1; r < this.rows; r++) {
			if (Math.abs(y - this.rowY(r)) <= tolerance) {
				return r;
			}
		}
		return -1;
	}

	/** Moves the border before track `index`, keeping the total size. */
	moveBorder(sizes, index, start, delta) {
		const a = start[0] + delta;
		const b = start[1] - delta;
		if (a < MIN_CELL_SIZE || b < MIN_CELL_SIZE) {
			const total = start[0] + start[1];
			sizes[index - 1] = Math.max(MIN_CELL_SIZE, Math.min(total - MIN_CELL_SIZE, a));
			sizes[index] = total - sizes[index - 1];
		} else {
			sizes[index - 1] = a;
			sizes[index] = b;
		}
		this.updateCellLayouts();
		this.fire('content');
	}
}

/** Creates a table editor in a DOM element (`murok.table.create`). */
export function createTable(element) {
	const document = element.ownerDocument;
	const view = document.defaultView;
	if (view.getComputedStyle(element).position === 'static') {
		element.style.position = 'absolute';
	}
	element.innerHTML = '';
	const canvas = document.createElement('canvas');
	canvas.className = 'murokTableCanvas';
	canvas.setAttribute('style', 'position: absolute; left: 0; top: 0; pointer-events: none;');
	const { wrapper, textarea } = createTextArea(document);
	element.appendChild(canvas);
	element.appendChild(wrapper);

	const table = new Table();
	let paintPending = false;
	const paint = () => {
		paintPending = false;
		if (table.externalPaintValue) {
			canvas.width = 0;
			canvas.height = 0;
			return;
		}
		paintInto(canvas, Math.max(1, table.totalWidth + 2), Math.max(1, table.totalHeight + 2),
			(ctx) => {
				ctx.translate(1, 1);
				table.draw(ctx);
			});
	};
	table.input = new TextInput(textarea, {
		navigate: (key, doc) => table.navigate(key, doc)
	});
	table.host = {
		focus: () => table.input.focus(),
		blur: () => textarea.blur(),
		hasFocus: () => table.input.isFocused(),
		repaint: () => {
			if (!table.externalPaintValue && !paintPending) {
				paintPending = true;
				view.requestAnimationFrame(paint);
			}
		}
	};
	textarea.addEventListener('focus', () => table.host.repaint());
	textarea.addEventListener('blur', () => table.host.repaint());

	let drag = null;
	const setCursor = (point) => {
		if (table.columnBorderAt(point.x, point.y) > 0) {
			element.style.cursor = 'col-resize';
		} else if (table.rowBorderAt(point.x, point.y) > 0) {
			element.style.cursor = 'row-resize';
		} else {
			element.style.cursor = 'text';
		}
	};
	element.addEventListener('pointerdown', (e) => {
		if (e.button !== 0 || !table.rows || !table.cols) {
			return;
		}
		e.preventDefault();
		const point = localPoint(element, e);
		const column = table.columnBorderAt(point.x, point.y);
		const row = column > 0 ? -1 : table.rowBorderAt(point.x, point.y);
		if (column > 0) {
			drag = { kind: 'column', index: column, from: point.x,
				start: [table.colSizes[column - 1], table.colSizes[column]] };
		} else if (row > 0) {
			drag = { kind: 'row', index: row, from: point.y,
				start: [table.rowSizes[row - 1], table.rowSizes[row]] };
		} else {
			const { r, c } = table.cellIndex(point.x, point.y);
			const cell = table.cells[r][c];
			if (table.isEditing(cell)) {
				const p = table.toText(r, c, point.x, point.y);
				const ordinal = cell.doc.byCoordinate(p.x, p.y).ordinal;
				if (e.shiftKey) {
					cell.doc.extendTo(ordinal);
				} else {
					cell.doc.select(ordinal, ordinal, true);
				}
				drag = { kind: 'text', r, c };
			} else {
				table.startEditing({ col0: c, row0: r }, point.x, point.y);
				drag = { kind: 'cells', r, c };
			}
		}
		if (element.setPointerCapture) {
			element.setPointerCapture(e.pointerId);
		}
	});
	element.addEventListener('pointermove', (e) => {
		const point = localPoint(element, e);
		if (!drag) {
			setCursor(point);
			return;
		}
		if (drag.kind === 'column') {
			table.moveBorder(table.colSizes, drag.index, drag.start, point.x - drag.from);
		} else if (drag.kind === 'row') {
			table.moveBorder(table.rowSizes, drag.index, drag.start, point.y - drag.from);
		} else if (drag.kind === 'text') {
			const p = table.toText(drag.r, drag.c, point.x, point.y);
			const doc = table.cells[drag.r][drag.c].doc;
			doc.extendTo(doc.byCoordinate(p.x, p.y).ordinal);
		} else if (drag.kind === 'cells') {
			const { r, c } = table.cellIndex(point.x, point.y);
			if (r !== drag.r || c !== drag.c || (table.sel && !table.sel.editing)) {
				const range = { col0: Math.min(c, drag.c), row0: Math.min(r, drag.r),
					col1: Math.max(c, drag.c) + 1, row1: Math.max(r, drag.r) + 1 };
				const old = table.sel;
				if (!old || old.editing || old.col0 !== range.col0 || old.row0 !== range.row0
						|| old.col1 !== range.col1 || old.row1 !== range.row1) {
					if (r === drag.r && c === drag.c) {
						table.startEditing({ col0: c, row0: r }, point.x, point.y);
					} else {
						table.stopInput();
						table.sel = range;
						table.fire('selection');
					}
				}
			}
		}
	});
	const endDrag = () => {
		if (drag && (drag.kind === 'column' || drag.kind === 'row')) {
			table.fire('content');
		}
		drag = null;
		if (table.editingCell()) {
			table.input.focus();
		}
	};
	element.addEventListener('pointerup', endDrag);
	element.addEventListener('pointercancel', endDrag);
	element.addEventListener('dblclick', (e) => {
		const point = localPoint(element, e);
		const { r, c } = table.cellIndex(point.x, point.y);
		const cell = table.cells[r][c];
		if (table.isEditing(cell)) {
			const p = table.toText(r, c, point.x, point.y);
			const range = wordRange(cell.doc, cell.doc.byCoordinate(p.x, p.y).ordinal);
			cell.doc.select(range.start, range.end, true);
		}
	});
	return table;
}
