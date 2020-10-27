from django.contrib import admin

from .models import (
    Word,
    Translation,
    WordTranslated,
    FailedTranslation,
)

admin.site.register(Word)
admin.site.register(Translation)
admin.site.register(WordTranslated)
admin.site.register(FailedTranslation)