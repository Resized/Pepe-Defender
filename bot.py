# bot.py
import os
import random
import discord
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PAZRIM = int(os.getenv('PAZRIM'))
RESIZED = int(os.getenv('RESIZED'))
GENERAL_CHANNEL = int(os.getenv('GENERAL_CHANNEL'))
AGULEI_ROLE = int(os.getenv('AGULEI_ROLE'))
ESCAPE_ROOM = int(os.getenv('ESCAPE_ROOM'))
isDefendOn = True

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    guild = discord.utils.get(bot.guilds, name=GUILD)


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )


@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.channel.send(response)


@bot.event
async def on_typing(channel, user, when):
    if user.id == PAZRIM:
        await channel.send(user.mention + ' STFU <:DansGame:525949909204205579>')


@bot.event
async def on_member_update(before, after):
    if str(before.status) == "offline" and before.id == PAZRIM:
        if str(after.status) == "online" and before.id == PAZRIM:
            guild = discord.utils.get(bot.guilds, name=GUILD)
            role = guild.get_role(AGULEI_ROLE)
            channel = bot.get_channel(GENERAL_CHANNEL)
            await channel.send(role.mention + ' He has come <:monkaW:675062105996656640>')


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel and member.id == PAZRIM and isDefendOn:
        guild = discord.utils.get(bot.guilds, name=GUILD)
        channel_to_move = discord.utils.find(lambda c: c != after.channel, guild.voice_channels)

        for member in after.channel.members:
            if member.id != PAZRIM:
                await member.move_to(channel_to_move)


@bot.command(name='vanish', help='Moves every user but Pazrim to a secret voice channel')
async def vanish(ctx):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    escape_room = guild.get_channel(ESCAPE_ROOM)
    channel = bot.get_channel(GENERAL_CHANNEL)

    lior = guild.get_member(PAZRIM)
    if lior.voice is not None and lior.voice.channel is not None:
        for member in lior.voice.channel.members:
            if member.id != PAZRIM:
                await member.move_to(escape_room)
        await channel.send('Discord has vanished <:pepeLaugh:672820944166977546>')
    else:
        await channel.send('No reason to vanish 😔')


@bot.command(name='defenceoff', help='Turns off Pazrims auto defence')
async def pazrim_defend_off(ctx):
    global isDefendOn
    isDefendOn = False
    channel = bot.get_channel(GENERAL_CHANNEL)
    await channel.send('Defense is off <:PepeHands:526494198858383361>')


@bot.command(name='defenceon', help='Turns on Pazrims auto defence')
async def pazrim_defend_on(ctx):
    global isDefendOn
    isDefendOn = True
    channel = bot.get_channel(GENERAL_CHANNEL)
    await channel.send('Defense is on <:pepeLaugh:672820944166977546>')


bot.run(TOKEN)
