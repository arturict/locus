// Runs the committed bundle and drives it the way Sandbox/QuickJS.java/SandboxConverter do.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const bundle = readFileSync(new URL(
	'../../web-common/src/main/resources/org/geogebra/web/html5/main/scripting/locus-quickjs.js',
	import.meta.url), 'utf8');

async function newContext() {
	const sandbox = { console, setTimeout, clearTimeout, TextDecoder, TextEncoder, WebAssembly, URL,
		atob, btoa, Date, Promise };
	sandbox.window = sandbox;
	sandbox.self = sandbox;
	sandbox.globalThis = sandbox;
	vm.createContext(sandbox);
	vm.runInContext(bundle, sandbox);
	assert.equal(typeof sandbox.QJS.getQuickJS, 'function');
	const factory = await sandbox.QJS.getQuickJS();
	return factory.newContext();
}

test('evalCode, handles and dump', async () => {
	const ctx = await newContext();
	assert.equal(ctx.unwrapResult(ctx.evalCode('1 + 2')).constructor.name.length > 0, true);
	assert.equal(ctx.dump(ctx.unwrapResult(ctx.evalCode('({a: [1, "x"]})'))).a[1], 'x');
	assert.equal(ctx.typeof(ctx.getProp(ctx.global, 'nothing')), 'undefined');
	for (const handle of [ctx.true, ctx.false, ctx.null, ctx.undefined]) {
		assert.ok(handle);
	}
	assert.throws(() => ctx.unwrapResult(ctx.evalCode('throw new Error("boom")')), /boom/);
});

test('host functions like ggbApplet.setValue and listeners called back', async () => {
	const ctx = await newContext();
	const calls = [];
	const ggbApplet = ctx.newObject();
	ctx.setProp(ctx.global, 'window', ctx.global);
	ctx.setProp(ctx.global, 'ggbApplet', ggbApplet);
	// like QuickJS.addWrappedMethod: arguments arrive as handles, the result is a handle
	ctx.setProp(ggbApplet, 'setValue', ctx.newFunction('', (...args) => {
		calls.push(args.map((a) => ctx.dump(a)));
		return ctx.newNumber(1);
	}));
	const listeners = [];
	ctx.setProp(ggbApplet, 'registerUpdateListener', ctx.newFunction('', (fn) => {
		// SandboxConverter keeps the function reachable through a global
		ctx.setProp(ctx.global, 'ggbPersistentFn' + listeners.length, fn);
		listeners.push(fn);
		return ctx.undefined;
	}));
	ctx.unwrapResult(ctx.evalCode('ggbApplet.setValue("a", 3)'));
	assert.equal(JSON.stringify(calls), '[["a",3]]');
	ctx.unwrapResult(ctx.evalCode('var seen = []; ggbApplet.registerUpdateListener(function(n) { seen.push(n); })'));
	const ref = ctx.getProp(ctx.global, 'ggbPersistentFn0');
	// Sandbox.callRef: callFunction.apply(context, [fn, this, ...args])
	ctx.unwrapResult(ctx.callFunction.apply(ctx, [ref, ctx.global, ctx.newString('A')]));
	assert.equal(JSON.stringify(ctx.dump(ctx.unwrapResult(ctx.evalCode('seen')))), '["A"]');
});

test('endless loops are interrupted', async () => {
	const ctx = await newContext();
	const started = Date.now();
	assert.throws(() => ctx.unwrapResult(ctx.evalCode('while (true) {}')), /interrupted/);
	assert.ok(Date.now() - started < 15000);
	// the context still works afterwards
	assert.equal(ctx.dump(ctx.unwrapResult(ctx.evalCode('6 * 7'))), 42);
});
