// Content format tests: the saved runs must match what GeoGebra files contain.
import test from 'node:test';
import assert from 'node:assert/strict';
import { RichText } from '../src/richtext.js';
import { json, useFakeMeasure } from './helpers.js';

useFakeMeasure();

function doc(runs) {
	const d = new RichText();
	d.setWidth(300);
	d.load(runs);
	return d;
}

test('load normalizes the end of the document', () => {
	assert.equal(json(doc([]).save()), '[{"text":"\\n"}]');
	assert.equal(json(doc([{ text: 'Hello world' }]).save()), '[{"text":"Hello world\\n"}]');
	assert.equal(json(doc([{ text: 'Hello world\n' }]).save()), '[{"text":"Hello world\\n"}]');
	// the final newline takes the formatting of the character before it
	assert.equal(json(doc([{ text: 'a' }, { text: '\n', italic: true }]).save()), '[{"text":"a\\n"}]');
	assert.equal(json(doc([{ text: 'Hello\n', bold: true }, { text: '\n' }]).save()),
		'[{"text":"Hello\\n\\n","bold":true}]');
	// a document that is only a newline keeps its formatting (mind map node default)
	assert.equal(json(doc([{ text: '\n', align: 'center' }]).save()), '[{"text":"\\n","align":"center"}]');
});

test('document range covers the final newline, the caret stays before it', () => {
	const d = doc([{ text: 'Hello world' }]);
	assert.equal(d.documentRange().end, 12);
	d.select(0, 99);
	assert.deepEqual(d.selection, { start: 0, end: 11 });
});

test('formatting keys are saved in canonical order without defaults', () => {
	const d = doc([{ text: 'Hello world\nSecond line' }]);
	d.select(0, 3);
	const r = d.selectedRange();
	r.setFormatting('size', 20);
	r.setFormatting('color', '#FF0000');
	r.setFormatting('font', 'Georgia, serif');
	r.setFormatting('script', 'super');
	r.setFormatting('italic', true);
	r.setFormatting('underline', true);
	r.setFormatting('strikeout', true);
	r.setFormatting('bgcolor', '#00FF00');
	assert.equal(json(d.save()), '[{"text":"Hel","size":20,"font":"Georgia, serif","color":"#FF0000",'
		+ '"bgcolor":"#00FF00","italic":true,"underline":true,"strikeout":true,"script":"super"},'
		+ '{"text":"lo world\\nSecond line\\n"}]');
	d.select(0, 3);
	d.selectedRange().setFormatting('italic', false);
	assert.equal(json(d.save()[0]), '{"text":"Hel","size":20,"font":"Georgia, serif","color":"#FF0000",'
		+ '"bgcolor":"#00FF00","underline":true,"strikeout":true,"script":"super"}');
});

test('formatting the whole document includes the final newline', () => {
	const d = doc([]);
	d.select(0, 0);
	d.insert('GeoGebra Rocks');
	d.documentRange().setFormatting('bold', true);
	assert.equal(json(d.save()), '[{"text":"GeoGebra Rocks\\n","bold":true}]');
	d.documentRange().setFormatting('bold', false);
	d.documentRange().setFormatting('underline', true);
	assert.equal(json(d.save()), '[{"text":"GeoGebra Rocks\\n","underline":true}]');
});

test('getFormattingValue: uniform value, defaults, and fallback for mixed values', () => {
	const d = doc([{ text: 'Hello', bold: true }, { text: ' world' }]);
	const all = d.documentRange();
	assert.equal(all.getFormattingValue('bold', 'FB'), 'FB');
	assert.equal(all.getFormattingValue('font', ''), 'Arial, sans-serif');
	assert.equal(all.getFormattingValue('size', 0), 16);
	assert.equal(all.getFormattingValue('script', 'x'), 'normal');
	assert.equal(all.getFormattingValue('url', 'x'), '');
	d.select(5, 5);
	assert.equal(d.selectedRange().getFormattingValue('bold', 'FB'), true);
	d.select(6, 6);
	assert.equal(d.selectedRange().getFormattingValue('bold', 'FB'), false);
	d.select(0, 0);
	assert.equal(d.selectedRange().getFormattingValue('bold', 'FB'), true);
});

test('collapsed formatting applies to the next insertion', () => {
	const d = doc([{ text: 'abc' }]);
	d.select(3, 3);
	d.selectedRange().setFormatting('size', 30);
	assert.equal(d.selectedRange().getFormattingValue('size', 0), 30);
	d.insert('Z');
	assert.equal(json(d.save()), '[{"text":"abc"},{"text":"Z\\n","size":30}]');
});

