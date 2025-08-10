import argparse
import csv
import random
import requests
import unicodedata

WIKTIONARY_API = "https://es.wiktionary.org/w/api.php"

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
        reader = csv.reader(f, delimiter='\t')
        next(reader) # Omit headers
        for word, freq in reader:
            words.append((word.lower(), float(freq)))
    return words

def get_definition(word):
    """Fetch definition from Wiktionary"""
    params = {
        "action": "query",
        "prop": "extracts",
        "titles": word,
        "format": "json",
        "explaintext": True
    }
    r = requests.get(WIKTIONARY_API, params=params)
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        extract = page.get("extract", "")
        if extract:
            start = extract.find("1\n") + 2
            end = extract.find("\n", start)
            definition = extract[start:end]
            return definition
    return None

def validate_word(word, definition):
    return len(word) >= 3 and len(word.split()) == 1 and \
            len(definition.split()) in range(4, 20)

def generate_rosco(words, attempts_per_letter):
    """Generate a rosco from the word list"""
    rosco = {}
    letters = [chr(c) for c in range(ord('A'), ord('Z') + 1)] + ['Ñ']
    
    # Pre-group words by starting letter
    grouped = {}
    for w, f in words:
        first_letter = strip_accents(w[0].upper())
        grouped.setdefault(first_letter, []).append((w, f))

    for letter in letters:
        if letter not in grouped:
            rosco[letter] = (None, None)
            continue
        
        candidates = grouped[letter]
        words_only = [w for w, _ in candidates]
        freqs = [f for _, f in candidates]
        
        chosen_word = None
        chosen_def = None
        
        for _ in range(attempts_per_letter):
            word = random.choices(words_only, weights=freqs, k=1)[0]
            definition = get_definition(word)
            if definition and validate_word(word, definition):
                chosen_word = word
                chosen_def = definition
                break
        
        rosco[letter] = (chosen_word, chosen_def)
    
    return rosco

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("dictionary", help="Path to the dictionary file.")
    parser.add_argument("-n", "--num_iters", default=10, help="Number of attempts for each letter")

    args = parser.parse_args()

    words = load_words(args.dictionary)
    rosco = generate_rosco(words, attempts_per_letter=args.num_iters)

    for letter, (word, definition) in rosco.items():
        if word and definition:
            print(f"{letter}: ({word}) {definition}")
        else:
            print(f"{letter}: [No encontrado]")
