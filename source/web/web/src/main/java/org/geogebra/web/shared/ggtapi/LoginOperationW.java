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

package org.geogebra.web.shared.ggtapi;

import org.geogebra.common.move.ggtapi.models.AuthenticationModel;
import org.geogebra.common.move.ggtapi.models.ClientInfo;
import org.geogebra.common.move.ggtapi.models.GeoGebraTubeUser;
import org.geogebra.common.move.ggtapi.models.Material;
import org.geogebra.common.move.ggtapi.models.Material.MaterialType;
import org.geogebra.common.move.ggtapi.models.MaterialRestAPI;
import org.geogebra.common.move.ggtapi.operations.BackendAPI;
import org.geogebra.common.move.ggtapi.operations.LogInOperation;
import org.geogebra.common.move.ggtapi.requests.MaterialCallbackI;

/**
 * Login operation of Locus. Locus has no accounts and no materials server, so
 * this operation never signs anybody in and never contacts a server: the user
 * is always logged out and may not log in. The shared code still asks for a
 * login operation, which is why this class exists at all.
 */
public final class LoginOperationW extends LogInOperation {

	private static final String NO_BACKEND = "Locus has no online accounts or materials server";

	private final BackendAPI backend = new OfflineBackendAPI();

	/**
	 * Creates a login operation that is permanently logged out.
	 */
	public LoginOperationW() {
		setModel(new OfflineAuthenticationModel());
		getModel().preventLoginPrompt();
	}

	@Override
	public BackendAPI getGeoGebraTubeAPI() {
		return backend;
	}

	/**
	 * There is no materials server; callers must not reach this method.
	 * @throws UnsupportedOperationException always
	 */
	@Override
	public MaterialRestAPI getResourcesAPI() {
		throw new UnsupportedOperationException(NO_BACKEND);
	}

	@Override
	public String getLoginURL(String languageTag) {
		return "";
	}

	@Override
	protected String getURLLoginCaller() {
		return "";
	}

	@Override
	protected String getURLClientInfo() {
		return "";
	}

	@Override
	public void performTokenLogin(String token, boolean automatic) {
		stayLoggedOut();
	}

	@Override
	public void doPerformTokenLogin(GeoGebraTubeUser user, boolean automatic) {
		stayLoggedOut();
	}

	@Override
	public void passiveLogin() {
		stayLoggedOut();
	}

	@Override
	public boolean canUserShare() {
		return false;
	}

	@Override
	public void setUserLanguage(String lang) {
		// no account to store the language in
	}

	/** Authentication model without tokens: nobody is ever logged in. */
	private static final class OfflineAuthenticationModel extends AuthenticationModel {

		@Override
		public void storeLoginToken(String token) {
			// no accounts
		}

		@Override
		public String getLoginToken() {
			return null;
		}

		@Override
		public void clearLoginToken() {
			// no accounts
		}
	}

	/** Backend that rejects every server request without touching the network. */
	private static final class OfflineBackendAPI implements BackendAPI {

		@Override
		public String getLoginUrl() {
			return "";
		}

		@Override
		public boolean parseUserDataFromResponse(GeoGebraTubeUser user, String loadLastUser) {
			return false;
		}

		@Override
		public void authorizeUser(GeoGebraTubeUser user, LogInOperation logInOperation,
				boolean automatic) {
			logInOperation.stayLoggedOut();
		}

		@Override
		public void setClient(ClientInfo clientInfo) {
			// nothing to identify towards
		}

		@Override
		public boolean isCheckDone() {
			return true;
		}

		@Override
		public void setUserLanguage(String lang, String token) {
			// no accounts
		}

		@Override
		public String getUrl() {
			return "";
		}

		@Override
		public void logout(String token) {
			// no accounts
		}

		@Override
		public void uploadLocalMaterial(Material mat, MaterialCallbackI cb) {
			cb.onError(new UnsupportedOperationException(NO_BACKEND));
		}

		@Override
		public void uploadMaterial(String tubeID, String visibility, String filename,
				String base64, MaterialCallbackI cb, MaterialType type, boolean isMultiuser) {
			cb.onError(new UnsupportedOperationException(NO_BACKEND));
		}

		@Override
		public boolean canUserShare(boolean student) {
			return false;
		}

		@Override
		public boolean anonymousOpen() {
			return true;
		}
	}
}
