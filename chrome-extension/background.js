chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "login") {
        let authUrl = `https://accounts.google.com/o/oauth2/auth?` +
            `client_id=780760452503-4m74p09gdvjl206utpb0q8mbe5j4n5sn.apps.googleusercontent.com&` +
            `response_type=token&` +  // 🟢 Make sure response_type is included
            `redirect_uri=https://pomlmbalkapmaaojofkpoaomiaboklkc.chromiumapp.org/&` +  // 🟢 Must match in Google Cloud Console
            `scope=openid%20profile%20email&` +
            `prompt=consent`;

        chrome.identity.launchWebAuthFlow(
            { url: authUrl, interactive: true },
            function (redirectUrl) {
                if (chrome.runtime.lastError) {
                    sendResponse({ error: chrome.runtime.lastError.message });
                    return;
                }

                let accessTokenMatch = redirectUrl.match(/access_token=([^&]+)/);
                if (!accessTokenMatch) {
                    sendResponse({ error: "No access token found." });
                    return;
                }

                let accessToken = accessTokenMatch[1];

                fetch("https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=" + accessToken)
                    .then(response => response.json())
                    .then(user => sendResponse({ user }))
                    .catch(error => sendResponse({ error: error.message }));
            }
        );

        return true; // Required for async sendResponse
    }
});


