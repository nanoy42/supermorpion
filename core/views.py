from django.shortcuts import render
from django.http import Http404, HttpResponse
import json

import uuid

from core.models import Game


def home(request):
    return render(request, "home.html")


def new_game(request):
    game = Game()
    game.save()
    return render(
        request, "new_game.html", {"x_uuid": game.x_uuid, "o_uuid": game.o_uuid}
    )


def supermorpion(request, uuid):
    games_x = Game.objects.filter(x_uuid=uuid)
    games_o = Game.objects.filter(o_uuid=uuid)
    if games_x:
        game = games_x[0]
        player = Game.Player.PLAYER_X
    elif games_o:
        game = games_o[0]
        player = Game.Player.PLAYER_O
    else:
        raise Http404("No game found with id {}".format(uuid))
    lines = game.get_lines()
    inactive_cases = [
        i for i, case in enumerate(game.big_board) if case != game.Case.EMPTY_CASE
    ]
    return render(
        request,
        "supermorpion.html",
        {
            "lines": lines,
            "player": player,
            "uuid": uuid,
            "id": game.id,
            "next_case": game.big_case_to_str(),
            "next_player": game.player,
            "inactive_cases": inactive_cases,
            "last_big_case": game.last_big_case,
            "last_line_case": game.last_line_case,
            "last_case": game.last_case,
            "finished": game.game_finished(),
            "game_owner": game.game_owner(),
        },
    )


def rules(request):
    return render(request, "rules.html")


def credits_view(request):
    return render(request, "credits.html")


def legals(request):
    return render(request, "legals.html")
