from django.urls import path

from . import views

app_name = "core"


urlpatterns = [
    path("", views.home, name="home"),
    path("play/<uuid:uuid>", views.supermorpion, name="play"),
    path("new-game", views.new_game, name="new-game"),
    path("rules", views.rules, name="rules"),
    path("credits", views.credits_view, name="credits"),
    path("legals", views.legals, name="legals"),
]