test('inserted text takes the formatting of the character before', () => {
	const d = doc([{ text: 'ab', bold: true }, { text: 'c\n' }]);
	d.select(1, 1);
	d.insert('X');
	assert.equal(json(d.save()), '[{"text":"aXb","bold":true},{"text":"c\\n"}]');
	d.select(0, 3);
	d.insert('Y');
	assert.equal(json(d.save()), '[{"text":"Y","bold":true},{"text":"c\\n"}]');
	assert.deepEqual(d.selection, { start: 1, end: 1 });
});

test('alignment applies to whole paragraphs', () => {
	const d = doc([{ text: 'Hello world\nSecond line' }]);
	d.select(1, 1);
	d.selectedRange().setFormatting('align', 'center');
	assert.equal(json(d.save()), '[{"text":"Hello world\\n","align":"center"},{"text":"Second line\\n"}]');
	d.select(1, 14);
	d.selectedRange().setFormatting('align', 'right');
	assert.equal(json(d.save()), '[{"text":"Hello world\\nSecond line\\n","align":"right"}]');
});

test('lists are saved as listStart / listNext / listEnd codes', () => {
	const d = doc([{ text: 'Hello world\nSecond line' }]);
	d.switchListTo(d.documentRange(), 'bullet');
	assert.equal(json(d.save()), '[{"text":{"$":"listStart","marker":"bullet"}},{"text":"Hello world"},'
		+ '{"text":{"$":"listNext"}},{"text":"Second line"},{"text":{"$":"listEnd"}}]');
	assert.equal(d.documentRange().getListStyle(), 'bullet');
	d.switchListTo(d.documentRange(), 'number');
	assert.equal(json(d.save()), '[{"text":{"$":"listStart"}},{"text":"Hello world"},'
		+ '{"text":{"$":"listNext"}},{"text":"Second line"},{"text":{"$":"listEnd"}}]');
	assert.equal(d.documentRange().getListStyle(), 'number');
	d.switchListTo(d.documentRange(), 'number');
	assert.equal(json(d.save()), '[{"text":"Hello world\\nSecond line\\n"}]');
	assert.equal(d.documentRange().getListStyle(), null);
});

test('a list can cover only the current paragraph', () => {
	const d = doc([{ text: 'Hello world\nSecond line' }]);
	d.select(2, 2);
	d.switchListTo(d.selectedRange(), 'bullet');
	assert.equal(json(d.save()), '[{"text":{"$":"listStart","marker":"bullet"}},{"text":"Hello world"},'
		+ '{"text":{"$":"listEnd"}},{"text":"Second line\\n"}]');
	assert.equal(d.selectedRange().getListStyle(), 'bullet');
	assert.deepEqual(d.selection, { start: 3, end: 3 });
});

test('list repair on load', () => {
	assert.equal(json(doc([{ text: 'a' }, { text: { $: 'listStart' } }, { text: 'b' },
		{ text: { $: 'listEnd' } }]).save()),
	'[{"text":"a\\n"},{"text":{"$":"listStart"}},{"text":"b"},{"text":{"$":"listEnd"}}]');
	assert.equal(json(doc([{ text: 'a\n' }, { text: { $: 'listStart' } }, { text: 'b' }]).save()),
		'[{"text":"a\\n"},{"text":{"$":"listStart"}},{"text":"b"},{"text":{"$":"listEnd"}}]');
	assert.equal(json(doc([{ text: 'a\n' }, { text: { $: 'listNext' } }, { text: 'b' },
		{ text: { $: 'listEnd' } }]).save()),
	'[{"text":"a\\n"},{"text":{"$":"listStart"}},{"text":"b"},{"text":{"$":"listEnd"}}]');
	assert.equal(json(doc([{ text: 'a' }, { text: { $: 'listEnd' } }]).save()), '[{"text":"a\\n"}]');
});

test('Enter in a list adds an item, Enter on an empty item leaves the list', () => {
	const d = doc([{ text: 'abc' }]);
	d.switchListTo(d.documentRange(), 'bullet');
	d.select(4, 4);
	d.newline();
	d.typeText('def');
	assert.equal(json(d.save()), '[{"text":{"$":"listStart","marker":"bullet"}},{"text":"abc"},'
		+ '{"text":{"$":"listNext"}},{"text":"def"},{"text":{"$":"listEnd"}}]');
	assert.deepEqual(d.selection, { start: 8, end: 8 });
	d.newline();
	d.newline();
	assert.equal(json(d.save()), '[{"text":{"$":"listStart","marker":"bullet"}},{"text":"abc"},'
		+ '{"text":{"$":"listNext"}},{"text":"def"},{"text":{"$":"listEnd"}},{"text":"\\n"}]');
	assert.deepEqual(d.selection, { start: 9, end: 9 });
	d.typeText('after');
	assert.equal(json(d.save().slice(-1)), '[{"text":"after\\n"}]');
});

