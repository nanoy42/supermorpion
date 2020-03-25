from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class Game(models.Model):
    class Case(models.IntegerChoices):
        EMPTY_CASE = 0
        X_CASE = 1
        O_CASE = 2

        @classmethod
        def default_big_board(cls):
            return list(cls.EMPTY_CASE for i in range(9))

        @classmethod
        def default_board(cls):
            return list(
                [[cls.EMPTY_CASE for i in range(3)] for j in range(3)] for k in range(9)
            )

    class Player(models.IntegerChoices):
        PLAYER_X = 1
        PLAYER_O = 2

    x_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    o_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    board = ArrayField(
        ArrayField(
            ArrayField(
                models.IntegerField(choices=Case.choices, default=Case.EMPTY_CASE),
                size=3,
            ),
            size=3,
        ),
        size=9,
        default=Case.default_board.__func__(Case),
    )
    big_board = ArrayField(
        models.IntegerField(choices=Case.choices, default=Case.EMPTY_CASE),
        size=9,
        default=Case.default_big_board.__func__(Case),
    )
    last_big_case = models.IntegerField(null=True, default=-1)
    last_line_case = models.IntegerField(null=True, default=-1)
    last_case = models.IntegerField(null=True, default=-1)
    player = models.IntegerField(choices=Player.choices, default=Player.PLAYER_X)

    SUCCESS = 0
    ERROR_BIG_CASE = 1
    ERROR_UNKOWN_PLAYER = 2
    ERROR_WRONG_PLAYER = 3
    ERROR_ALREADY_PLAYED = 4
    ERROR_BIG_ALREADY_PLAYED = 5
    ERROR_GAME_FINISHED = 6

    def case_owner(self, case_number):
        if 0 <= case_number <= 8:
            case = self.board[case_number]
            if (case[0][0] == case[0][1] == case[0][2]) and case[0][
                0
            ] != self.Case.EMPTY_CASE:
                return case[0][0]
            elif (case[1][0] == case[1][1] == case[1][2]) and case[1][
                0
            ] != self.Case.EMPTY_CASE:
                return case[1][0]
            elif (case[2][0] == case[2][1] == case[2][2]) and case[2][
                0
            ] != self.Case.EMPTY_CASE:
                return case[2][0]
            elif (case[0][0] == case[1][0] == case[2][0]) and case[0][
                0
            ] != self.Case.EMPTY_CASE:
                return case[0][0]
            elif (case[0][1] == case[1][1] == case[2][1]) and case[0][
                1
            ] != self.Case.EMPTY_CASE:
                return case[0][1]
            elif (case[0][2] == case[1][2] == case[2][2]) and case[0][
                2
            ] != self.Case.EMPTY_CASE:
                return case[0][2]
            elif (case[0][0] == case[1][1] == case[2][2]) and case[0][
                0
            ] != self.Case.EMPTY_CASE:
                return case[0][0]
            elif (case[0][2] == case[1][1] == case[2][0]) and case[0][
                2
            ] != self.Case.EMPTY_CASE:
                return case[0][2]
            else:
                return self.Case.EMPTY_CASE

    def game_owner(self):
        if (
            self.big_board[0] == self.big_board[1] == self.big_board[2]
        ) and self.big_board[0] != self.Case.EMPTY_CASE:
            return self.big_board[0]
        elif (
            self.big_board[3] == self.big_board[4] == self.big_board[5]
        ) and self.big_board[3] != self.Case.EMPTY_CASE:
            return self.big_board[3]
        elif (
            self.big_board[6] == self.big_board[7] == self.big_board[8]
        ) and self.big_board[6] != self.Case.EMPTY_CASE:
            return self.big_board[6]
        elif (
            self.big_board[0] == self.big_board[3] == self.big_board[6]
        ) and self.big_board[0] != self.Case.EMPTY_CASE:
            return self.big_board[0]
        elif (
            self.big_board[1] == self.big_board[4] == self.big_board[7]
        ) and self.big_board[1] != self.Case.EMPTY_CASE:
            return self.big_board[1]
        elif (
            self.big_board[2] == self.big_board[5] == self.big_board[8]
        ) and self.big_board[3] != self.Case.EMPTY_CASE:
            return self.big_board[2]
        elif (
            self.big_board[0] == self.big_board[4] == self.big_board[8]
        ) and self.big_board[0] != self.Case.EMPTY_CASE:
            return self.big_board[0]
        elif (
            self.big_board[2] == self.big_board[4] == self.big_board[6]
        ) and self.big_board[2] != self.Case.EMPTY_CASE:
            return self.big_board[2]
        else:
            return self.Case.EMPTY_CASE

    def game_finished(self):
        return self.game_owner() != self.Case.EMPTY_CASE

    def is_full(self, big_case):
        for i in range(3):
            for j in range(3):
                if self.board[big_case][i][j] == self.Case.EMPTY_CASE:
                    return False
        return True

    def case_to_big_case(self):
        if self.last_big_case != -1:
            big_case = 3 * self.last_line_case + self.last_case
            if self.big_board[big_case] != self.Case.EMPTY_CASE or self.is_full(
                big_case
            ):
                return -2
            return big_case
        else:
            return 4

    def play(self, big_case, line_case, case, player_uuid):
        if player_uuid == self.x_uuid:
            player = self.Player.PLAYER_X
        elif player_uuid == self.o_uuid:
            player = self.Player.PLAYER_O
        else:
            return self.ERROR_UNKOWN_PLAYER, -1, self.Case.EMPTY_CASE

        if self.game_finished():
            return self.ERROR_GAME_FINISHED, -1, self.Case.EMPTY_CASE

        if player != self.player:
            return self.ERROR_WRONG_PLAYER, -1, self.Case.EMPTY_CASE

        next_big_case = self.case_to_big_case()
        if big_case != next_big_case and next_big_case > -1:
            return self.ERROR_BIG_CASE, -1, self.Case.EMPTY_CASE

        if self.board[big_case][line_case][case] != self.Case.EMPTY_CASE:
            return self.ERROR_ALREADY_PLAYED, -1, self.Case.EMPTY_CASE

        if self.big_board[big_case] != self.Case.EMPTY_CASE:
            return self.ERROR_BIG_ALREADY_PLAYED, -1, self.Case.EMPTY_CASE

        self.board[big_case][line_case][case] = player
        new_case_owner = self.case_owner(big_case)
        self.big_board[big_case] = new_case_owner
        if new_case_owner != self.Case.EMPTY_CASE:
            res2 = big_case
        else:
            res2 = -1
        self.last_big_case = big_case
        self.last_line_case = line_case
        self.last_case = case
        if player == self.Player.PLAYER_X:
            self.player = self.Player.PLAYER_O
        else:
            self.player = self.Player.PLAYER_X
        self.save()
        return self.SUCCESS, res2, self.game_owner()

    def get_lines(self):
        res = []
        for i in range(9):
            if i >= 6:
                offset = 6
            elif i >= 3:
                offset = 3
            else:
                offset = 0
            line = (
                [self.board[offset][i % 3][c] for c in range(3)]
                + [self.board[offset + 1][i % 3][c] for c in range(3)]
                + [self.board[offset + 2][i % 3][c] for c in range(3)]
            )
            res.append(line)
        return res

    def print(self):
        for line in self.get_lines():
            line_print = ""
            for char in line:
                if char == self.Case.EMPTY_CASE:
                    line_print += "-"
                elif char == self.Case.X_CASE:
                    line_print += "X"
                else:
                    line_print += "O"
            print(line_print)

    def big_case_to_str(self):
        next_big_case = self.case_to_big_case()
        res = ""
        if next_big_case == -2:
            res = "any case"
        elif next_big_case == 0:
            res = "the upper-left case"
        elif next_big_case == 1:
            res = "the upper-middle case"
        elif next_big_case == 2:
            res = "the upper-right case"
        elif next_big_case == 3:
            res = "the middle-left case"
        elif next_big_case == 4 or next_big_case == -1:
            res = "the central case"
        elif next_big_case == 5:
            res = "the middle-right case"
        elif next_big_case == 6:
            res = "the lower-left case"
        elif next_big_case == 7:
            res = "the lower-middle case"
        elif next_big_case == 8:
            res = "the lower-right case"
        return res
