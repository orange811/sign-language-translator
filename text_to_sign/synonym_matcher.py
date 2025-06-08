import json
import torch
from sentence_transformers import SentenceTransformer, util
import re
import itertools

# Load the gloss dictionary from file
def load_gloss_dict(path="data/gloss_dict.txt"):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

# Precompute embeddings for all dictionary keys
def build_dictionary_embeddings(gloss_dict, model):
    keys = list(gloss_dict.keys())
    embeddings = model.encode(keys, convert_to_tensor=True)
    return keys, embeddings

# Clean and tokenize gloss sentence
def preprocess_sentence(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r"[^\w\s\-]", "", sentence)  # remove punct except hyphen
    return sentence.split()

# Generate all possible contiguous word n-grams (e.g., "skin colour")
def generate_ngrams(words, max_n=4):
    ngrams = []
    for n in range(max_n, 0, -1):  # Start with longest phrases first
        ngrams += [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]
    return ngrams

# Map gloss sentence with multi-word phrase support
def map_gloss_sentence(gloss_sentence, gloss_dict, keys, embeddings, model, threshold=0.5):
    words = preprocess_sentence(gloss_sentence)
    used_indices = set()
    results = {}

    ngrams = generate_ngrams(words, max_n=4)

    for phrase in ngrams:
        phrase_words = phrase.split()
        start_idx = words.index(phrase_words[0])
        end_idx = start_idx + len(phrase_words)

        # Skip if these indices are already used
        if any(i in used_indices for i in range(start_idx, end_idx)):
            continue

        phrase_embedding = model.encode(phrase, convert_to_tensor=True)
        cosine_scores = util.cos_sim(phrase_embedding, embeddings)[0]
        best_score, best_idx = torch.max(cosine_scores, dim=0)
        best_score = best_score.item()

        if best_score >= threshold:
            matched_key = keys[best_idx]
            results[phrase] = gloss_dict[matched_key]
            used_indices.update(range(start_idx, end_idx))

    # Fallback: map leftover single words not part of any ngram
    for i, word in enumerate(words):
        if i in used_indices:
            continue
        word_embedding = model.encode(word, convert_to_tensor=True)
        cosine_scores = util.cos_sim(word_embedding, embeddings)[0]
        best_score, best_idx = torch.max(cosine_scores, dim=0)
        best_score = best_score.item()

        if best_score >= threshold:
            matched_key = keys[best_idx]
            results[word] = gloss_dict[matched_key]
        else:
            results[word] = None

    return results

# --- Example usage ---
if __name__ == "__main__":
    gloss_dict = load_gloss_dict("data/gloss_dict.txt")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    keys, embeddings = build_dictionary_embeddings(gloss_dict, model)

    gloss_sentence = "tiny store skin colour t-shirt"

    result = map_gloss_sentence(gloss_sentence, gloss_dict, keys, embeddings, model)

    print("Mapped Gloss Sentence to Videos:")
    for word, video in result.items():
        if video:
            print(f"{word} → {video}")
        else:
            print(f"{word} → ❌ No match found")
