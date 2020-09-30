from goban import Goban, Stone
from enum import IntEnum

def parse_command(command, goban, player):
    if (command == "pass"):
        return True, True
    command = command[1:-1].split(', ')
    command = [int(command[0]), int(command[1])]
    if (goban.play(command, player)):
        return True, False
    return False, False


def parse_kill(command, goban):
    if (command == "pass"):
        return True
    command = command[1:-1].split(', ')
    command = [int(command[0]), int(command[1])]
    goban.kill(command)
    goban.prepare_all_scores()
    goban.display()
    goban.reset_scores()
    return False
