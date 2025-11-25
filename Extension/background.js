browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'analyze_text') {
        console.log("Background: Sending request to Python server for:", message.text);

        fetch('http://127.0.0.1:5000/hover_analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: message.text,
                offset: message.offset,
                level: message.level
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Background: Received data:", data);
            sendResponse(data);
        })
        .catch(error => {
            console.error("Background: Fetch error:", error);
            sendResponse({ found: false, error: error.message });
        });

        return true; // Keeps the message channel open for the async response
    }
});