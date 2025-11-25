import sys
import os

# Ensure we can import modules from the Main package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from Main.Model.user import User


def main():
    print("--- Japanese Sentence Search Tool ---")

    # 1. Get User Level
    while True:
        level = input("Please enter your JLPT level (N5, N4, N3, N2, N1): ").strip().upper()
        if level in ["N5", "N4", "N3", "N2", "N1"]:
            break
        print("Invalid level. Please enter N1, N2, N3, N4, or N5.")

    print(f"\nInitializing dictionaries for level {level}...")
    print("This may take a moment while we load the book data...")

    try:
        user = User(level)
        print("Initialization complete!\n")
    except Exception as e:
        print(f"Error initializing application: {e}")
        return

    # 2. Main Search Loop
    while True:
        search_word = input("Enter a word to search (or 'q' to quit): ").strip()

        if search_word.lower() == 't':
            print("Goodbye!")
            break

        if not search_word:
            continue

        try:
            # Search returns a tuple: (definitions_list, sorted_sentences_list)
            result = user.search_for_word(search_word)

            if result:
                definitions, sentences = result

                # Display Definitions for the search word
                print(f"\n--- Definitions for '{search_word}' ---")
                if definitions:
                    for definition in definitions:
                        print(f"- {definition}")
                else:
                    print("No definitions found.")

                # Display Sentences
                print(f"\n--- Found {len(sentences)} Sentences ---")

                for i, sentence_data in enumerate(sentences):
                    # sentence_data structure is [sentence_string, scores, non_jlpt_words, count, etc.]
                    sentence_text = sentence_data[0].strip()
                    print(f"\nSentence #{i + 1}:")
                    print(f"  {sentence_text}")

                    # --- NEW: Display definitions for difficult words ---
                    difficult_words = user.get_difficult_words_in_sentence(sentence_text)
                    if difficult_words:
                        print("  [Words above your level]:")
                        for word, w_level, w_def in difficult_words:
                            print(f"    - {word} ({w_level}): {w_def}")
                    # ----------------------------------------------------

                    # Simple pagination
                    if i < len(sentences) - 1:
                        cont = input("\n[Enter] for next sentence, [n] for new search: ").lower()
                        if cont == 'n':
                            break
                print("-" * 30 + "\n")

        except Exception as e:
            print(f"An error occurred during search: {e}")


if __name__ == "__main__":
    main()