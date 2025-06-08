# pip install svgling
# pip install nltk
# pip install SpeechRecognition
# pip install pyaudio
# pip install ffmpeg-python

# pip install ipykernel
# python -m ipykernel install --user --name=venv311 --display-name "Python 3.11 (venv311)"

# Path to input audio file
AUDIO_FILE = ("data/Standard_recording_68.wav")

import os
import nltk
from nltk.parse.stanford import StanfordParser
# from nltk import ParentedTree, Tree
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# from nltk.stem import PorterStemmer
from nltk import pos_tag
from nltk.corpus import stopwords
import re
import speech_recognition as sr

r = sr.Recognizer()
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4') # for lemmatizer
nltk.download('averaged_perceptron_tagger')

#Setting java path
java_path = "/usr/lib/jvm/java-11-openjdk-amd64/bin/java"
os.environ['JAVAHOME'] = java_path

# Setting up the Stanford Parser
sp = StanfordParser(path_to_jar='stanford-parser-full-2018-02-27/stanford-parser.jar', 
                    path_to_models_jar='stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models.jar')

# stopwords_set = set(['a', 'an', 'the', 'is','to','The','in','of','us'])

stopwords_set = set(stopwords.words('english'))
# print("Stopwords loaded:", stopwords_set)

pronouns = {
    'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'mine', 'yours', 'ours', 'theirs'
}

auxiliaries = {'is', 'am', 'are', 'was', 'were', 'be', 'being', 'been', 'do', 'does', 'did', 'have', 'has', 'had'}

def text_to_isl(raw_sentence):
    # REMOVE hardcoded override
    # raw_sentence = " The boy is playing football with his friend."
    print("Converting text to ISL gloss...")

    pattern = r'[^\w\s]'
    raw_sentence = re.sub(pattern, '', raw_sentence)

    sentence = ""
    for w in raw_sentence.split():
        w = w.lower().strip()
        if w not in stopwords_set or w in pronouns:
            sentence += w + " "

    englishtree = [tree for tree in sp.parse(sentence.split())]
    parsetree = englishtree[0]
    words = parsetree.leaves()

    # Use POS tagging
    tagged = pos_tag([w.lower() for w in words])

    # Convert NLTK POS to WordNet POS (simple mapping)
    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return 'a'
        elif treebank_tag.startswith('V'):
            return 'v'
        elif treebank_tag.startswith('N'):
            return 'n'
        elif treebank_tag.startswith('R'):
            return 'r'
        else:
            return 'n'  # default to noun

    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [
        lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in tagged
    ]

    # Initialize string outside loop
    islsentence = ""
    for w in lemmatized_words:
        if w not in stopwords_set or w in pronouns:
            islsentence += w + " "

    return islsentence.lower().strip()


# OLD Speech To Text trial conversion
# print("Converting text to ISL gloss...")
# with sr.AudioFile(AUDIO_FILE) as source:
#     #reads the audio file. Here we use record instead of
#     #listen
#     audio = r.record(source)
# speech=r.recognize_google(audio)
# speech = "the loud and happy dog is playing in the park with a boy who fell down"
# print("RAW TEXT: ", speech)
# print("ISL GLOSS TEXT: ", text_to_isl(speech))
