# bot.py
import os
import random
import discord
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
# 305730826266607616 Resized
# 202825823974064129 Pazrim
PAZRIM = 202825823974064129
RESIZED = 305730826266607616
GENERAL_CHANNEL = 352519274117595136
AGULEI_ROLE = 494285611063181332

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
            await channel.send(role.mention + ' He has come <:monkaW:748581021376839783>')


@bot.event
async def on_voice_state_update(member, before, after):

    if before.channel != after.channel and member.id == PAZRIM:
        guild = discord.utils.get(bot.guilds, name=GUILD)
        channel_to_move = discord.utils.find(lambda c: c != after.channel, guild.voice_channels)

        for member in after.channel.members:
            if member.id != PAZRIM:
                await member.move_to(channel_to_move)


@bot.command(name='vanish', help='Moves every user but Pazrim to a secret voice channel')
async def vanish(ctx):


bot.run(TOKEN)
