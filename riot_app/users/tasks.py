from django.contrib.auth import get_user_model

from config import celery_app
from riot_app.users.models import MatchData, Player, Profile
from celery.schedules import crontab
from riotwatcher import LolWatcher
from json import dumps, loads


User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()

@celery_app.task()
def add_profile():
    last_added = Player.objects.last()
    print (last_added)

    name_id = last_added.profile.s_name
    region_id = last_added.profile.region
    p_region = last_added.profile.p_region
    match_data = last_added.match_data
    

    lol_watcher = LolWatcher("RGAPI-00161b91-c1fa-4485-bd70-44ecc1915643")
    by_name = lol_watcher.summoner.by_name  # request with name
    by_summoner = lol_watcher.league.by_summoner  # request with summoner
    by_puuid = lol_watcher.match.matchlist_by_puuid  # request with puuid
    by_id = lol_watcher.match.by_id  # request with id

    match_detail = dumps(by_id(p_region, match_data))
    match_detail_list = loads(match_detail)

    for x in range(10):
        the_player = match_detail_list["info"]["participants"][x]
        if match_detail_list:
            requested_profile = by_name(region_id, the_player["summonerName"])
            print("requested_profile:", requested_profile)
            requested_profile_stats = dumps(
            by_summoner(region_id, requested_profile["id"])
                    )
            requested_profil_stats_list = loads(requested_profile_stats)
            #Save profile to db
            profile_obj, add_profile = Profile.objects.update_or_create(
                s_name=the_player["summonerName"],
                region=region_id,
                p_region=p_region,
                level=requested_profile["summonerLevel"],
                tier=requested_profil_stats_list[0]["tier"],
                rank=requested_profil_stats_list[0]["rank"],
                win=requested_profil_stats_list[0]["wins"],
                lose=requested_profil_stats_list[0]["losses"],
            )
        if match_detail:
            match_obj, add_match = MatchData.objects.update_or_create(
                match_id=match_data
            )
            if match_detail_list:
                player_obj, first_created = Player.objects.update_or_create(
                    match_data=match_obj,
                    profile=profile_obj,
                    champ=the_player["championName"],
                    kda=round(the_player["challenges"]["kda"], 2),
                    total_gold=the_player["goldEarned"],
                    solo_kill=the_player["challenges"]["soloKills"],
                    level=the_player["champLevel"],
                    cs=the_player["totalMinionsKilled"],
                )
                print("profile saved to db.")

@celery_app.task()
def update_profile():
    for object in Profile.objects.all():
        name_id = object.s_name
        region_id = object.region
        p_region = object.p_region

        lol_watcher = LolWatcher("RGAPI-00161b91-c1fa-4485-bd70-44ecc1915643")
        by_name = lol_watcher.summoner.by_name  # request with name
        by_summoner = lol_watcher.league.by_summoner  # request with summoner
        by_puuid = lol_watcher.match.matchlist_by_puuid  # request with puuid
        by_id = lol_watcher.match.by_id  # request with id

        # Pull Player's match details
        requested_profile = by_name(region_id, name_id)
        print("requested_profile:", requested_profile)
        requested_profile_stats = dumps(
            by_summoner(region_id, requested_profile["id"])
        )
        requested_profil_stats_list = loads(requested_profile_stats)
        print("requested_profile_stats:", requested_profile_stats)
        
        profile_obj, add_profile = Profile.objects.update_or_create(
            s_name=name_id,
            region=region_id,
            p_region=p_region,
            level=requested_profile["summonerLevel"],
            tier=requested_profil_stats_list[0]["tier"],
            rank=requested_profil_stats_list[0]["rank"],
            win=requested_profil_stats_list[0]["wins"],
            lose=requested_profil_stats_list[0]["losses"],
        )
        print("profile updated.")
                            

