// Contents written by GeoGebra's former editor (observed through its public API) must load
// and save unchanged, otherwise opening a GeoGebra file would mark it as modified.
import test from 'node:test';
import assert from 'node:assert/strict';
import { RichText } from '../src/richtext.js';
import { Table } from '../src/table.js';
import { useFakeMeasure } from './helpers.js';

useFakeMeasure();

const texts = [
	'[{"text":"GeoGebra Rocks\\n","bold":true}]',
	'[{"text":"Text element example\\n","underline":true}]',
	'[{"text":"Hel","size":20,"font":"Georgia, serif","color":"#FF0000","bgcolor":"#00FF00","italic":true,'
		+ '"underline":true,"strikeout":true,"script":"super"},{"text":"lo world\\nSecond line\\n"}]',
	'[{"text":"H","size":20,"script":"none"},{"text":"el","size":20,"script":"super"},{"text":"lo\\n"}]',
	'[{"text":{"$":"listStart","marker":"bullet"}},{"text":"Hello world"},{"text":{"$":"listNext"}},'
		+ '{"text":"Second line"},{"text":{"$":"listEnd"}}]',
	'[{"text":{"$":"listStart"}},{"text":"abc"},{"text":{"$":"listNext"}},{"text":"def"},'
		+ '{"text":{"$":"listEnd"}},{"text":"after\\n"}]',
	'[{"text":{"$":"listStart","marker":"bullet"}},{"text":"Hello world"},{"text":{"$":"listEnd"}},'
		+ '{"text":"Second line\\n"}]',
	'[{"text":"Hello "},{"text":"LINK","color":"#1565C0","underline":true,"url":"https://c.d"},'
		+ '{"text":"\\nSecond line\\n"}]',
	'[{"text":"Hello world\\n","align":"center"},{"text":"Second line\\n"}]',
	'[{"text":"\\n","align":"center"}]',
	'[{"text":"a","bold":true},{"text":"b\\n","size":20,"italic":true}]'
];

const tables = [
	'{"rows":[36,36],"columns":[100,100],"content":[[{"content":null},{"content":null}],[{"content":null},'
		+ '{"content":null}]],"vborders":null,"hborders":null,"bgcolor":null,"wrapping":null,"valign":null,'
		+ '"halign":null,"rotation":null}',
	'{"rows":[36,36],"columns":[100,100],"content":[[{"content":null,"bgcolor":"#00FF00"},{"content":'
		+ '[{"text":"abc\\n","bold":true}],"bgcolor":"#00FF00"}],[{"content":null},{"content":null}]],'
		+ '"vborders":[[0,3,0],[0,3,0]],"hborders":[[0,0],[3,3],[0,0]],"bgcolor":"#FF0000","wrapping":"clip",'
		+ '"valign":"middle","halign":"center","rotation":"rotateUp"}',
	'{"rows":[100,100],"columns":[200,200],"content":[[{"content":null,"bgcolor":"#123456","valign":"bottom"},'
		+ '{"content":null}],[{"content":null},{"content":null}]],"vborders":[[3,3,1],[1,1,1]],'
		+ '"hborders":[[3,1],[3,1],[1,1]],"bgcolor":null,"wrapping":null,"valign":null,"halign":null,'
		+ '"rotation":null}'
];

test('text contents round-trip unchanged', () => {
	for (const text of texts) {
		const doc = new RichText();
		doc.load(JSON.parse(text));
		assert.equal(JSON.stringify(doc.save()), text);
	}
});

test('table contents round-trip unchanged', () => {
	for (const content of tables) {
		const table = new Table();
		table.load(JSON.parse(content));
		assert.equal(JSON.stringify(table.save()), content);
	}
});
