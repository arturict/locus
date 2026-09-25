// Table model tests (no DOM): saved format, cell properties, borders, rows and columns.
import test from 'node:test';
import assert from 'node:assert/strict';
import { Table } from '../src/table.js';
import { json, useFakeMeasure } from './helpers.js';

useFakeMeasure();

function table(rows = 2, cols = 2) {
	const t = new Table();
	t.init(rows, cols);
	return t;
}

test('a new table has the default sizes and saved form', () => {
	const t = table();
	assert.equal(json(t.save()), '{"rows":[36,36],"columns":[100,100],"content":[[{"content":null},'
		+ '{"content":null}],[{"content":null},{"content":null}]],"vborders":null,"hborders":null,'
		+ '"bgcolor":null,"wrapping":null,"valign":null,"halign":null,"rotation":null}');
	assert.deepEqual([t.totalWidth, t.totalHeight, t.getMinWidth(), t.getMinHeight(), t.rows, t.cols],
		[200, 72, 32, 32, 2, 2]);
	assert.equal(t.selection, null);
	assert.deepEqual(['bgcolor', 'valign', 'halign', 'wrapping', 'rotation'].map((p) => t.getCellProperty(p)),
		['transparent', 'top', 'left', 'wrap', 'none']);
	assert.deepEqual([t.getBorderThickness(), t.getBorderStyle(), t.getFormatting('font', 'FB'),
		t.getFormatting('size', 'FB'), t.getListStyle()], [1, 'all', 'Arial, sans-serif', 16, null]);
});

test('editing a cell stores its runs', () => {
	const t = table();
	const hit = t.getHitCell(150, 30);
	assert.deepEqual(hit, { col0: 1, row0: 0 });
	t.startEditing(hit, 150, 30);
	assert.deepEqual(t.selection, { col0: 1, row0: 0, editing: true });
	t.insert('abc');
	assert.equal(json(t.save().content[0][1]), '{"content":[{"text":"abc\\n"}]}');
	assert.deepEqual([t.selectedRange().start, t.selectedRange().end], [3, 3]);
	t.setFormatting('bold', true);
	assert.equal(json(t.save().content[0][1]), '{"content":[{"text":"abc\\n","bold":true}]}');
	assert.equal(t.getFormatting('bold', 'FB'), true);
	t.stopEditing();
	t.removeSelection();
	assert.equal(t.selection, null);
	assert.equal(t.selectedRange().plainText(), '');
});

test('cell properties: table level without selection, cell level with one', () => {
	const t = table();
	t.setCellProperty('bgcolor', '#FF0000');
	assert.equal(t.save().bgcolor, '#FF0000');
	t.setHitCell(10, 10);
	assert.deepEqual(t.selection, { col0: 0, row0: 0 });
	t.setCellProperty('bgcolor', '#123456');
	t.setCellProperty('valign', 'bottom');
	assert.equal(json(t.save().content[0][0]), '{"content":null,"bgcolor":"#123456","valign":"bottom"}');
	assert.equal(t.getCellProperty('bgcolor'), '#123456');
	t.removeSelection();
	t.setCellProperty('valign', 'middle');
	t.setCellProperty('halign', 'center', null);
	t.setCellProperty('wrapping', 'clip');
	t.setCellProperty('rotation', 'up');
	const saved = t.save();
	assert.deepEqual([saved.valign, saved.halign, saved.wrapping, saved.rotation],
		['middle', 'center', 'clip', 'up']);
	t.setCellProperty('bgcolor', '#00FF00', { col0: 0, row0: 0, col1: 2, row1: 1 });
	assert.deepEqual(t.save().content[0].map((c) => c.bgcolor), ['#00FF00', '#00FF00']);
	assert.equal(t.save().content[1][0].bgcolor, undefined);
});

test('border thickness and style', () => {
	const t = table();
	t.setBorderThickness(3);
	t.setBorderStyle('inner');
	let saved = t.save();
	assert.equal(json(saved.vborders), '[[0,3,0],[0,3,0]]');
	assert.equal(json(saved.hborders), '[[0,0],[3,3],[0,0]]');
	assert.deepEqual([t.getBorderThickness(), t.getBorderStyle()], [3, 'inner']);
	t.setBorderStyle('outer');
	assert.equal(t.getBorderStyle(), 'outer');
	t.setBorderStyle('none');
	assert.equal(t.getBorderStyle(), 'none');
	t.setBorderStyle('all');
	saved = t.save();
	assert.equal(json(saved.vborders), '[[1,1,1],[1,1,1]]');
	assert.equal(t.getBorderStyle(), 'all');

	const single = table();
	single.setHitCell(10, 10);
	single.setBorderThickness(3);
	assert.equal(single.getBorderStyle(), 'outer');
	assert.equal(single.getBorderThickness(), 3);
	assert.equal(json(single.save().vborders), '[[3,3,1],[1,1,1]]');
	assert.equal(json(single.save().hborders), '[[3,1],[3,1],[1,1]]');
});

