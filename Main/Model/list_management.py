import time
import requests
import json
import os
from Main.Model.JLPT_N1 import JLPT_N1
from Main.Model.JLPT_N2 import JLPT_N2
from Main.Model.JLPT_N3 import JLPT_N3
from Main.Model.JLPT_N4 import JLPT_N4
from Main.Model.JLPT_N5 import JLPT_N5
from Main.Model.sudachipi import sentence_breakdown

"""
    This class is used to manage the lists of words for each JLPT level. It is used to search for words in the lists and to calculate the JLPT score of a sentence.
"""


class list_management:
    def __init__(self):
        self.N5 = None
        self.N4 = None
        self.N3 = None
        self.N2 = None
        self.N1 = None
        self.user_level = None
        self.sentence_breakdown = sentence_breakdown()
        self.score_distribution = None
        self.levels = ["N5", "N4", "N3", "N2", "N1"]

        # Define the path for the persistent cache file
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_file_path = os.path.join(self.script_dir, '../../dictionary_files/jisho_cache.json')

        # Initialize cache from file
        self.jisho_cache = {}
        self.load_cache()

    def set_user_level(self, level):
        self.user_level = level
        if self.user_level == "N5":
            self.score_distribution = [5, -1, -2, -3, -4]
        elif self.user_level == "N4":
            self.score_distribution = [4, 5, -1, -2, -3]
        elif self.user_level == "N3":
            self.score_distribution = [3, 4, 5, -1, -2]
        elif self.user_level == "N2":
            self.score_distribution = [2, 3, 4, 5, -1]
        elif self.user_level == "N1":
            self.score_distribution = [1, 2, 3, 4, 5]

    def initialise(self):
        self.N5 = JLPT_N5()
        self.N5.create_dic()

        self.N4 = JLPT_N4()
        self.N4.create_dic()

        self.N3 = JLPT_N3()
        self.N3.create_dic()

        self.N2 = JLPT_N2()
        self.N2.create_dic()

        self.N1 = JLPT_N1()
        self.N1.create_dic()
        return

    def load_cache(self):
        """Loads the cache from the JSON file if it exists."""
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                    self.jisho_cache = json.load(f)
                print(f"Loaded {len(self.jisho_cache)} words from Jisho cache.")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.jisho_cache = {}
        else:
            print("No existing cache found. Creating a new one.")
            self.jisho_cache = {}

    def save_cache(self):
        """Saves the current cache to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
            with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.jisho_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def search_lists(self, word):
        """
        This function searches for a word in the JLPT lists.
        :param word: the word to get the level of
        :return: the word and its level. none if it was not in a JLPT list
        """
        result = self.N5.search_dic(word)
        if result != None: return result, "N5"

        result = self.N4.search_dic(word)
        if result != None: return result, "N4"

        result = self.N3.search_dic(word)
        if result != None: return result, "N3"

        result = self.N2.search_dic(word)
        if result != None: return result, "N2"

        result = self.N1.search_dic(word)
        if result != None: return result, "N1"

        return None

    def get_jisho_definition(self, word):
        """
        Fetches definition from Jisho for non-JLPT words.
        Checks persistent cache first, then fetches and saves if not found.
        """
        print(f"looking for: {word}")

        if word in self.jisho_cache:
            print(f"Hit cache for: {word}")
            if self.jisho_cache[word] == "NOT_FOUND":
                return None
            return self.jisho_cache[word]

        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            time.sleep(0.1)
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code != 200:
                print(f"Jisho API status {response.status_code} for: {word}")
                return None

            data = response.json()

            if data.get("data"):
                senses = data["data"][0]["senses"]
                definitions = [sense["english_definitions"] for sense in senses]
                flat_definitions = [definition for sublist in definitions for definition in sublist]

                if flat_definitions:
                    final_def = "; ".join(flat_definitions[:2])
                    self.jisho_cache[word] = final_def
                    self.save_cache()
                    print(final_def)
                    return final_def

        except Exception as e:
            print(f"Error fetching {word}: {e}")

        print(f"No definition found for '{word}', caching as NOT_FOUND.")
        self.jisho_cache[word] = "NOT_FOUND"
        self.save_cache()

        return None

    def calculate_JLPT_score(self, sentence):
        """
        Calculates the JLPT score of a sentence.
        """
        JLPT_distribution = [0, 0, 0, 0, 0]
        non_JLPT_words = []
        self.sentence_breakdown.set_sentence(sentence)
        word_list = self.sentence_breakdown.get_all_dict_forms()
        for word in word_list:
            result = self.search_lists(word)
            if result == None:
                non_JLPT_words.append(word)
            elif result[1] == "N5":
                JLPT_distribution[0] += 1
            elif result[1] == "N4":
                JLPT_distribution[1] += 1
            elif result[1] == "N3":
                JLPT_distribution[2] += 1
            elif result[1] == "N2":
                JLPT_distribution[3] += 1
            elif result[1] == "N1":
                JLPT_distribution[4] += 1

        if len(word_list) > 0:
            for i in range(5):
                JLPT_distribution[i] = JLPT_distribution[i] / len(word_list)

        return JLPT_distribution, non_JLPT_words, len(word_list)

    def get_difficult_words(self, sentence, user_level):
        """
        Identifies words in the sentence that are strictly above the user's JLPT level.
        Returns a list of tuples: (word, level, meaning)
        """
        print(sentence)
        try:
            user_idx = self.levels.index(user_level)
        except ValueError:
            return []

        difficult_words = []
        seen_words = set()

        self.sentence_breakdown.set_sentence(sentence)
        word_list = self.sentence_breakdown.get_all_dict_forms()

        for word in word_list:
            if word in seen_words:
                continue

            result = self.search_lists(word)

            if result:
                meaning, word_level = result
                try:
                    word_idx = self.levels.index(word_level)
                    if word_idx > user_idx:
                        difficult_words.append((word, word_level, meaning))
                        seen_words.add(word)
                except ValueError:
                    pass
            else:
                # Word is NOT in local JLPT lists
                definition = self.get_jisho_definition(word)
                if definition:
                    difficult_words.append((word, "Outside JLPT", definition))
                    seen_words.add(word)

        return difficult_words