from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
import uuid
from .models import Game


class SupermorpionConsumer(WebsocketConsumer):
    def connect(self):
        self.id = self.scope["url_route"]["kwargs"]["id"]
        self.group_name = "morpion_%s" % self.id
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        big_case = int(text_data_json["big_case"])
        line_case = int(text_data_json["line_case"])
        case = int(text_data_json["case"])
        game_id = int(text_data_json["id"])
        player_uuid = uuid.UUID(text_data_json["uuid"])

        game = Game.objects.get(pk=game_id)
        res, new_case_owned, game_owner = game.play(
            big_case, line_case, case, player_uuid
        )

        if res == Game.SUCCESS:
            self.send(
                text_data=json.dumps(
                    {
                        "type": "response",
                        "success": True,
                        "next_case": game.big_case_to_str(),
                    }
                )
            )
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "move",
                    "message": json.dumps(
                        {
                            "type": "announce",
                            "next_player": game.player,
                            "next_case": game.big_case_to_str(),
                            "big_case": big_case,
                            "line_case": line_case,
                            "case": case,
                            "next_big_case": game.case_to_big_case(),
                        }
                    ),
                },
            )
            if new_case_owned != -1:
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "move",
                        "message": json.dumps(
                            {"type": "block", "big_case": new_case_owned,}
                        ),
                    },
                )
            if game_owner != Game.Case.EMPTY_CASE:
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "move",
                        "message": json.dumps(
                            {"type": "finished", "player": game_owner}
                        ),
                    },
                )
        else:
            if res == Game.ERROR_ALREADY_PLAYED:
                msg = "This case is already played"
            elif res == Game.ERROR_BIG_ALREADY_PLAYED:
                msg = "The big case is already played"
            elif res == Game.ERROR_UNKOWN_PLAYER:
                msg = "You are not authorize to play"
            elif res == Game.ERROR_BIG_CASE:
                msg = "You cannot play in this big case"
            elif res == Game.ERROR_WRONG_PLAYER:
                msg = "Not your turn"
            elif res == Game.ERROR_GAME_FINISHED:
                msg = "Game finished"
            else:
                msg = ""
            self.send(
                text_data=json.dumps({"type": "response", "success": False, "msg": msg})
            )

    def move(self, event):
        message = event["message"]
        self.send(text_data=message)
