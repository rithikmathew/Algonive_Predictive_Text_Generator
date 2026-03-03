import re
import json
from collections import defaultdict, Counter
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomDictionary

# --- 1. NLP MARKOV CHAIN SETUP ---
# Dictionary to hold our word associations
markov_model = defaultdict(Counter)


def train_model(text):
    """Simple n-gram (bigram) trainer."""
    words = re.findall(r'\w+', text.lower())
    for i in range(len(words) - 1):
        markov_model[words[i]][words[i + 1]] += 1


# Initial base corpus to train the model so it isn't empty
base_corpus = """
hello world this is a predictive text generator built with django and python. 
it uses natural language processing to suggest the next word based on context. 
machine learning makes this smart and highly customizable.
"""
train_model(base_corpus)

# Load existing custom words from database into the model on startup
try:
    custom_entries = CustomDictionary.objects.all()
    for entry in custom_entries:
        train_model(entry.word_or_phrase)
except Exception:
    pass  # Database might not be migrated yet


# --- 2. DJANGO VIEWS ---

def index(request):
    """Renders the single-page HTML interface."""
    return render(request, 'predictor/index.html')


def predict(request):
    """API endpoint that returns word suggestions."""
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'suggestions': []})

    # Get the last typed word
    words = re.findall(r'\w+', query.lower())
    if not words:
        return JsonResponse({'suggestions': []})

    last_word = words[-1]

    # Check the Markov model for the next likely words
    if last_word in markov_model:
        # Get the top 3 most common subsequent words
        top_matches = [word for word, count in markov_model[last_word].most_common(3)]
        return JsonResponse({'suggestions': top_matches})

    return JsonResponse({'suggestions': []})


@csrf_exempt
def add_word(request):
    """API endpoint to add a new phrase to the dictionary and retrain."""
    if request.method == 'POST':
        data = json.loads(request.body)
        new_text = data.get('text', '').strip()

        if new_text:
            # Save to database
            CustomDictionary.objects.get_or_create(word_or_phrase=new_text)
            # Retrain the active model with the new text
            train_model(new_text)
            return JsonResponse({'status': 'success', 'message': f'"{new_text}" added to custom dictionary!'})

    return JsonResponse({'status': 'error'}, status=400)
# Create your views here.
