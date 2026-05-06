import spacy
import nltk
from nltk.corpus import stopwords
import re

# Download NLTK stopwords if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class NLPCleaner:
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            # Fallback if the user hasn't downloaded it yet, 
            # though our setup command should have handled it.
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model], check=True)
            self.nlp = spacy.load(model)
            
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text: str) -> str:
        # 1. Strip Markdown-style fluff (basic links, bold, etc.)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text) # Links
        text = re.sub(r'[*_]{1,3}', '', text)               # Bold/Italic
        text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)       # Code snippets
        
        # 2. Process with spaCy for lemmatization
        doc = self.nlp(text.lower())
        
        # 3. Lemmatize and remove stopwords/punctuation/whitespace
        semantic_tokens = []
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                token.text not in self.stop_words):
                semantic_tokens.append(token.lemma_)
                
        return " ".join(semantic_tokens)
