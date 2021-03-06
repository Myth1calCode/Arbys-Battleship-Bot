import discord
from discord.ext import commands
import bge
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return "Arby's Battleship Bot is currently online!"

def run():
  app.run(host="0.0.0.0", port=8000)

def keep_alive():
  server = Thread(target=run)
  server.start()

GAME = bge.start_game()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
BOARD = GAME.show_board()

Client = discord.Client()

bot_prefix = "^"

bot = commands.Bot(command_prefix=bot_prefix)

GAME_START = 'Let The Game Begin!'
INSTRUCTIONS1 = 'A game of battleships is about to begin'
INSTRUCTIONS2 = 'An 6X6 board with 3 ships on it will be created'
INSTRUCTIONS3 = "You'll have to select a row and a column to shoot at every " \
                "turn until you sink all 3 ships."


@bot.event
async def on_ready():
    """
    prints messages to console when bot is activated
    :return: None
    """
    await bot.change_presence(activity=discord.Streaming(name='Battleship', url='https://www.twitch.tv/search?term=Battleship'))
    print('Bot started successfully!')


@bot.event
async def on_member_join(member):
    """
    Whenever a new memeber joins the channel, the bot welcomes him in a DM
    channel
    :param member: a new member joining the channel
    :return: None
    """
    await member.create_dm()
    await member.dm_channel.send(
        f"Hi {member.name}, welcome to Memeing about Arby's! Type '^play' to "
        f"start a game of Battleship."
    )


@bot.command(name='play')
async def start_game(ctx):
    """
    Waits for the start_game command and when this command is sent by a
    member in the channel, the bot starts a new battleships game in a DM
    channel with the member
    :param ctx: context
    :return: None
    """
    author = ctx.message.author
    if author == bot.user:
        return

    await author.create_dm()
    await ctx.author.dm_channel.send(GAME_START)
    await ctx.author.dm_channel.send(INSTRUCTIONS1)
    await ctx.author.dm_channel.send(INSTRUCTIONS2)
    await ctx.author.dm_channel.send(INSTRUCTIONS3)
    for row in BOARD:
        await ctx.author.dm_channel.send(row)


@bot.command()
async def shoot(ctx, row: int, column: int):
    """
    attempts to shoot at a given coordiantes
    :param ctx: context
    :param row: the row to target
    :param column: the column to target
    :return: None
    """
    author = ctx.message.author
    if author == bot.user:
        return
    try:
        await ctx.author.dm_channel.send(GAME.shoot(row - 1, column - 1))

        for row in BOARD:
            await ctx.author.dm_channel.send(row)
        g_on = GAME.check_victory()
        if GAME.game_over:
            await ctx.author.dm_channel.send(g_on)
        else:
            await ctx.author.dm_channel.send(g_on)
    except IndexError:
        pass


@bot.command()
async def stats(ctx):
    """
    Sends a message to the user giving him current game stats such as number of
    turns, number of hits and number of misses.
    :param ctx: context
    :return: None
    """
    author = ctx.message.author
    if author == bot.user:
        return
    s = GAME.game_stats()
    for stat in s:
        await ctx.author.dm_channel.send(stat)


@bot.command()
async def surrender(ctx):
    """
    A command that can be used by a user when playing and wanting the game
    to stop
    :param ctx:context
    :return: None
    """
    author = ctx.message.author
    if author == bot.user:
        return
    GAME.game_over = True
    await ctx.author.dm_channel.send('Game was surrendered. To start a '
                                     'new game please type ^start_game '
                                     'in the general text channel.')


@bot.command()
async def info(ctx):
    """
    General info about the author of the bot and the bot itself.
    :param ctx: context
    :return: None
    """
    embed = discord.Embed(title="Battle Ships Bot",
                          description="a bot the lets you play the Battle "
                                      "Ships game in a DM channel in Discord",
                          color=0xeee657)

    # give info about you here
    embed.add_field(name="Daniel Walters", value="<Kishkashta>")

    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    # give users a link to invite this bot to their server
    embed.add_field(name="Invite",
                    value="<https://discordapp.com/api/oauth2/authorize?client_id=700061008693166229&permissions=0&scope=bot>")

    await ctx.send(embed=embed)


# removing the built-in help function since we want to build a new one.
bot.remove_command('help')


@bot.command()
async def help(ctx):
    """
    an explanation about all the possible commands that the member is able
    to use to communicate with the bot
    :param ctx: context
    :return: None
    """
    embed = discord.Embed(title="Battle Ships Bot",
                          description="a bot the lets you play the Battle "
                                      "Ships game in a DM channel in Discord",
                          color=0xeee657)

    embed.add_field(name="^start_game", value="bot creates a dm channel and "
                                              "starts a battle ship game",
                    inline=False)
    embed.add_field(name="^shoot X Y", value="Bot shoots the given "
                                             "coordinates", inline=False)
    embed.add_field(name="^stats", value="Gives stats about current game, "
                                         "number of turns, hits and misses",
                    inline=False)
    embed.add_field(name="^surrender", value="surrenders and stops a current "
                                             "game session", inline=False)
    embed.add_field(name="^info", value="Gives a little info about the bot",
                    inline=False)
    embed.add_field(name="^help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)

keep_alive()
bot.run(TOKEN)
