let popup = null;
let currentSentenceIndex = 0;
let currentData = null;
let debounceTimer = null;
let hideTimer = null;
let lastNavTime = 0;
let visibleLimit = 5;

function createPopup() {
    const oldPopup = document.getElementById('jlpt-sentence-popup');
    if (oldPopup) {
        oldPopup.remove();
    }

    popup = document.createElement('div');
    popup.id = 'jlpt-sentence-popup';
    popup.style.display = 'none';
    document.body.appendChild(popup);

    popup.addEventListener('mouseenter', () => {
        if (hideTimer) clearTimeout(hideTimer);
    });

    popup.addEventListener('mouseleave', () => hidePopup());
    console.log("JLPT Extension: Popup created.");
}

function updatePopupContent(data) {
    if (!data.sentences || data.sentences.length === 0) {
        popup.innerHTML = `<div class="header"><strong>${data.word}</strong>: No sentences found.</div>`;
        return;
    }

    if (currentSentenceIndex >= visibleLimit) {
         popup.innerHTML = `
            <div class="header">
                <span class="word">${data.word}</span>
                <div class="controls">
                    <span class="nav-btn" id="prev-btn">◀</span>
                    <span class="counter">${currentSentenceIndex + 1}/${data.sentences.length}</span>
                    <span class="nav-btn" style="color:gray; cursor:default;">▶</span> 
                </div>
            </div>
            <div style="text-align:center; padding: 20px;">
                <button id="load-more-btn" style="
                    padding: 8px 16px; 
                    background: #3498db; 
                    color: white; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer;
                    font-size: 14px;">
                    Load More Sentences
                </button>
                <p style="font-size:12px; color:#bdc3c7; margin-top:5px;">(Sentences ${visibleLimit + 1}-${data.sentences.length})</p>
            </div>
        `;

        document.getElementById('prev-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            navigateSentence(-1);
        });

        document.getElementById('load-more-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            visibleLimit = data.sentences.length;
            updatePopupContent(currentData);
        });
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
    } else if (currentSentenceIndex >= 5) {
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

    document.getElementById('prev-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        navigateSentence(-1);
    });
    document.getElementById('next-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        navigateSentence(1);
    });

    const revealBtn = document.getElementById('reveal-def-btn');
    const defContent = popup.querySelector('.def-content');

    revealBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        revealBtn.style.display = 'none';
        defContent.style.display = 'block';
    });
}

function navigateSentence(direction) {
    if (!currentData || !currentData.sentences) return;

    const newIndex = currentSentenceIndex + direction;

    let maxNav = Math.min(currentData.sentences.length - 1, visibleLimit);

    if (visibleLimit < currentData.sentences.length) {
        maxNav = visibleLimit;
    }

    if (newIndex >= 0 && newIndex <= maxNav) {
        currentSentenceIndex = newIndex;
        lastNavTime = Date.now();
        updatePopupContent(currentData);
    }
}

function hidePopup() {
    if (Date.now() - lastNavTime < 500) return;

    hideTimer = setTimeout(() => {
        if (Date.now() - lastNavTime < 500) return;
        if (popup) popup.style.display = 'none';
    }, 300);
}

document.addEventListener('keydown', (e) => {
    if (popup && popup.style.display !== 'none') {
        if (e.key === 'ArrowLeft') {
            navigateSentence(-1);
        } else if (e.key === 'ArrowRight') {
            navigateSentence(1);
        }
    }
});

async function handleHover(e) {
    if (!popup) createPopup();

    if (e.target.id === 'jlpt-sentence-popup' || e.target.closest('#jlpt-sentence-popup')) {
        if (hideTimer) clearTimeout(hideTimer);
        return;
    }

    if (!document.caretPositionFromPoint) {
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

    const storage = await browser.storage.local.get(['jlptLevel']);
    const level = storage.jlptLevel || 'N5';

    try {
        const response = await browser.runtime.sendMessage({
            type: 'analyze_text',
            text: text,
            offset: rangePos.offset,
            level: level
        });

        if (response && response.found) {
            if (currentData && currentData.word === response.word && popup.style.display === 'block') {
                return;
            }

            console.log("JLPT Extension: Word found:", response.word);
            currentData = response;
            currentSentenceIndex = 0;
            visibleLimit = 5; // Reset limit for new word

            updatePopupContent(response);

            popup.style.display = 'block';
            popup.style.left = (e.pageX + 15) + 'px';
            popup.style.top = (e.pageY + 15) + 'px';
        } else {
            hidePopup();
        }
    } catch (err) {
    }
}

document.addEventListener('mousemove', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => handleHover(e), 200);
});

createPopup();