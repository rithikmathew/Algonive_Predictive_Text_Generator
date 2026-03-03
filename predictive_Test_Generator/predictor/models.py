
from django.db import models

class CustomDictionary(models.Model):
    word_or_phrase = models.CharField(max_length=255, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word_or_phrase
# Create your models here.
