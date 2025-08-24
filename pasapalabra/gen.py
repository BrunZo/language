import argparse
import csv
import random

import defs.rae as rae
import defs.wiktionary as wikt

sources = { "rae": rae, "wikt": wikt }

def strip_accents(s):
    """Remove accents from words so that first letter is accent-insensitive"""
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "ü": "u", "Ü": "U"
    }
    return "".join(replacements.get(c, c) for c in s)

def load_words(filename):
    """Load word-frequency list from CSV: word,frequency"""
    words = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Omit headers
        for word, freq in reader:
            words.append((word.lower(), float(freq)))
    return words

def generate_rosco(words, attempts_per_letter, source=wikt):
    """Generate a rosco from the word list"""
    rosco = {}
    letters = 'ABCDEFGHIJLMNÑOPQRSTUVXYZ'
    can_contain = 'HJÑQUXYZ'
    
    # Pre-group words by starting letter
    grouped = {}
    for w, f in words:
        first_letter = strip_accents(w[0].upper())
        grouped.setdefault(first_letter, []).append((w, f))

        for letter in w.upper().replace('ñ', 'Ñ'):
            if letter in can_contain:
                grouped.setdefault(letter, []).append((w, f))

    for letter in letters:
        candidates = grouped[letter]
        words_only = [w for w, _ in candidates]
        freqs = [f for _, f in candidates]
        
        chosen_word = None
        chosen_def = None
        
        for _ in range(attempts_per_letter):
            word = random.choices(words_only, weights=freqs, k=1)[0]
            definition = source.get_definition(word)
            if definition:
                chosen_word = word
                chosen_def = definition
                break
        
        rosco[letter] = (chosen_word, chosen_def)
    
    return rosco

def make_definition(letter, word, definition):

    if word == None:
        return "N/A"

    if letter == word.upper()[0]:
        return f"[{letter}] {definition}"
    else:
        return f"[Contiene {letter}] {definition}"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("dictionary", help="Path to the dictionary file.")
    parser.add_argument("-d", "--dest_file", help="Path in which the output files will be saved.")
    parser.add_argument("-s", "--source", default="wikt", choices=sources.keys(), help="From which dictionary fetch the definitions.")
    parser.add_argument("-n", "--num_iters", type=int, default=1, help="Number of attempts for each letter.")

    args = parser.parse_args()

    words = load_words(args.dictionary)
    rosco = generate_rosco(words, attempts_per_letter=args.num_iters, source=sources[args.source])

    words_only = [word if word else 'N/A' for _, (word, _) in rosco.items()]
    definitions = [
        make_definition(letter, word, definition) for letter, (word, definition) in rosco.items()
    ]

    with open(f"{args.dest_file}/words.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(words_only))

    with open(f"{args.dest_file}/definitions.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(definitions))