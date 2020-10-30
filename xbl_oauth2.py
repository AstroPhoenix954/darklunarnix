"""
Sign in to Xbox Live with OAUTH2
1. Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
2. Register new app ("+ New registration")
2.1. Enter a name for your app
2.2. Set "Supported account types" to "Personal Microsoft accounts only"
2.3. Click register
2.4. Choose "Redirect URIs" -> "Add a Redirect URI"
2.5. Click "Add a platform" -> "Mobile and desktop applications"
2.6. Enter custom redirect URI (Use something like "https://localhost/oauth_success" for testing)
3. From the overview of your app page, copy "Application (client) ID" to CLIENT_ID below in the py code
4. Replace REDIRECT_URI in the py code with the actual URI set in Azure app registration
5. Test and profit ;)
"""

import requests

CLIENT_ID = "772cccd8-54f6-4fce-858b-645fbabf1bed"
REDIRECT_URI = "https://localhost/oauth_success"


def main():
    """
    Authorize account for app and receive authorization code
    """

    url = "https://login.live.com/oauth20_authorize.srf"
    query_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "Xboxlive.signin Xboxlive.offline_access",
        "redirect_uri": REDIRECT_URI,
    }

    destination_url = requests.Request("GET", url, params=query_params).prepare().url

    print("Authorize using following URL: " + destination_url)

    authorization_code = input("Enter Code:")

    """
    Authenticate account via authorization code and receive access/refresh token
    """
    base_url = "https://login.live.com/oauth20_token.srf"
    params = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "scope": "Xboxlive.signin Xboxlive.offline_access",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
    }

    resp = requests.post(base_url, data=params)
    if resp.status_code != 200:
        print("Failed to get access token")
        return

    access_token = resp.json()["access_token"]

    """
    Authenticate via access token and receive user token
    """
    url = "https://user.auth.xboxlive.com/user/authenticate"
    headers = {"x-xbl-contract-version": "1"}
    data = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d=" + access_token,
        },
    }

    resp = requests.post(url, json=data, headers=headers)

    if resp.status_code != 200:
        print("Invalid response")
        return

    user_token = resp.json()["Token"]

    """
    Authorize via user token and receive final X token
    """
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    headers = {"x-xbl-contract-version": "1"}
    data = {
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL",
        },
    }

    resp = requests.post(url, json=data, headers=headers)

    if resp.status_code != 200:
        print("Invalid response")
        return

    print(":::XTOKEN:::")
    print(resp.json())


if __name__ == "__main__":
    main()
