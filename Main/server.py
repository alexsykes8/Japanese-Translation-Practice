import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure we can import modules from the Main package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from Main.Model.user import User
from Main.Model.sudachipi import sentence_breakdown

app = Flask(__name__)
CORS(app)  # Allow the extension to communicate with this server

# Initialize User with a default level (will be updated per request)
# We load the heavy dictionary data once at startup
print("Loading dictionaries... please wait.")
user = User("N5")
print("Server ready.")


@app.route('/hover_analyze', methods=['POST'])
def hover_analyze():
    data = request.json
    text_chunk = data.get('text', '')
    offset = data.get('offset', 0)
    user_level = data.get('level', 'N5')

    # 1. Update User Level dynamically for this request
    if user.user_level != user_level:
        user.user_level = user_level
        user.JLPT_lists.set_user_level(user_level)

    # 2. Find the specific word under the cursor using Sudachi
    # We reconstruct the token positions to find which one covers the offset
    sb = sentence_breakdown()
    sb.set_sentence(text_chunk)

    target_word = None
    current_pos = 0

    # Sudachi tokens
    tokens = sb.tokenizer_obj.tokenize(text_chunk, sb.mode)

    for token in tokens:
        token_len = len(token.surface())
        # Check if the cursor offset falls within this token
        if current_pos <= offset < current_pos + token_len:
            target_word = token.dictionary_form()
            break
        current_pos += token_len

    if not target_word:
        return jsonify({'found': False})

    # 3. Search for sentences using existing logic
    result = user.search_for_word(target_word)

    if not result:
        return jsonify({'found': False, 'word': target_word})

    definitions, sentences = result

    # Process sentences to include "difficult words" definitions
    processed_sentences = []
    for s_data in sentences:  # Limit to top 5 to save bandwidth
        sent_text = s_data[0].strip()
        diff_words = user.get_difficult_words_in_sentence(sent_text)

        # Filter out the target word from difficult words list
        filtered_diff_words = [
            {'word': w, 'level': l, 'def': d}
            for w, l, d in diff_words
            if w != target_word
        ]

        processed_sentences.append({
            'text': sent_text,
            'difficult_words': filtered_diff_words
        })

    return jsonify({
        'found': True,
        'word': target_word,
        'definitions': definitions,
        'sentences': processed_sentences
    })


if __name__ == '__main__':
    app.run(port=5000)