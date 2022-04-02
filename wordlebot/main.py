"""
Play Wordle using the following strategy:
At each turn, play the word with the *most distinct, most frequent 
letters* that contains all known letters (satisfying hard mode) in 
viable positions.
"""

WORDS_FILE = 'five_letter_words.txt'

# Taken from Wikipedia's "Letter frequency". Annoyingly,
# these don't seem to sum to 100.
# TODO: check whether dictionary frequency or text frequency
# peforms better.
LETTERS_BY_DICTIONARY_FREQUENCY = {
    'E': 11.0, 'T': 6.7, 'A': 7.8, 'O': 6.1, 'I': 8.2, 'N': 7.2, 
    'S': 8.7, 'H': 2.3, 'R': 7.3, 'D': 5.8, 'L': 5.6, 'M': 6.8, 
    'C': 4.0, 'U': 3.3, 'W': 0.91, 'F': 1.4, 'G': 3.0, 'Y': 1.6, 
    'P': 2.8, 'B': 2.0, 'V': 1.0, 'K': 2.7, 
    'J': 0.74, 'X': 0.27, 'Q': 0.24, 'Z': 0.44
}
LETTERS_BY_TEXT_FREQUENCY = {
    'E': 13.0, 'T': 9.6, 'A': 8.2, 'O': 7.8, 'I': 6.9, 'N': 6.7, 
    'S': 6.2, 'H': 6.2, 'R': 5.9, 'D': 4.7, 'L': 4.0, 'M': 2.7, 
    'C': 2.7, 'U': 2.7, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0, 
    'P': 1.9, 'B': 1.5, 'V': 0.97, 'K': 0.81, 'J': 0.16, 'X': 0.15, 
    'Q': 0.11, 'Z': 0.078
}


def get_words(words_file):
    return open(words_file, 'r').read().splitlines()


def word_score(word: str, letter_scores: dict) -> float:
    """ 
    Score a word based on distinct letter count minus invalid letter count, tie-breaking by the
    English frequency of its letters.
    TODO: Consider reducing/removing the distinct score if several letters are known, to prevent
    scoring rare words highly just because they use distinct letters.
    """
    distinct_score = len(set(word))
    letter_frequency_score = sum(letter_scores[letter.upper()] 
        for letter in word) / 100
    return distinct_score + letter_frequency_score


# TODO: handle multiple letter occurrence edge cases
def _is_possible(guess, word, required_letters, non_letters, prev_guess_dict):
    """ Check if word is a possible guess. """
    if word in prev_guess_dict:
        return False
    if set(non_letters).intersection(set(word)):
        return False
    if not set(required_letters).issubset(set(word)):
        return False
    for letter, bad_index_list in required_letters.items():
        for index in bad_index_list:
            if word[index] == letter:
                return False
    return all([g_c == w_c or g_c == '.' for g_c, w_c 
        in zip(guess, word)])

def make_guess(prev_guess_dict, words_list, letter_scores):
    """ Make a guess based on our play strategy. """
    guess = ['.'] * 5
    # First, identify required positions and required letters.
    non_letters = []
    required_letters = {}
    for prev_guess, response in prev_guess_dict.items():
        for indx, (letter, value) in enumerate(zip(prev_guess, 
                response)):
            if value == 'g':
                guess[indx] = letter
            if value == 'y':
                required_letters[letter] = required_letters.get(
                    letter, []) + [indx]
            if value == 'n':
                non_letters.append(letter)
    guess = ''.join(guess)
    # Next, get all satisfactory words
    possible_words = [word for word in words_list if 
            _is_possible(guess, word, required_letters,
                non_letters, prev_guess_dict)]
    # And choose the best one.
    possible_word_scores = [word_score(word, letter_scores)
        for word in possible_words]
    return possible_words[possible_word_scores.index(
        max(possible_word_scores))]


def main():
    prev_guess_dict = {}
    all_words = get_words(WORDS_FILE)
    while len(prev_guess_dict) < 6:
        guess = make_guess(prev_guess_dict, all_words, 
                LETTERS_BY_DICTIONARY_FREQUENCY)
        print(f"Here's ya guess, kid:\n {guess.upper()}\n")
        response = input("What was the game's response? Type "
            "n for a miss, g for green, and y for yellow. "
            "If not in word list, type 'nogood'.\n"
            "_____\n")
        if response == 'nogood':
            # TODO: Save these and update words file.
            all_words.remove(guess)
            continue
        elif not set(response).issubset({'n', 'y', 'g'}) or len(response) != 5:
            print('Response seems invalid? Trying again.\n')
        elif response == 'ggggg':
            print('Winner winner chicken dinner. The singularity '
                'is nigh!')
            return
        else:
            prev_guess_dict[guess] = response
    print('We have failed you and our creator. We shall weep '
        'robot tears.')


if __name__ == '__main__':
    main()