test('rows and columns copy the formatting of their source', () => {
	const t = table();
	t.setBorderThickness(3);
	t.setBorderStyle('inner');
	t.startEditing({ col0: 1, row0: 0 });
	t.insert('abc');
	t.setFormatting('bold', true);
	t.stopEditing();
	t.removeSelection();
	t.setCellProperty('bgcolor', '#00FF00', { col0: 0, row0: 0, col1: 2, row1: 1 });
	t.addRow(1, 0);
	let saved = t.save();
	assert.equal(json(saved.rows), '[36,36,36]');
	assert.equal(json(saved.content[1]), '[{"content":null,"bgcolor":"#00FF00"},'
		+ '{"content":[{"text":"\\n","bold":true}],"bgcolor":"#00FF00"}]');
	assert.equal(json(saved.vborders), '[[0,3,0],[0,3,0],[0,3,0]]');
	assert.equal(json(saved.hborders), '[[0,0],[0,0],[3,3],[0,0]]');
	t.addColumn(0, 0);
	saved = t.save();
	assert.equal(json(saved.columns), '[100,100,100]');
	assert.equal(json(saved.vborders), '[[0,0,3,0],[0,0,3,0],[0,0,3,0]]');
	assert.equal(json(saved.hborders), '[[0,0,0],[0,0,0],[3,3,3],[0,0,0]]');
	t.removeRow(0);
	t.removeColumn(0);
	saved = t.save();
	assert.deepEqual([t.rows, t.cols], [2, 2]);
	assert.equal(json(saved.vborders), '[[0,3,0],[0,3,0]]');
	assert.equal(json(saved.hborders), '[[0,0],[3,3],[0,0]]');
});

test('removing every row leaves an empty table', () => {
	const t = table(1, 1);
	t.removeRow(0);
	assert.deepEqual([t.rows, t.totalHeight], [0, 0]);
});

test('setWidth and setHeight scale tracks proportionally', () => {
	const t = table();
	t.setWidth(400);
	t.setHeight(200);
	assert.equal(json(t.save().rows), '[100,100]');
	assert.equal(json(t.save().columns), '[200,200]');
	assert.deepEqual([t.getMinWidth(), t.getMinHeight()], [32, 32]);
});

test('load and save round trip', () => {
	const data = {
		rows: [36, 50], columns: [100, 80],
		content: [[{ content: [{ text: 'a\n' }] }, { content: [{ text: 'b\n', bold: true }], halign: 'right' }],
			[{ content: null }, { content: null, bgcolor: '#ABCDEF' }]],
		vborders: [[1, 3, 1], [1, 1, 1]], hborders: null,
		bgcolor: null, wrapping: null, valign: 'middle', halign: null, rotation: null
	};
	const t = table();
	t.load(data);
	assert.equal(json(t.save()), json(data));
	assert.deepEqual([t.getBorderStyle(), t.getBorderThickness()], ['all', 1]);
});

test('formatting without an edited cell applies to every cell', () => {
	const t = table();
	t.load({ rows: [36, 36], columns: [100, 100], content: [[{ content: [{ text: 'a\n' }] },
		{ content: [{ text: 'b\n', bold: true }] }], [{ content: null }, { content: null }]] });
	assert.equal(t.getFormatting('bold', 'FB'), 'FB');
	t.setFormatting('italic', true);
	assert.equal(t.getFormatting('italic', 'FB'), true);
	assert.equal(json(t.save().content[0][1]), '{"content":[{"text":"b\\n","bold":true,"italic":true}]}');
	t.setHitCell(10, 10);
	t.setFormatting('size', 30);
	assert.equal(t.getFormatting('size', 'FB'), 30);
	assert.equal(json(t.save().content[0][0]), '{"content":[{"text":"a\\n","size":30,"italic":true}]}');
});

test('typing more lines grows the row and reports a size change', () => {
	const t = table();
	let sizeChanges = 0;
	t.sizeChanged(() => sizeChanges++);
	t.startEditing({ col0: 0, row0: 0 });
	t.insert('one');
	t.cells[0][0].doc.newline();
	t.insert('two');
	t.cells[0][0].doc.newline();
	t.insert('three');
	assert.equal(t.save().rows[0], 3 * 16 + 16);
	assert.ok(sizeChanges > 0);
	assert.equal(t.totalHeight, 64 + 36);
});

test('Tab moves to the next cell', () => {
	const t = table();
	t.startEditing({ col0: 0, row0: 0 });
	t.navigate('Tab', t.cells[0][0].doc);
	assert.deepEqual([t.selection.row0, t.selection.col0, t.selection.editing], [0, 1, true]);
	t.navigate('Tab', t.cells[0][1].doc);
	assert.deepEqual([t.selection.row0, t.selection.col0], [1, 0]);
	t.navigate('ArrowUp', t.cells[1][0].doc);
	assert.deepEqual([t.selection.row0, t.selection.col0], [0, 0]);
});

test('rotated cells map pointer coordinates into the text', () => {
	const t = table();
	t.setHitCell(10, 10);
	t.setCellProperty('rotation', 'up');
	// rotated up: text runs from the bottom edge upwards
	const p = t.toText(0, 0, 8, 36 - 8 - 25);
	assert.deepEqual(p, { x: 25, y: 0 });
});

test('urls inside cells', () => {
	const t = table();
	t.load({ rows: [36], columns: [200], content: [[{ content: [{ text: 'x', url: 'https://a.b' }] }]] });
	assert.equal(t.urlByCoordinate(12, 15), 'https://a.b');
	assert.equal(t.urlByCoordinate(150, 15), '');
});
