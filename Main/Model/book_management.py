import os
import re
import csv  # Added to handle TSV files properly

from Main.Model import sudachipi


class BookManagement:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.directory_path = os.path.join(self.script_dir, '../../book_files')
        self.book_dictionary_path = os.path.join(self.script_dir, '../../dictionary_files/book_dictionary.txt')
        self.dictionary = {}
        # Initialize by scanning for books immediately
        self.scan_for_new_books()

    def _get_dictionary(self):
        return self.dictionary

    def _save_dic_to_file(self):
        # Ensure directory exists before saving
        os.makedirs(os.path.dirname(self.book_dictionary_path), exist_ok=True)

        with open(self.book_dictionary_path, 'w', encoding='utf-8') as file:
            for word in self.dictionary:
                # Clean sentences to remove newlines that might break the format
                sentences = [s.replace('\n', '') for s in self.dictionary[word]]
                file.write(f"{word}|{str(sentences)}\n")

    def _load_dic_from_file(self):
        if not os.path.exists(self.book_dictionary_path):
            return

        with open(self.book_dictionary_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split("|")
                if len(parts) < 2:
                    continue
                # Basic cleaning of the string representation of list
                cleaned_part = parts[1].replace("[", "").replace("]", "").replace("'", "").replace('"', '')
                if not cleaned_part:
                    continue

                # Split by comma, but be careful with commas in sentences
                # This simple split might be fragile for complex sentences,
                # but fits the current logic.
                # A more robust way would be using ast.literal_eval if we saved as proper python lists
                sentence_array = [s.strip() for s in cleaned_part.split(", ")]
                self.dictionary[parts[0]] = sentence_array

    def _process_sentence(self, sentence):
        """
        Helper function to process a single sentence and add it to the dictionary
        """
        sentence = sentence.replace("\u3000", "").strip()
        if not sentence:
            return

        # uses sudachipi to break down the sentence into its component words
        sentence_composition = sudachipi.sentence_breakdown()
        sentence_composition.set_sentence(sentence)

        if sentence_composition.get_all_dict_forms():
            for word in sentence_composition.get_all_dict_forms():
                if word in self.dictionary:
                    # Avoid duplicate sentences for the same word
                    if sentence not in self.dictionary[word]:
                        self.dictionary[word].append(sentence)
                else:
                    self.dictionary[word] = [sentence]

    def _add_book(self, filename):
        """
        Adds a book (txt) or corpus (tsv) to the dictionary.
        """
        self._books_added_to_dic(filename)
        file_path = os.path.join(self.directory_path, filename)

        print(f"Processing {filename}...")

        if filename.endswith('.tsv'):
            # Handle TSV files (Tatoeba format)
            # Tatoeba format ID \t Language \t Sentence
            with open(file_path, 'r', encoding='utf-8') as file:
                # TSV reader
                reader = csv.reader(file, delimiter='\t')
                for row in reader:
                    if not row: continue


                    text = ""
                    if len(row) == 3 and row[1] == 'jpn':
                        text = row[2]
                    elif len(row) >= 2:
                        text = row[-1]

                    if text:
                        self._process_sentence(text)

        else:
            # Handle standard Text files
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    # Split by sentence delimiters
                    sentences = re.split(r'(?<=[。！？])|\n', line)
                    for sentence in sentences:
                        self._process_sentence(sentence)

    def _books_added_to_dic(self, book):
        """
        Once a book is added to the dictionary, make a note of it
        """
        file_path = os.path.join(self.script_dir, '../../dictionary_files/books_added.txt')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(f"{book}\n")

    def _check_if_book_added(self, book):
        """
        checks if a book has already been added to the dictionary
        """
        file_path = os.path.join(self.script_dir, '../../dictionary_files/books_added.txt')
        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if book in line.strip():
                    return True
        return False

    def scan_for_new_books(self):
        """
        Scans the book_files directory for .txt and .tsv files.
        """
        added_books = []

        # loads the existing dictionary
        self._load_dic_from_file()

        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

        for filename in os.listdir(self.directory_path):
            if filename.endswith(".txt") or filename.endswith(".tsv"):
                if not self._check_if_book_added(filename):
                    self._add_book(filename)
                    added_books.append(filename)

        if added_books:
            self._save_dic_to_file()

        return added_books

    def search_dic(self, word):
        return self.dictionary.get(word)


if __name__ == "__main__":
    book_management = BookManagement()
    book_management.scan_for_new_books()