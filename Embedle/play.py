import numpy, random, gzip

def read_frequent_nouns():
    frequent_nouns = set()
    with open('wordfreq.txt', 'r') as fp:
        for line in fp:
            if line.startswith('#'):
                # Comment line
                continue
            _, word, part_of_speech, _ = line.strip().split()
            if part_of_speech != 'n':
                continue
            frequent_nouns.add(word.lower())
    return frequent_nouns

def read_embeddings():
    embeddings = {}
    with gzip.open('embeddings.gz', 'rt', encoding='utf-8') as fp:
        for line in fp:
            parts = line.strip().split()
            if len(parts) != 301 or not parts[0].endswith('_NOUN'):
                continue
            word = parts[0][:-len('_NOUN')].lower()
            embedding = numpy.asarray([ float(x) for x in parts[1:] ],
                                      dtype=numpy.float32)
            embeddings[word] = embedding
    return embeddings

def cos_similarity(v1, v2):
    return numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))


if __name__ == '__main__':
    frequent_nouns = read_frequent_nouns()
    embeddings = read_embeddings()
    # Ensure we won't pick a secret word whose embedding is not known.
    for n in list(frequent_nouns):
        if n not in embeddings:
            frequent_nouns.remove(n)

    # word = 'taste'
    # print(cos_similarity(embeddings[word], embeddings['sourness']))
    # print(cos_similarity(embeddings[word], embeddings['horse']))
    # print(cos_similarity(embeddings[word], embeddings['escherichia']))
    # ds = [ (cos_similarity(embeddings[word], v), w)
    #        for w, v in embeddings.items()
    #        if w != word ]
    # print(sorted(ds, key=lambda t: t[0], reverse=True)[:20])

    secret_word = random.choice(list(frequent_nouns))
    print("I'm thinking of a noun. Try to guess it, Ctrl-D to give up.")
    guesses = []

    while True:
        try:
            guess = input('Guess> ')
        except EOFError:
            print(f'\nYou tried {len(guesses)} words, but failed to guess the word "{secret_word}" I was thinking about.  Better luck next time!')
            break
        guess = guess.strip().lower()
        if guess == secret_word:
            print(f'Correct! You used {len(guesses)} attempts.')
            break
        if guess in guesses:
            print(f'The word "{guess}" has been guessed before. Cosine distance to my word is {cos_similarity(embeddings[guess], embeddings[secret_word]):.4f}')
            continue
        if guess not in embeddings:
            print(f'The word "{guess}" is not known to me.')
        else:
            guesses.append(guess)
            print(f'Cosine distance from "{guess}" to my word is {cos_similarity(embeddings[guess], embeddings[secret_word]):.4f}')
            if guess not in frequent_nouns:
                print(f'The word "{guess}" is known to me, but too rare for the one I\'m thinking about.')
        print('Your closest guesses with cosine distances from my word:')
        for sim, guess in sorted([
                (cos_similarity(embeddings[g], embeddings[secret_word]), g)
                for g in guesses ],
                                 key=lambda t: t[0], reverse=True)[:20]:
            print(f'    {sim:.4f} {guess}')
