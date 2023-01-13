from django.contrib.auth import get_user_model
from rest_framework import serializers
from riot_app.users.models import MatchData, Player, Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }

class MatchDataSerializer(serializers.ModelSerializer):
    #2 tane serializer
    class Meta:
        model = MatchData
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    match_data = MatchDataSerializer(read_only=True)
    class Meta:
        model = Player
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'

