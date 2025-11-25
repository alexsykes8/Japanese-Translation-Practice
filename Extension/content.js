let popup = null;
let currentSentenceIndex = 0;
let currentData = null;
let debounceTimer = null;

// 1. Create the popup element
function createPopup() {
    if (document.getElementById('jlpt-sentence-popup')) return; // Avoid duplicates
    popup = document.createElement('div');
    popup.id = 'jlpt-sentence-popup';
    popup.style.display = 'none';
    document.body.appendChild(popup);

    popup.addEventListener('mouseenter', () => clearTimeout(hideTimer));
    popup.addEventListener('mouseleave', () => hidePopup());
    console.log("JLPT Extension: Popup created");
}

// 2. Update HTML content
function updatePopupContent(data) {
    if (!data.sentences || data.sentences.length === 0) {
        popup.innerHTML = `<div class="header"><strong>${data.word}</strong>: No sentences found.</div>`;
        return;
    }

    const sentence = data.sentences[currentSentenceIndex];
    let difficultWordsHtml = '';

    if (sentence.difficult_words && sentence.difficult_words.length > 0) {
        difficultWordsHtml = `<div class="diff-words">
            <strong>New Words:</strong><br>
            ${sentence.difficult_words.map(w => 
                `<span class="dw-item">${w.word} (${w.level}): ${w.def}</span>`
            ).join('<br>')}
        </div>`;
    }

    const defs = data.definitions ? data.definitions.slice(0, 2).join("; ") : "No definition";

    popup.innerHTML = `
        <div class="header">
            <span class="word">${data.word}</span> 
            
            <div class="controls">
                <span class="nav-btn" id="prev-btn">◀</span>
                <span class="counter">${currentSentenceIndex + 1}/${data.sentences.length}</span>
                <span class="nav-btn" id="next-btn">▶</span>
            </div>
        </div>
        <div class="sentence">${sentence.text}</div>
        
        <div class="def-container">
            <div class="reveal-btn" id="reveal-def-btn">Show Definition</div>
            <div class="def-content" style="display:none;">${defs}</div>
        </div>

        ${difficultWordsHtml}
    `;

    // Re-attach listeners for navigation
    document.getElementById('prev-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentSentenceIndex > 0) {
            currentSentenceIndex--;
            updatePopupContent(data);
        }
    });
    document.getElementById('next-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentSentenceIndex < data.sentences.length - 1) {
            currentSentenceIndex++;
            updatePopupContent(data);
        }
    });

    // Attach listener for reveal button
    const revealBtn = document.getElementById('reveal-def-btn');
    const defContent = popup.querySelector('.def-content');

    revealBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        revealBtn.style.display = 'none';
        defContent.style.display = 'block';
    });
}

let hideTimer = null;

function hidePopup() {
    hideTimer = setTimeout(() => {
        if (popup) popup.style.display = 'none';
    }, 300);
}

async function handleHover(e) {
    if (!popup) createPopup();
    if (e.target.id === 'jlpt-sentence-popup' || e.target.closest('#jlpt-sentence-popup')) return;

    // Firefox check
    if (!document.caretPositionFromPoint) {
        console.log("JLPT Extension: caretPositionFromPoint not supported in this context.");
        return;
    }

    const rangePos = document.caretPositionFromPoint(e.clientX, e.clientY);
    if (!rangePos || !rangePos.offsetNode) return;

    const textNode = rangePos.offsetNode;
    if (textNode.nodeType !== Node.TEXT_NODE) return;

    const text = textNode.textContent;
    const hasJapanese = /[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]/.test(text);

    if (!hasJapanese) {
        hidePopup();
        return;
    }

    console.log("JLPT Extension: Japanese detected, querying server...");

    // Get user level
    const storage = await browser.storage.local.get(['jlptLevel']);
    const level = storage.jlptLevel || 'N5';

    // SEND MESSAGE TO BACKGROUND SCRIPT
    try {
        const response = await browser.runtime.sendMessage({
            type: 'analyze_text',
            text: text,
            offset: rangePos.offset,
            level: level
        });

        if (response && response.found) {
            console.log("JLPT Extension: Word found:", response.word);
            currentData = response;
            currentSentenceIndex = 0;
            updatePopupContent(response);

            popup.style.display = 'block';
            popup.style.left = (e.pageX + 15) + 'px';
            popup.style.top = (e.pageY + 15) + 'px';
        } else {
            console.log("JLPT Extension: No word found or server error.");
            hidePopup();
        }
    } catch (err) {
        console.error("JLPT Extension: Messaging error:", err);
    }
}

document.addEventListener('mousemove', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => handleHover(e), 200);
});

// Init
createPopup();