from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models


class User(AbstractUser):
    """
    Default custom user model for Riot_App.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

class MatchData(models.Model):
    match_id = models.CharField(max_length=50, null=True, unique=True)
    #

    def __str__(self):
        return f'{self.match_id}'

class Profile(models.Model):
    s_name = models.CharField(max_length=50, null=True)
    region = models.CharField(max_length=50, null=True)
    p_region = models.CharField(max_length=50, null=True)
    level = models.CharField(max_length=50, null=True)
    tier = models.CharField(max_length=50, null=True)
    rank = models.CharField(max_length=50, null=True)
    win = models.CharField(max_length=50, null=True)
    lose = models.CharField(max_length=50, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.s_name}'

class Player(models.Model):
    match_data = models.ForeignKey(MatchData, on_delete=models.CASCADE ,related_name='players')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='players')
    champ = models.CharField(max_length=50, null=True)
    kda = models.CharField(max_length=50, null=True)
    total_gold = models.IntegerField(null=True)
    solo_kill = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    cs = models.IntegerField(null=True)
    
    def __str__(self):
        return f'{self.profile.s_name} - {self.match_data.match_id}'


