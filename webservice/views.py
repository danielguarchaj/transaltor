from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Word,
    Translation,
    WordTranslated,
    FailedTranslation,
)

from django.contrib.auth.models import User


class TranslateAPIView(APIView):
    def get_translation_and_alternatives(self, source_alternatives, target_alternatives, match, text):
        response = {}
        for i in range(len(source_alternatives)):    
            if text == source_alternatives[i]:
                word = match
                translation = target_alternatives[0]
                response['original_word'] = text
                response['word'] = word
                response['translation'] = translation
                del source_alternatives[i]
                response['source_alternatives'] = source_alternatives
                response['target_alternatives'] = target_alternatives[1:]
                return response
        return response

    def get_translation(self, text, matches, translated_from):
        response = {}
        for match in matches:
            kiche_alternatives = match.kiche.split(';')
            spanish_alternatives = match.spanish.split(';')
            if translated_from == 1:
                response = self.get_translation_and_alternatives(spanish_alternatives, kiche_alternatives, match, text)
            elif translated_from == 2:
                response = self.get_translation_and_alternatives(kiche_alternatives, spanish_alternatives, match, text)
            if 'word' in response:
                print(response['word'])
                return response
        response = 'failed-translation'
        return response

    def post(self, request, *args, **kwargs):
        response = {}
        translated_from = request.data['translated_from']
        text = request.data['text']
        single_word = request.data['single_word']
        user = request.user if request.user.is_authenticated else None
        if single_word:
            matches = Word.objects.filter(spanish__icontains=text) if translated_from == 1 else Word.objects.filter(kiche__icontains=text) 
            response = self.get_translation(text, matches, translated_from)
            if response != 'failed-translation':
                new_translation = Translation.objects.create(
                    translated_from = translated_from,
                    user = user,
                    single_word = single_word,
                    text = text
                )
                word_translated = WordTranslated.objects.create(
                    translation = new_translation,
                    word = response['word']
                )
                del response['word']
            elif response == 'failed-translation':
                FailedTranslation.objects.create(
                    single_word = single_word,
                    translated_from = translated_from,
                    user = user,
                    text = text
                )
        else:
            words = text.split()
            response = []
            translated_words = []
            failed_translation = False
            for word in words:
                matches = Word.objects.filter(spanish__icontains=word) if translated_from == 1 else Word.objects.filter(kiche__icontains=word)
                word_translation = self.get_translation(word, matches, translated_from)
                print(word_translation)
                if word_translation == 'failed-translation':
                    failed_translation = True
                    response = 'failed-translation'
                    FailedTranslation.objects.create(
                        single_word = single_word,
                        translated_from = translated_from,
                        user = user,
                        text = text
                    )
                    break
                else:
                    translated_words.append(word_translation['word'])
                    del word_translation['word']
                    response.append(word_translation)
            if not failed_translation:
                new_translation = Translation.objects.create(
                    translated_from = translated_from,
                    user = user,
                    single_word = single_word,
                    text = text
                )
                for w in translated_words:
                    word_translated = WordTranslated.objects.create(
                        translation = new_translation,
                        word = w
                    )
        return Response(response)