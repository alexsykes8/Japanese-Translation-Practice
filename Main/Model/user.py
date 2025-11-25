import os
from Main.Model.book_management import BookManagement
from Main.Model.list_management import list_management
from Main.Model.wordsearch import WordSearch


class User:
    def __init__(self, level):
        self.user_level = level
        # Initialize the word lists and set the user level scoring
        self.JLPT_lists = list_management()
        self.JLPT_lists.set_user_level(self.user_level)
        self.JLPT_lists.initialise()

        # Initialize the dictionary of sentences from books
        self.sentence_dictionary = BookManagement()

    def search_for_word(self, word):
        # Initialize the search logic with the current user context
        word_searcher = WordSearch(self)
        # Perform the search
        return word_searcher.search(word)

    def get_difficult_words_in_sentence(self, sentence):
        """
        Returns a list of words in the sentence that are above the user's level.
        Each item is (word, level, meaning).
        """
        return self.JLPT_lists.get_difficult_words(sentence, self.user_level)

    def update_book_library(self):
        """
        Triggers the scanning of the book directory for new files.
        Returns the list of newly added books.
        """
        return self.sentence_dictionary.scan_for_new_books()