test('Enter on an empty middle item splits the list and keeps its type', () => {
	const d = doc([{ text: { $: 'listStart', marker: 'bullet' } }, { text: 'a' }, { text: { $: 'listNext' } },
		{ text: { $: 'listNext' } }, { text: 'b' }, { text: { $: 'listEnd' } }]);
	d.select(3, 3);
	d.newline();
	assert.equal(json(d.save()), '[{"text":{"$":"listStart","marker":"bullet"}},{"text":"a"},'
		+ '{"text":{"$":"listEnd"}},{"text":"\\n"},{"text":{"$":"listStart","marker":"bullet"}},'
		+ '{"text":"b"},{"text":{"$":"listEnd"}}]');
});

test('Backspace at the start of the first item removes the list marker', () => {
	const d = doc([{ text: 'abc' }]);
	d.switchListTo(d.documentRange(), 'bullet');
	d.select(1, 1);
	d.deleteBackward();
	assert.equal(json(d.save()), '[{"text":"abc\\n"}]');
	assert.deepEqual(d.selection, { start: 0, end: 0 });
	const two = doc([{ text: 'abc\ndef' }]);
	two.switchListTo(two.documentRange(), 'bullet');
	two.select(1, 1);
	two.deleteBackward();
	assert.equal(json(two.save()), '[{"text":"abc\\n"},{"text":{"$":"listStart","marker":"bullet"}},'
		+ '{"text":"def"},{"text":{"$":"listEnd"}}]');
});

test('hyperlinks', () => {
	const d = doc([{ text: 'Hello world\nSecond line' }]);
	d.select(6, 11);
	d.insertHyperlink('https://a.b', 'LINK');
	assert.equal(json(d.save()), '[{"text":"Hello "},{"text":"LINK","color":"#0E7C86","underline":true,'
		+ '"url":"https://a.b"},{"text":"\\nSecond line\\n"}]');
	assert.deepEqual(d.selection, { start: 10, end: 10 });
	d.select(8, 8);
	const link = d.hyperlinkRange();
	assert.deepEqual([link.start, link.end, link.plainText()], [6, 10, 'LINK']);
	assert.equal(d.selectedRange().getFormattingValue('url', ''), 'https://a.b');
	d.setHyperlinkUrl('https://c.d');
	assert.equal(d.save()[1].url, 'https://c.d');
	d.select(0, 0);
	d.insertHyperlink('https://x.y', '');
	assert.equal(d.save()[0].text, 'https://x.y');
});

test('undo and redo restore content and selection', () => {
	const d = doc([{ text: 'Hello' }]);
	d.select(5, 5);
	d.typeText(' world');
	d.select(0, 5);
	d.selectedRange().setFormatting('bold', true);
	assert.equal(json(d.save()), '[{"text":"Hello","bold":true},{"text":" world\\n"}]');
	d.performUndo();
	assert.equal(json(d.save()), '[{"text":"Hello world\\n"}]');
	d.performUndo();
	assert.equal(json(d.save()), '[{"text":"Hello\\n"}]');
	d.performUndo(true);
	assert.equal(json(d.save()), '[{"text":"Hello world\\n"}]');
});

test('insert filters can change or drop typed text', () => {
	const d = doc([{ text: 'abc' }]);
	d.insertFilters.push((s) => s.toUpperCase());
	d.select(3, 3);
	d.typeText('xy');
	d.insertFilters.length = 0;
	d.insertFilters.push(() => null);
	d.typeText('q');
	assert.equal(json(d.save()), '[{"text":"abcXY\\n"}]');
});

test('events: content and selection listeners fire', () => {
	const d = doc([{ text: 'abc' }]);
	const log = [];
	d.contentChanged(() => log.push('c'));
	d.selectionChanged(() => log.push('s'));
	d.select(3, 3);
	d.typeText('d');
	assert.deepEqual(log, ['s', 'c', 's']);
	log.length = 0;
	d.load([{ text: 'x' }]);
	assert.deepEqual(log, ['c', 's']);
});

test('unknown run keys and code objects survive a round trip', () => {
	const runs = [{ text: 'a', custom: 'keep' }, { text: { $: 'mystery', value: 3 } }, { text: 'b\n' }];
	assert.equal(json(doc(runs).save()), json(runs));
});

test('plain text of lists uses newlines between items', () => {
	const d = doc([{ text: 'abc\ndef' }]);
	d.switchListTo(d.documentRange(), 'number');
	assert.equal(d.documentRange().plainText(), 'abc\ndef\n');
});
