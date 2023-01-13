from django.urls import path
from riot_app.users.api import views as api_views

urlpatterns = [
    path('matches/', api_views.MatchListCreateAPIView.as_view(), name='match-list'),
    path('matches/<int:pk>', api_views.MatchDetailAPIView.as_view(), name='match-data'),
    path('profile/', api_views.ProfileListCreateAPIView.as_view(), name='profile-list'),
    path('profile/<str:name_id>/<str:region_id>', api_views.ProfileDetailAPIView.as_view(), name='profile-data'),
    path('player/', api_views.PlayerListCreateAPIView.as_view(), name='player-list'),
    path('player/<int:pk>', api_views.PlayerDetailCreateAPIView.as_view(), name='player-data'),
]
