from rest_framework import serializers

from django.contrib.auth.models import User

from .models import FailedTranslation, Word


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "last_login",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "profile",
        ]
        depth = 1


class FailedTranslationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = FailedTranslation
        fields = '__all__'


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'