from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from riot_app.users.api.serializers import (
    MatchDataSerializer,
    PlayerSerializer,
    ProfileSerializer,
)
from riot_app.users.models import MatchData, Player, Profile
from riotwatcher import LolWatcher
from json import dumps, loads
from django.http import Http404
from datetime import datetime, timedelta
from django.utils import timezone

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class MatchListCreateAPIView(generics.ListCreateAPIView):
    queryset = MatchData.objects.all()
    serializer_class = MatchDataSerializer


class MatchDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MatchData.objects.all()
    serializer_class = MatchDataSerializer


class ProfileListCreateAPIView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        # Check Database
        name_id = self.kwargs["name_id"]
        region_id = self.kwargs["region_id"]
        profile = Profile.objects.filter(s_name=name_id, region=region_id).first()
        present = timezone.now()

        if profile:
            #calculate profile's last updated time and present time
            last_updated = profile.last_updated
            profile_last_updated_time = (
                last_updated.year
                + last_updated.month
                + last_updated.day
                + last_updated.hour
                + last_updated.minute
            )
            present_total_time = (
                present.year
                + present.month
                + present.day
                + present.hour
                + present.minute
            )
            print(type(profile_last_updated_time))
            print(profile_last_updated_time)
            print(present_total_time)
            if profile_last_updated_time + 4 > present_total_time:
                print("profile find and it's updated.")
                return profile
        print("no profile in db or not updated. Requesting from Riot...")

        ##Requests from Riot api##
        lol_watcher = LolWatcher("RGAPI-00161b91-c1fa-4485-bd70-44ecc1915643")
        europe = ["eun1", "euw1", "ru", "tr1"]
        americas = ["br1", "la1", "la2", "na1", "oc1"]
        asia = ["jp1", "kr"]
        by_name = lol_watcher.summoner.by_name  # request with name
        by_summoner = lol_watcher.league.by_summoner  # request with summoner
        by_puuid = lol_watcher.match.matchlist_by_puuid  # request with puuid
        by_id = lol_watcher.match.by_id  # request with id

        try:
            # Pull Profile stats, convert to list(prevents key_error)
            requested_profile = by_name(region_id, name_id)
            print("requested_profile:", requested_profile)
            requested_profile_stats = dumps(
                by_summoner(region_id, requested_profile["id"])
            )
            requested_profil_stats_list = loads(requested_profile_stats)
            print("requested_profile_stats:", requested_profile_stats)
            # Pull last match detail, convert to list
            if region_id in europe:
                my_matches = by_puuid("europe", requested_profile["puuid"])
                match_region = "europe"
            elif region_id in americas:
                my_matches = by_puuid("americas", requested_profile["puuid"])
                match_region = "americas"
            elif region_id in asia:
                my_matches = by_puuid("asia", requested_profile["puuid"])
                match_region = "asia"
            print("my_matches:",my_matches)

            #Save profile stats once
            if requested_profil_stats_list:
                    profile_obj, add_profile = Profile.objects.update_or_create(
                        s_name=requested_profile["name"],
                        region=region_id,
                        p_region=match_region,
                        level=requested_profile["summonerLevel"],
                        tier=requested_profil_stats_list[0]["tier"],
                        rank=requested_profil_stats_list[0]["rank"],
                        win=requested_profil_stats_list[0]["wins"],
                        lose=requested_profil_stats_list[0]["losses"],
                    )

            for y in range(10):
                last_match_detail = dumps(by_id(match_region, my_matches[y]))
                last_match_detail_list = loads(last_match_detail)
                
                print("y:", y)
                print("my_matches[y]:", my_matches[y])

                # Pull Player's match details
                for x in range(10):
                    if (
                        name_id
                        == last_match_detail_list["info"]["participants"][x]["summonerName"]
                    ):
                        my_player = last_match_detail_list["info"]["participants"][x]
                
                if my_matches:
                    match_obj, add_match = MatchData.objects.update_or_create(
                        match_id=my_matches[y]
                    )
                    if last_match_detail_list:
                        player_obj, first_created = Player.objects.update_or_create(
                            match_data=match_obj,
                            profile=profile_obj,
                            champ=my_player["championName"],
                            kda=round(my_player["challenges"]["kda"], 2),
                            total_gold=my_player["goldEarned"],
                            solo_kill=my_player["challenges"]["soloKills"],
                            level=my_player["champLevel"],
                            cs=my_player["totalMinionsKilled"],       
                        )
                        print("profile saved to db.")
        except:
            # No data from db and riot api
            raise Http404("Given query not found....")
        return Profile.objects.filter(s_name=name_id, region=region_id).first()   


class PlayerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerDetailCreateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
