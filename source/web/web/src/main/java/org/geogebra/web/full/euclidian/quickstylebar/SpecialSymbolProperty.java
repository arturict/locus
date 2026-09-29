/*
 * GeoGebra - Dynamic Mathematics for Everyone
 * Copyright (c) GeoGebra GmbH, Altenbergerstr. 69, 4040 Linz, Austria
 * https://www.geogebra.org
 *
 * This file is licensed by GeoGebra GmbH under the EUPL 1.2 licence and
 * may be used under the EUPL 1.2 in compatible projects (see Article 5
 * and the Appendix of EUPL 1.2 for details).
 * You may obtain a copy of the licence at:
 * https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 *
 * Note: The overall GeoGebra software package is free to use for
 * non-commercial purposes only.
 * See https://www.geogebra.org/license for full licensing details
 */

package org.geogebra.web.full.euclidian.quickstylebar;

import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Stream;

import org.geogebra.common.euclidian.draw.HasTextFormat;
import org.geogebra.common.kernel.geos.GeoElement;
import org.geogebra.common.kernel.geos.HasTextFormatter;
import org.geogebra.common.main.Localization;
import org.geogebra.common.properties.PropertySupplier;
import org.geogebra.common.properties.impl.AbstractProperty;
import org.geogebra.common.properties.impl.objects.FontProperty;
import org.geogebra.common.properties.impl.objects.delegate.FontStyleUtil;

/**
 * Inserting symbols into text is implemented as a write-only property:
 * {@link #insertSymbol(SpecialSymbol)} changes the state of the text, but there is no meaningful
 * getter for this property.
 *
 * <p>These special symbols are only available in special fonts used in German primary
 * schools; group names and symbol descriptions are translation keys
 * ({@code SpecialSymbols.*} in menu.properties).</p>
 */
public final class SpecialSymbolProperty extends AbstractProperty {
	private final GeoElement geo;
	private final String groupKey;
	private final List<SpecialSymbol> values;

	private SpecialSymbolProperty(
			Localization loc, String groupKey, Predicate<SpecialSymbol> filter, GeoElement geo) {
		super(loc, "Sonderzeichen");
		this.geo = geo;
		this.groupKey = groupKey;
		values = Stream.of(SpecialSymbol.values()).filter(filter).toList();
	}

	/**
	 * @return font family to be used for rendering this property
	 */
	public FontProperty.FontFamily getFontFamily() {
		HasTextFormat formatter = ((HasTextFormatter) geo).getFormatter();
		String fontFamily = "";
		if (formatter != null) {
			fontFamily = formatter.getFormat("font", "");
		}
		return FontProperty.FontFamily.getByCssName(
				fontFamily, FontProperty.FontFamily.BY_DS_SCHREIBEN_1_2_BLUE_FARBBAND);
	}

	/**
	 * @return translated name of this group of symbols
	 */
	public String getGroupName() {
		return getLocalization().getMenu(groupKey);
	}

	/**
	 * @param symbol special symbol
	 * @return translated description of the symbol, shown under it
	 */
	public String getDescription(SpecialSymbol symbol) {
		return getLocalization().getMenu(symbol.descriptionKey);
	}

	/**
	 * Special symbols, each represented by Unicode codepoint.
	 */
	public enum SpecialSymbol {
		BASIC1("[", "HouseLeft"),
		BASIC2("]", "HouseRight"),
		BASIC3("|", "LineEnd"),
		BASIC4("\ue100", "NarrowLines"),
		BASIC5("\ue000", "Space"),

		DIFF1("\ue028", "Easy"),
		DIFF2("\ue029", "Medium"),
		DIFF3("\ue030", "Hard"),

		PUZZLE1("\ue001", "Part1"),
		PUZZLE2("\ue002", "Part2"),
		PUZZLE3("\ue003", "Part3"),
		PUZZLE4("\ue004", "Part4"),

		WURM("\ue031", "Head");
		public final String symbol;
		/** translation key of the description */
		public final String descriptionKey;

		SpecialSymbol(String symbol, String description) {
			this.symbol = symbol;
			this.descriptionKey = "SpecialSymbols." + description;
		}
	}

	/**
	 * Properties for given objects.
	 * @param loc localization
	 * @param activeGeoList geos
	 * @return properties
	 */
	public static PropertySupplier[] forGeos(Localization loc, List<GeoElement> activeGeoList) {
		GeoElement geo = activeGeoList.size() == 1 ? activeGeoList.get(0) : null;
		if (!FontStyleUtil.isInlineWithSymbols(geo)) {
			return new PropertySupplier[0];
		}
		SpecialSymbolProperty diffs = new SpecialSymbolProperty(
				loc, "SpecialSymbols.Differentiation", byPrefix("DIFF"), geo);
		boolean limitBasicSymbols = FontStyleUtil.isFontStyleApplicableWithLimitation(geo);
		SpecialSymbolProperty basics = getBasicSpecialSymbolProperty(loc, geo, limitBasicSymbols);

		if (limitBasicSymbols) {
			return new PropertySupplier[] {basics, diffs};
		} else if (FontStyleUtil.isFontStyleApplicable(geo)) {
			SpecialSymbolProperty puzzles = new SpecialSymbolProperty(
					loc, "SpecialSymbols.Puzzle", byPrefix("PUZZLE"), geo);
			return new PropertySupplier[] {basics, diffs, puzzles};
		} else if (FontStyleUtil.isInlineWithWurm(geo)) {
			SpecialSymbolProperty wurm = new SpecialSymbolProperty(
					loc, "SpecialSymbols.Worm", byPrefix("WURM"), geo);
			return new PropertySupplier[] {wurm, diffs};
		} else {
			return new PropertySupplier[] {diffs};
		}
	}

	private static Predicate<SpecialSymbol> byPrefix(String prefix) {
		return specialSymbol -> specialSymbol.name().startsWith(prefix);
	}

	/**
	 * @param localization Localization
	 * @param geo GeoElement
	 * @param limitBasicSymbols Whether the basic symbols are limited to the ones listed below.
	 * @return The property for the basic symbols used for the 'ByDS' fonts.
	 * @implNote 'ByDS Schreiben 3' and 'ByDS Schreiben 4' must contain only the basic symbols
	 * {@link SpecialSymbol#BASIC3}, {@link SpecialSymbol#BASIC4}, and {@link SpecialSymbol#BASIC5}
	 */
	private static SpecialSymbolProperty getBasicSpecialSymbolProperty(
			Localization localization, GeoElement geo, boolean limitBasicSymbols) {
		if (limitBasicSymbols) {
			return new SpecialSymbolProperty(
					localization,
					"SpecialSymbols.Basic",
					List.of(SpecialSymbol.BASIC3, SpecialSymbol.BASIC4, SpecialSymbol.BASIC5)::contains,
					geo);
		}
		return new SpecialSymbolProperty(localization, "SpecialSymbols.Basic", byPrefix("BASIC"), geo);
	}

	/**
	 * @param value symbol to insert
	 */
	public void insertSymbol(SpecialSymbol value) {
		HasTextFormat formatter = ((HasTextFormatter) geo).getFormatter();
		if (formatter != null) {
			formatter.setSelectionText(value.symbol);
		}
	}

	public List<SpecialSymbol> getValues() {
		return values;
	}
}
