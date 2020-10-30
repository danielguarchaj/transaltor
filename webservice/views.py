from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .models import (
    Word,
    Translation,
    WordTranslated,
    FailedTranslation,
)

from .paginations import (
    DefaultPagination
)

from django.contrib.auth.models import User
from datetime import datetime, date
from dateutil.parser import parse

from .serializers import UserSerializer, FailedTranslationSerializer, WordSerializer


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.db.models import Sum, Count

from rest_framework.permissions import IsAuthenticated

class TopTenTranslatedWordsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request, *args, **kwargs):
        query_params = self.request.query_params

        if 'age' in query_params:
            qs = WordTranslated.objects.filter(user_age=int(query_params['age']))\
                    .values('word__kiche', 'word__spanish') \
                    .annotate(translations=Count('word')) \
                    .order_by('-translations')[:10]
        elif 'lt_age' in query_params:
            qs = WordTranslated.objects.filter(user_age__lt=int(query_params['lt_age']))\
                    .values('word__kiche', 'word__spanish') \
                    .annotate(translations=Count('word')) \
                    .order_by('-translations')[:10]
        elif 'gt_age' in query_params:
            qs = WordTranslated.objects.filter(user_age__gt=int(query_params['gt_age']))\
                    .values('word__kiche', 'word__spanish') \
                    .annotate(translations=Count('word')) \
                    .order_by('-translations')[:10]
        else:
            qs = WordTranslated.objects.values('word__kiche', 'word__spanish') \
                    .annotate(translations=Count('word')) \
                    .order_by('-translations')[:10]

        return Response(list(qs))


class FailedTranslationsListAPIView(ListAPIView):
    serializer_class = FailedTranslationSerializer
    permission_classes = (IsAuthenticated, )
    queryset = FailedTranslation.objects.all()
    pagination_class = DefaultPagination


class WordListAPIView(ListAPIView):
    serializer_class = WordSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Word.objects.all()
    pagination_class = DefaultPagination


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user_serializer = UserSerializer(user)
        token['user'] = user_serializer.data
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        required_fields = ['username', 'first_name', 'last_name', 'password', 'birth_date']
        missing_fields = []
        for field in required_fields:
            if field not in request.data: 
                missing_fields.append(field)

        if len(missing_fields) > 0:
            return Response({"status": 400, "message": "missing fields", "missing_fields": missing_fields})
        
        existing_user = False

        try:
            User.objects.get(username=request.data['username'])
            existing_user = True
        except:
            pass
        
        if existing_user:
            return Response({"status": 400, "message": "Username already registered"})

        try:
            parse(request.data['birth_date'])    
        except:
            return Response({"status": 400, "message": "Invalid date format. Expected: yyyy-mm-dd"})
        data = request.data
        new_user = User.objects.create_user(data['username'], None, str(data['password']))
        new_user.first_name = data['first_name']
        new_user.last_name = data['last_name']
        new_user.profile.birth_date = data['birth_date']
        
        new_user.save()
        new_user.profile.save()

        user_serializer = UserSerializer(new_user)
        user_data = user_serializer.data

        return Response({"status": 201, "data": user_data})


class TranslateAPIView(APIView):
    def get_user_age(self, birth_date):
        if birth_date is None:
            return 0
        today = date.today()
        age =  today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def get_translation_and_alternatives(self, source_alternatives, target_alternatives, match, text):
        response = {}
        for i in range(len(source_alternatives)):    
            if text == source_alternatives[i]:
                word = match
                translation = target_alternatives[0]
                response['original_word'] = text
                response['word'] = word
                response['translation'] = translation
                try:
                    response['image_url'] = word.image.url
                except:
                    response['image_url'] = None
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
                return response
        response = 'failed-translation'
        return response

    def post(self, request, *args, **kwargs):
        response = {}
        translated_from = request.data['translated_from']
        text = request.data['text'].strip()
        single_word = request.data['single_word']
        user = request.user if request.user.is_authenticated else None
        try:
            user_birth_date = user.profile.birth_date
        except:
            user_birth_date = None
        user_age = self.get_user_age(user_birth_date)
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
                    word = response['word'],
                    user_age = user_age
                )
                word_object = response['word']
                word_object.translations_count = word_object.translations_count + 1
                word_object.save()
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
                word = word.strip()
                matches = Word.objects.filter(spanish__icontains=word) if translated_from == 1 else Word.objects.filter(kiche__icontains=word)
                word_translation = self.get_translation(word, matches, translated_from)
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
                        word = w,
                        user_age = user_age
                    )
                    word_object = w
                    word_object.translations_count = word_object.translations_count + 1
                    word_object.save()
        return Response(response)


import openpyxl
from pathlib import Path


def upload_dictionary(request):
    # Setting the path to the xlsx file:
    xlsx_file = Path('dictionary.xlsx')

    wb_obj = openpyxl.load_workbook(xlsx_file)
    wsheet = wb_obj.active

    col_kiche = 'A'
    col_spanish = 'B'

    row = 2
    while row < 466:
        Word.objects.create(
            spanish = str(wsheet[f'{col_spanish}{row}'].value).lower().strip().replace('; ', ';').replace('’', "'"),
            kiche = str(wsheet[f'{col_kiche}{row}'].value).lower().strip().replace('; ', ';').replace('’', "'"),
        )
        print(row)
        row += 1