from goban import Goban, Stone
from enum import IntEnum

def parse_command(goban, player):
    command = input()
    if (command == "pass"):
        return True, True
    command = command[1:-1].split(', ')
    command = [int(command[0]), int(command[1])]
    if (goban.play(command, player)):
        return True, False
    return False, False


def parse_kill(goban):
    command = input()
    if (command == "pass"):
        return True
    command = command[1:-1].split(', ')
    command = [int(command[0]), int(command[1])]
    goban.kill(command)
    goban.prepare_all_scores()
    goban.display()
    goban.reset_scores()
    return False


def run(size, komi=7.5):
    player1 = Stone.BLACK
    player2 = Stone.WHITE
    current_player = player1
    consecutive_passes = 0
    goban = Goban(size, komi=komi)
    while (consecutive_passes < 2):
        success, passed = parse_command(goban, current_player)
        while not success:
            success, passed = parse_command(goban, current_player)
        if passed:
            consecutive_passes += 1
        if not passed:
            consecutive_passes = 0
        if current_player == player1:
            current_player = player2
        else:
            current_player = player1

    goban.display()
    print("Ok, please select dead groups")
    from scorer import Scorer
    scorer = Scorer(goban)
    consecutive_passes = 0
    while (consecutive_passes < 2):
        passed = parse_kill(scorer)
        if passed:
            consecutive_passes += 1
        if not passed:
            consecutive_passes = 0
    print(scorer.count_territory())
    scorer.display()

run(3)
