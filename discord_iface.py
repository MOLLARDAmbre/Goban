import discord
from datetime import datetime
from goban import Goban, Stone
from parser import *
from enum import IntEnum

class GameState(IntEnum):
    NOT_STARTED = 0
    STARTED = 1
    SCORING = 2

class Iface:
    def __init__(self, client):
        self.client = client
        self.game_state = GameState.NOT_STARTED
        self.goban = None
        self.scorer = None
        self.current_player = Stone.BLACK
        self.channel = None
        self.consecutive_passes = 0

    def change_player(self):
        if (self.current_player == Stone.BLACK):
            self.current_player = Stone.WHITE
        else:
            self.current_player = Stone.BLACK

    async def pass_turn(self, passed):
        if passed:
            self.consecutive_passes += 1
        else:
            self.consecutive_passes = 0
        if self.consecutive_passes >= 2:
            self.consecutive_passes = 0
            if self.game_state == GameState.STARTED:
                from scorer import Scorer
                self.scorer = Scorer(self.goban)
                self.game_state = GameState.SCORING
            else:
                await self.end()

    async def start(self, size):
        size = int(size[1:-1])
        if (size >= 2):
            g = Goban(size)
            self.goban = g
            self.scorer = None
            self.game_state = GameState.STARTED
            await self.update()
        else:
            await self.channel.send("Please select at least a goban of size 2")

    async def clear(self):
        messages = await self.channel.history().flatten()
        await self.channel.delete_messages(messages)

    async def end(self):
        self.goban = None
        await self.clear()
        await self.update()
        await self.channel.send(self.scorer.count_territory())
        self.scorer = None
        self.game_state = GameState.NOT_STARTED

    async def play(self, command):
        success, passed = parse_command(command, self.goban, self.current_player)
        if success:
            self.change_player()
        else:
            await self.bad_move()
        await self.pass_turn(passed)
        if self.game_state != GameState.NOT_STARTED:
            await self.update()

    async def kill(self, command):
        passed = parse_kill(command, self.scorer)
        await self.pass_turn(passed)
        await self.update()

    async def bad_move(self):
        await self.channel.send("Illegal move, please try again")

    async def bad_command(self):
        await self.channel.send("Bad command, please verify it. You can also type '!help' to get some help")

    async def help(self):
        await self.channel.send("Welcome to Goban bot. \n\
        To launch a game, please use '!start(n)' with n the size of the goban you want, \n\
        To play a move, please alternate witht he other player using '!play(a, b)' with a the ord and b the abs values of your moves \n\
        Once you both passed (with !pass), please use 'kill(a, b)' to mark groups as dead. If you make a mistake, reusing the command on a dead group will make it rise back from the deads. \n\
        One you are done, please just pass (with !pass). This will compute the scores and end the game.")

    async def update(self):
        await self.clear()
        if self.game_state == GameState.STARTED:
            self.goban.display()
        if self.game_state == GameState.SCORING:
            await self.channel.send("Please tag dead groups with 'kill'")
            self.scorer.prepare_all_scores()
            self.scorer.display()
        await self.channel.send(file=discord.File("temp.png"))

client = discord.Client()

interface = Iface(client)

@client.event
async def on_ready():
    interface.channel = interface.client.get_channel(760822648920866832)
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!start') and interface.game_state == GameState.NOT_STARTED:
        await interface.start(message.content[6:])
    elif message.content.startswith('!display') and interface.game_state == GameState.STARTED:
        await interface.update()
    elif message.content.startswith('!display') and interface.game_state == GameState.SCORING:
        await interface.kill("pass")
    elif message.content.startswith('!pass') and interface.game_state != GameState.NOT_STARTED:
        await interface.play("pass")
    elif message.content.startswith('!play') and interface.game_state == GameState.STARTED:
        await interface.play(message.content[5:])
    elif message.content.startswith('!kill') and interface.game_state == GameState.SCORING:
        await interface.kill(message.content[5:])
    # elif message.content.startswith('!end'):
    #     await interface.save()
    # elif message.startswith('!load'):
    #     await interface.load()
    elif message.content.startswith('!help'):
        await interface.help()
    else:
        await interface.bad_command()


client.run('Your token here')
