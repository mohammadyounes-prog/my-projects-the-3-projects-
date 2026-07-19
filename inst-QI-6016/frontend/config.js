(async function() {
    // Default to current host - this is the most reliable fallback
    const currentHost = window.location.origin;
    
    // Check if we are running locally
    const isLocal = currentHost.includes('localhost') || currentHost.includes('127.0.0.1');

    if (!window.BACKEND_BASE_URL) {
        window.BACKEND_BASE_URL = currentHost;
    }

    try {
        const response = await fetch(`${currentHost}/config`);
        if (response.ok) {
            const config = await response.json();
            if (config.BACKEND_BASE_URL) {
                // If we are on localhost, don't let the external domain override it
                if (isLocal && (config.BACKEND_BASE_URL.includes('questai.examforall.com'))) {
                    console.log("Local testing detected, staying on localhost instead of switching to", config.BACKEND_BASE_URL);
                    window.BACKEND_BASE_URL = currentHost;
                } else {
                    window.BACKEND_BASE_URL = config.BACKEND_BASE_URL;
                }
                
                console.log("Config loaded dynamic backend URL:", window.BACKEND_BASE_URL);
                // Trigger an event so other scripts know the config is ready
                window.dispatchEvent(new CustomEvent('configLoaded', { detail: window.BACKEND_BASE_URL }));
            }
        }
    } catch (e) {
        console.warn("Could not fetch dynamic config, using default:", window.BACKEND_BASE_URL);
    }
})();
