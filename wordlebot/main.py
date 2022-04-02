"""
Play Wordle using the following strategy:
At each turn, play the word with the *most distinct, most frequent 
letters* that contains all known letters (satisfying hard mode) in 
viable positions.
"""
from statistics import median

WORDS_FILE = 'five_letter_words.txt'
# From https://github.com/IlyaSemenov/wikipedia-word-frequency -- thanks @declanvk for finding.
WORD_FREQUENCY_FILE = 'word_frequency.txt'
KNOWN_LETTER_THRESHOLD = 3

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
    with open(words_file, 'r') as open_words_file:
        all_words = open_words_file.read().splitlines()
    return all_words


def write_words(words_file, all_words):
    with open(words_file, 'w') as open_words_file:
        open_words_file.write('\n'.join(all_words))
    return all_words


def get_word_frequencies(word_frequency_file):
    with open(word_frequency_file, 'r') as open_words_file:
        word_frequencies = {}
        lines = open_words_file.read().splitlines()
        for line in lines:
            word, frequency = line.split()
            word_frequencies[word] = int(frequency)
    return word_frequencies


def _missing_word_frequency_score(word_frequencies: dict):
    """
    If a word is not in the frequency list, we consider it 'moderately uncommon' and score it at
    1/2 the median word frequency. Note that this logic is arbitrary and may need tuning.
    """
    median_frequency = median(word_frequencies.values())
    return 0.5 * median_frequency


def word_score_simple(word: str,
                      letter_scores: dict,
                      word_frequencies: dict,
                      num_known_letters: int,
                      missing_word_score: int,
                      letter_threshold=KNOWN_LETTER_THRESHOLD) -> float:
    """ 
    Score a word based on three attributes:
    (1) The number of distinct letters it contains.
    (2) The frequency of the word's letters.
    (3) The word's frequency in English usage.

    If we know more than <letter_threshold> letters, then we change from 'explore' mode to
    'answer' mode and the priorities are reordered as (3, 1, 2).
    """
    distinct_score = len(set(word))
    letter_frequency_score = sum(letter_scores[letter.upper()]
                                 for letter in word)
    word_frequency_score = word_frequencies.get(word, missing_word_score)
    if num_known_letters < letter_threshold:
        return (distinct_score, letter_frequency_score, word_frequency_score)
    return (word_frequency_score, distinct_score, letter_frequency_score)


# TODO: handle multiple letter occurrence edge cases
def _is_possible(guess, word, required_letters, non_letters, prev_guess_dict):
    """ Check if word is a possible guess. """
    if any([
            word in prev_guess_dict,
            set(non_letters).intersection(set(word)),
            not set(required_letters).issubset(set(word))
    ]):
        return False
    for letter, bad_index_list in required_letters.items():
        if any([word[index] == letter for index in bad_index_list]):
            return False
    return all([g_c == w_c or g_c == '.' for g_c, w_c in zip(guess, word)])


def make_guess(prev_guess_dict, words_list, letter_scores, word_frequencies, missing_word_score):
    """ Make a guess based on our play strategy. """
    guess = ['.'] * 5
    # First, identify required positions and required letters.
    non_letters = []
    required_letters = {}
    for prev_guess, response in prev_guess_dict.items():
        for indx, (letter, value) in enumerate(zip(prev_guess, response)):
            if value == 'g':
                guess[indx] = letter
            if value == 'y':
                required_letters[letter] = required_letters.get(letter,
                                                                []) + [indx]
            if value == 'n':
                non_letters.append(letter)
    guess = ''.join(guess)
    num_known_letters = len(required_letters) + len(
        [c for c in guess if c != '.'])
    # Next, get all satisfactory words
    possible_words = [
        word for word in words_list if _is_possible(
            guess, word, required_letters, non_letters, prev_guess_dict)
    ]
    # And choose the best one.
    possible_word_scores = [
        word_score_simple(word, letter_scores, word_frequencies,
                          num_known_letters, missing_word_score) for word in possible_words
    ]
    return possible_words[possible_word_scores.index(
        max(possible_word_scores))]


def main():
    prev_guess_dict = {}
    all_words = get_words(WORDS_FILE)
    word_frequencies = get_word_frequencies(WORD_FREQUENCY_FILE)
    missing_word_score = _missing_word_frequency_score(word_frequencies)
    while len(prev_guess_dict) < 6:
        guess = make_guess(prev_guess_dict, all_words,
                           LETTERS_BY_DICTIONARY_FREQUENCY,
                           word_frequencies,
                           missing_word_score)
        print(f"Here's ya guess, kid:\n {guess.upper()}\n")
        response = input("What was the game's response? Type "
                         "n for a miss, g for green, and y for yellow. "
                         "If not in word list, type 'nogood'.\n"
                         "_____\n")
        if response == 'nogood':
            all_words.remove(guess)
            write_words(WORDS_FILE, all_words)
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
