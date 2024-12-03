from flask import Flask, request, jsonify, render_template, session
import numpy as np
import random
import gzip
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random secret key


def read_frequent_nouns():
    frequent_nouns = set()
    with open('wordfreq.txt', 'r') as fp:
        for line in fp:
            if line.startswith('#'):
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
            embedding = np.asarray([float(x) for x in parts[1:]], dtype=np.float32)
            embeddings[word] = embedding
    return embeddings


def cos_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


# Load data on app start
frequent_nouns = read_frequent_nouns()
embeddings = read_embeddings()
frequent_nouns = {n for n in frequent_nouns if n in embeddings}


@app.route('/')
def index():
    if 'secret_word' not in session:
        secret_word = random.choice(list(frequent_nouns))
        session['secret_word'] = secret_word
        session['guesses'] = []
    return render_template('index.html')


@app.route('/guess', methods=['POST'])
def guess():
    guess = request.json.get('guess', '').strip().lower()
    secret_word = session.get('secret_word')
    guesses = session.get('guesses', [])

    if not guess:
        return jsonify({'error': 'Empty guess.'}), 400

    # Always compute and include closest guesses
    all_guesses = sorted(
        [{'word': g, 'similarity': float(cos_similarity(embeddings[g], embeddings[secret_word]))} for g in guesses],
        key=lambda t: t['similarity'],
        reverse=True
    )
    closest_guesses = all_guesses[:5]

    if guess == secret_word:
        return jsonify({
            'message': f'Correct! You used {len(guesses)} attempts.',
            'success': True,
            'guesses': all_guesses,
            'closest': closest_guesses
        })

    if guess in guesses:
        similarity = float(cos_similarity(embeddings[guess], embeddings[secret_word]))
        return jsonify({
            'message': f'The word "{guess}" has been guessed before. Cosine distance to secret word: {similarity:.4f}',
            'success': False,
            'guesses': all_guesses,
            'closest': closest_guesses
        })

    if guess not in embeddings:
        return jsonify({
            'message': f'The word "{guess}" is not known to me.',
            'success': False,
            'guesses': all_guesses,
            'closest': closest_guesses
        })

    # Add valid guess
    guesses.append(guess)
    session['guesses'] = guesses

    similarity = float(cos_similarity(embeddings[guess], embeddings[secret_word]))

    return jsonify({
        'message': f'Cosine distance from "{guess}" to secret word: {similarity:.4f}',
        'success': False,
        'guesses': all_guesses,
        'closest': closest_guesses
    })


@app.route('/reset', methods=['POST'])
def reset():
    secret_word = session.get('secret_word', 'Unknown')
    session.clear()
    return jsonify({'message': 'Game has been reset.', 'secret_word': secret_word})

if __name__ == '__main__':
    app.run(debug=True)