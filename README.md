# Japanese Reading Practice Tool

This project helps Japanese language learners practice reading by finding example sentences from real texts that are appropriate for their level.

## How It Works

The tool is composed of two main parts: a Python backend and a firefox extension frontend.

### Backend (`Main/`)

The backend is a Python application that does the heavy lifting of processing texts, managing vocabulary lists, and finding sentences.

#### Core Components:

*   **`book_management.py`**: Scans a directory of text files (books) and creates an inverted index. This allows for quick lookups of sentences containing a specific word.
*   **`JLPT.py` & `list_management.py`**: Manages the JLPT vocabulary lists (N1-N5) and user-specific known words. It calculates a "difficulty score" for sentences based on the user's declared JLPT level.
*   **`user.py`**: The main model class that ties everything together. It holds the user's level and provides the main `search_for_word` functionality.
*   **`wordsearch.py`**: Uses the Jisho.org API via `requests` to fetch word definitions.
*   **`sudachipi.py`**: Uses the `sudachipy` library for Japanese morphological analysis. This is used for breaking down sentences into individual words and finding their dictionary forms.

### Server (`Main/server.py`)

The backend is exposed via a Flask web server.

*   **Endpoint**: `POST /hover_analyze`
*   **Function**: This endpoint is designed to be called when a user hovers over a word in their editor.
    1.  It receives a chunk of text, the cursor's position (`offset`), and the user's JLPT level.
    2.  It uses `sudachipy` to identify the specific word under the cursor.
    3.  It then calls the `user.search_for_word()` method to find example sentences for that word.
    4.  It also fetches definitions from Jisho.org.
    5.  The results (definitions and sentences) are returned as a JSON response.

## How to Use

This project is designed to be run locally for development and debugging.

### Backend Setup

The Python backend server must be running for the extension to work.

**Prerequisites:**

*   Python 3.x
*   Your own Japanese texts (e.g., `.txt` files from Aozora Bunko) placed in the `book_files` directory. It is also setup to process the Japanese tsv sample sentence file that can be downloaded from https://tatoeba.org/en/downloads. I'd recommend using this if you can, but on my machine it took two days to process the whole file so keep that in mind. 

**Steps:**

1.  **Install Dependencies**:
    Open a terminal in the project root and install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server**:
    Execute the `server.py` script. This will start the Flask development server.

    ```bash
    python Main/server.py
    ```

    The server will be running on `http://127.0.0.1:5000`. It needs to be running in the background for the browser extension to use it.

### Firefox Extension Debugging

You can load the extension in Firefox for testing.

**Prerequisites:**

*   Firefox Browser
*   The backend server must be running.

**Steps:**

1.  Navigate to `about:debugging` in Firefox.
2.  Click on "This Firefox".
3.  Click "Load Temporary Add-on...".
4.  Navigate to the `Extension` directory in this project and select any file inside it (e.g., `manifest.json`).
5.  The extension is now installed temporarily. You can test it by browsing any webpage with Japanese text. Hovering over a word should trigger the analysis and display the results.
