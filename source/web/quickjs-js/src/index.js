/*
 * Locus JavaScript sandbox: QuickJS compiled to WebAssembly, behind the global
 * `window.QJS.getQuickJS()` that org.geogebra.web.html5.main.scripting.QuickJS calls.
 * Copyright (c) 2026 Locus contributors, EUPL 1.2.
 * quickjs-emscripten (c) Jake Teton-Landis, MIT; QuickJS (c) Fabrice Bellard and
 * Charlie Gordon, MIT.
 */
import variant from '@jitl/quickjs-singlefile-browser-release-sync';
import { newQuickJSWASMModuleFromVariant } from 'quickjs-emscripten-core';

/** A script (with everything it calls) may run this long before it is interrupted. */
export const TIME_LIMIT_MS = 10000;

/**
 * Interrupts scripts that run too long, e.g. an endless loop in a button script,
 * which would otherwise freeze the page. Nested calls share the outer deadline.
 */
function guard(context) {
	let deadline = Infinity;
	context.runtime.setInterruptHandler(() => Date.now() > deadline);
	for (const name of ['evalCode', 'callFunction']) {
		const original = context[name].bind(context);
		context[name] = (...args) => {
			const outer = deadline === Infinity;
			if (outer) {
				deadline = Date.now() + TIME_LIMIT_MS;
			}
			try {
				return original(...args);
			} finally {
				if (outer) {
					deadline = Infinity;
				}
			}
		};
	}
	return context;
}

let modulePromise = null;

export function getQuickJS() {
	if (!modulePromise) {
		modulePromise = newQuickJSWASMModuleFromVariant(variant).then((module) => ({
			module,
			newContext(options) {
				return guard(module.newContext(options));
			}
		}));
	}
	return modulePromise;
}

const api = { getQuickJS };
if (typeof window !== 'undefined') {
	window.QJS = api;
}
export default api;
