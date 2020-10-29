from django.contrib import admin

from .models import (
    Word,
    Translation,
    WordTranslated,
    FailedTranslation,
    Profile,
)

admin.site.register(Word)
admin.site.register(Translation)
admin.site.register(WordTranslated)
admin.site.register(FailedTranslation)
admin.site.register(Profile)