document.addEventListener('DOMContentLoaded', () => {
    const levelSelect = document.getElementById('level');
    const statusDiv = document.getElementById('status');

    // Load saved level
    browser.storage.local.get(['jlptLevel']).then((result) => {
        if (result.jlptLevel) {
            levelSelect.value = result.jlptLevel;
        }
    });

    // Save level
    document.getElementById('save').addEventListener('click', () => {
        const level = levelSelect.value;
        browser.storage.local.set({ jlptLevel: level });

        statusDiv.style.display = 'block';
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 1500);
    });
});