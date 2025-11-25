
import requests


class WordSearch:
    def __init__(self, user):
        self.user = user


    def search(self, search_word):

        while (search_word != "q"):
            sentences = self.user.sentence_dictionary.search_dic(search_word)
            if sentences is None:
                print("Word not found")
                break
            scored_sentences = []
            for sentence in sentences:
                JLPT_score = self.user.JLPT_lists.calculate_JLPT_score(sentence)
                temp = []
                temp.append(sentence)
                temp.append(JLPT_score[0])  # JLPT score
                temp.append(JLPT_score[1])  # Extra non-JLPT words
                temp.append(JLPT_score[2])  # Number of words
                scored_sentences.append(temp)

            sorted_sentences = self.sort_sentences(scored_sentences)


            return (self.get_jisho_definition(search_word), sorted_sentences)



    def sort_sentences(self, sentences):
        """
        Sorts the sentences based on the number of words from each JLPT level, relative to the user's level.

        Args:
            sentences: the sentences to sort

        Returns:
            [[sentence,[scores],[words that aren't in a JLPT list], number of words in the sentence]
        """
        match self.user.user_level:
            case "N5":
                sorted_sentences = sorted(sentences, key=lambda x: (x[1][0], x[1][1], x[1][2], x[1][3], x[1][4]), reverse = True)
            case "N4":
                sorted_sentences = sorted(sentences, key=lambda x: (x[1][1], x[1][0], x[1][2], x[1][3], x[1][4]), reverse = True)
            case "N3":
                sorted_sentences = sorted(sentences, key=lambda x: (x[1][2], x[1][1], x[1][0], x[1][3], x[1][4]), reverse = True)
            case "N2":
                sorted_sentences = sorted(sentences, key=lambda x: (x[1][3], x[1][2], x[1][1], x[1][0], x[1][4]), reverse = True)
            case "N1":
                sorted_sentences = sorted(sentences, key=lambda x: (x[1][4], x[1][3], x[1][2], x[1][1], x[1][0]), reverse = True)
        return sorted_sentences

    def get_jisho_definition(self, word):
        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        response = requests.get(url)
        data = response.json()
        if data["data"]:
            senses = data["data"][0]["senses"]
            # Extract 'english_definitions' from each sense
            definitions = [sense["english_definitions"] for sense in senses]
            # Flatten the list if needed
            flat_definitions = [definition for sublist in definitions for definition in sublist]
            return flat_definitions
        else:
            return ["No definition found."]



