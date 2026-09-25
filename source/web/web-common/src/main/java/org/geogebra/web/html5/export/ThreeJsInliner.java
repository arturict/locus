/*
 * Locus - free software under the EUPL 1.2, based on GeoGebra.
 * Copyright (c) 2026 Locus contributors
 *
 * This file is licensed under the EUPL 1.2.
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package org.geogebra.web.html5.export;

import java.util.function.Consumer;

import org.geogebra.common.geogebra3D.euclidian3D.printer3D.FormatColladaHTML;
import org.geogebra.common.util.debug.Log;
import org.geogebra.web.resources.StyleInjector;

import com.google.gwt.core.client.GWT;

import elemental2.dom.DomGlobal;
import elemental2.promise.Promise;

/**
 * Copies the three.js files that the Collada HTML export links to into the page, so
 * that the exported file works offline. The app serves the files next to its own
 * module directory, in <code>vendor/three/r92/</code>.
 */
public final class ThreeJsInliner {

	private ThreeJsInliner() {
		// utility class
	}

	/**
	 * @param html exported page
	 * @return whether the page links to the three.js files
	 */
	public static boolean needsInlining(String html) {
		return html.contains(FormatColladaHTML.THREE_JS_BASE);
	}

	/**
	 * Replaces each three.js script link by the script itself. If a file cannot be
	 * loaded, its link (to the Locus website) stays in the page.
	 * @param html exported page
	 * @param callback receives the page
	 */
	public static void inline(String html, Consumer<String> callback) {
		String base = StyleInjector.normalizeUrl(GWT.getModuleBaseURL()) + "../vendor/three/r92/";
		inline(html, base, 0, callback);
	}

	private static void inline(String html, String base, int index,
			Consumer<String> callback) {
		if (index >= FormatColladaHTML.THREE_JS_FILES.length) {
			callback.accept(html);
			return;
		}
		String file = FormatColladaHTML.THREE_JS_FILES[index];
		DomGlobal.fetch(base + file).then(response -> {
			if (!response.ok) {
				return Promise.<String>reject("HTTP " + response.status);
			}
			return response.text();
		}).then(script -> {
			inline(replaceScriptTag(html, file, script), base, index + 1, callback);
			return null;
		}, error -> {
			Log.warn("Could not load " + file + " for the export: " + error);
			inline(html, base, index + 1, callback);
			return null;
		});
	}

	private static String replaceScriptTag(String html, String file, String script) {
		String tag = FormatColladaHTML.getScriptTag(file);
		int start = html.indexOf(tag);
		if (start < 0) {
			return html;
		}
		// the three.js files contain no "</script", so they can stand inside a script element
		return html.substring(0, start) + "<script>\n" + script + "\n</script>\n"
				+ html.substring(start + tag.length());
	}
}
