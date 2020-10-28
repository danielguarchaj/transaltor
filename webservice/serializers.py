from rest_framework import serializers

from django.contrib.auth.models import User


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