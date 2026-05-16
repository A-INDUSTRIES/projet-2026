import json

TO_REPLACE = [("é", "e"),
                ("è", "e"),
                ("ê", "e"),
                ("ë", "e"),
                ("à", "a"),
                ("â", "a"),
                ("ä", "a"),
                ("ì", "i"),
                ("î", "i"),
                ("ï", "i"),
                ("ò", "o"),
                ("ô", "o"),
                ("ö", "o"),
                ("ù", "u"),
                ("û", "u"),
                ("ü", "u"),
                ("ç", "c"),
                ("œ", "oe"),
                ("-", ""),
                ("æ", "ae"),
                ("ñ", "n"),
                ("ã", "a"),
                ("ó", "o"),
                ("/", ""),
                (" ", "")]

with open("coords.json", 'r') as f:
    coords = json.load(f)

with open("words.csv", 'r', encoding="utf-8-sig") as f:
    words = f.readlines()

wordPaths = []
for originalWord in words:
    word = originalWord.strip()
    for l,m in TO_REPLACE:
        word = word.replace(l, m)
    letters = list(word)

    wordPath = []
    for letter in letters:
        coord = coords[letter]
        wordPath.append(coord)

    wordPaths.append({originalWord.strip(): wordPath})

with open("word_paths_raw.json", 'w', encoding="utf-8") as f:
    json.dump(wordPaths, f, indent=4, ensure_ascii=False)