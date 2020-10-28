from django.db import models

from django.contrib.auth.models import User


from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()


class Word(models.Model):
    spanish = models.CharField(max_length=500)
    kiche = models.CharField(max_length=500)
    translations_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='traductor/palabras_imagenes/', null=True, blank=True)

    def __str__(self):
        return f'{self.spanish} - {self.kiche}'


class Translation(models.Model):
    translated_from = models.SmallIntegerField(choices=[
        (1, 'Español'),
        (2, 'Kiche')
    ])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translations', null=True, blank=True)
    single_word = models.BooleanField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        translated_from = "Español to Kiche" if self.translated_from == 1 else "Kiche to Español"
        return f'Translated by: {self.user.username} - Single word: {self.single_word} - Translated from: {translated_from}'


class WordTranslated(models.Model):
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE, related_name='words_translated')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='translations')
    user_age = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.word.spanish} - {self.word.kiche}'


class FailedTranslation(models.Model):
    translated_from = models.SmallIntegerField(choices=[
        (1, 'Español'),
        (2, 'Kiche')
    ])
    single_word = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='failed_translations', null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)