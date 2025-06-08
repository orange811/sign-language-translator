import ast
from sentence_transformers import SentenceTransformer, util

# Load your dictionary
DICT_FILE = "data/gloss_dict.txt"
with open(DICT_FILE, "r", encoding="utf-8") as f:
    GLOSS_DICT = ast.literal_eval(f.read())

# Create reverse mapping: key is the dict entry, value is the original gloss key
gloss_keys = list(GLOSS_DICT.keys())

# Load sentence transformer model (you can choose lighter if needed)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings for the entire dictionary only once
dict_embeddings = model.encode(gloss_keys, convert_to_tensor=True)

def map_gloss_sentence(gloss_sentence):
    gloss_words = gloss_sentence.lower().split()
    result = {}

    for word in gloss_words:
        # Try exact match
        if word in GLOSS_DICT:
            result[word] = GLOSS_DICT[word]
            continue
        
        # Else, find most similar word in dictionary
        word_embedding = model.encode(word, convert_to_tensor=True)
        cosine_scores = util.cos_sim(word_embedding, dict_embeddings)[0]
        best_match_id = int(cosine_scores.argmax())
        best_score = float(cosine_scores[best_match_id])

        threshold = 0.45  # You can tune this
        if best_score >= threshold:
            best_gloss = gloss_keys[best_match_id]
            result[word] = GLOSS_DICT[best_gloss]
        else:
            result[word] = None  # or leave unmapped

    return result

# # Example usage
# gloss_sentence = "loud happy dog playing park boy fell"
# mapped = map_gloss_sentence(gloss_sentence)
# for word, mapping in mapped.items():
#     print(f"{word} → {mapping}")
