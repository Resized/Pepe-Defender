# bot.py
import asyncio
import json
import logging
import os
import random
import typing

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BadArgument
from dotenv import load_dotenv

from utils import play_sound, sounds_location

load_dotenv()
logging.basicConfig(level=logging.WARNING)

# global vars
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GIPHY = os.getenv('GIPHY_API')
PAZRIM = int(os.getenv('PAZRIM'))
RESIZED = int(os.getenv('RESIZED'))
BENCHUK = int(os.getenv('BENCHUK'))
GENERAL_CHANNEL = int(os.getenv('GENERAL_CHANNEL'))
AGULEI_ROLE = int(os.getenv('AGULEI_ROLE'))
ESCAPE_ROOM = int(os.getenv('ESCAPE_ROOM'))
FFMPEG = os.getenv('FFMPEG_LOCATION')
S3_BUCKET = os.getenv('S3_BUCKET')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


isDefendOn = False

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    game = discord.Game(name="with my balls")

    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.command(help='Picks a random gif from the top 10 results and posts it')
async def giphy(ctx, *, search=None):
    embed = discord.Embed(colour=discord.Colour.blue())
    session = aiohttp.ClientSession()

    if search is None:
        response = await session.get('https://api.giphy.com/v1/gifs/random?api_key=' + GIPHY)
        data = json.loads(await response.text())
        embed.set_image(url=data['data']['images']['original']['url'])
    else:
        search.replace(' ', '+')
        response = await session.get(
            'http://api.giphy.com/v1/gifs/search?q=' + search + '&api_key=' + GIPHY + '&limit=10')
        data = json.loads(await response.text())
        total_results = data.get('pagination').get('total_count')
        max_rand = 10
        if total_results < 10:
            max_rand = total_results
        if total_results <= 0:
            await ctx.channel.send('No GIFs found for ' + search)
            await session.close()
            return
        gif_choice = random.randint(0, max_rand - 1)
        embed.set_image(url=data['data'][gif_choice]['images']['original']['url'])

    await session.close()
    await ctx.channel.send(embed=embed)


@bot.command(name='clear', help='Clears last messages out of 20 (can specify by specific user)')
async def message_clear(ctx, amount: typing.Optional[int] = 1, username=''):
    user = ''
    counter = 0
    if username != '':
        try:
            user = await commands.MemberConverter().convert(ctx, username)
        except BadArgument:
            await ctx.channel.send('Found no user named ' + username)
            return
    await ctx.message.delete()
    messages_to_delete = []
    async for message in ctx.channel.history(limit=20):
        if amount <= 0:
            break
        if user is not None and user != '':
            if message.author == user:
                messages_to_delete.append(message)
                amount -= 1
                counter += 1
        elif user == '':
            messages_to_delete.append(message)
            amount -= 1
            counter += 1
    await ctx.channel.delete_messages(messages_to_delete)
    if username == '':
        await ctx.channel.send(ctx.message.author.name + ' successfully removed last ' + str(counter) + ' messages.')
    else:
        await ctx.channel.send(
            ctx.message.author.name + ' successfully removed ' + username + "'s last " + str(counter) + ' messages.')


@bot.command(name='teams', help='Generate 2 random teams for uses in voice channel')
async def gen_teams(ctx):
    embed = discord.Embed(title='Team Generator', colour=discord.Colour.blue())
    user_list = ctx.author.voice.channel.members
    display_name_list = []
    for member in user_list:
        if not member.bot:
            display_name_list.append(member.display_name)
    num_users = len(display_name_list)
    random.shuffle(display_name_list)
    team_1 = ', '.join(display_name_list[:num_users // 2])
    team_2 = ', '.join(display_name_list[num_users // 2:])
    embed.description = 'Team A:\n\t' + team_1 + '\n\n' + 'Team B:\n\t' + team_2
    await ctx.channel.send(embed=embed)


@bot.command(name='msg_count', help='msg_count [username] [search_limit]')
async def msg_count(ctx, username=None, limit: typing.Optional[int] = None):
    member = None
    if username is not None:
        try:
            member = await commands.MemberConverter().convert(ctx, username)
        except BadArgument:
            await ctx.channel.send('Found no user named ' + username)
            return
    counter = 0
    global_counter = 0
    async for message in ctx.channel.history(limit=limit):
        if message.author == member:
            counter += 1
        global_counter += 1
    if member is not None:
        await ctx.channel.send(
            '{0} has typed {1} messages out of {2} in {3} channel.'.format(username, counter, global_counter,
                                                                           ctx.channel.name))
    else:
        await ctx.channel.send('{0} messages has been typed in {1} channel.'.format(global_counter, ctx.channel.name))


@bot.command(name='msg_stats', help='Generate 2 random teams for uses in voice channel')
async def msg_stats(ctx, limit: typing.Optional[int] = None):
    message_dict = {}
    embed = discord.Embed(title='Message Stats', colour=discord.Colour.blue())
    async for message in ctx.channel.history(limit=limit):
        if message.author.name not in message_dict:
            message_dict[message.author.name] = 1
        else:
            message_dict[message.author.name] += 1
    embed.description = ''
    messages_sorted = sorted(message_dict.items(), key=lambda x: x[1], reverse=True)
    for message in messages_sorted:
        embed.description += '{0}: {1}\n'.format(message[0], message[1])
    await ctx.channel.send(embed=embed)


@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
    if member.id == PAZRIM and before.channel is None \
            and after.channel is not None:
        await play_sound(bot, member.voice.channel, f'{sounds_location}ohno.mp3', 0.5)
        return
    time_to_move = 60
    game_list = ["VALORANT", "Counter-Strike: Global Offensive"]
    if member.id == BENCHUK and before.self_mute is False and after.self_mute is True \
            and before.self_deaf is False and after.self_deaf is False and member.activity \
            and member.activity.name in game_list:
        while time_to_move > 0:
            if after.self_mute is False or after.self_deaf is True:
                return
            time_to_move -= 1
            await asyncio.sleep(1)
            if time_to_move <= 0:
                current_room = member.voice.channel
                await play_sound(bot, current_room, f'{sounds_location}tzirman.mp3', 1)
                return


@bot.event
async def on_message(message):
    if message.author.id == PAZRIM:
        num = random.randint(0, 99)
        if num < 20:
            emojis = bot.emojis
            react_emoji = random.choice(emojis)
            await message.add_reaction(react_emoji)
    await bot.process_commands(message)


@bot.command(name='8ball')
async def eight_ball(ctx, *, message=None):
    answers = [
        'It is certain.',
        'It is decidedly so.',
        'Without a doubt.',
        'Yes – definitely.',
        'You may rely on it.',
        'As I see it, yes.',
        'Most likely.',
        'Outlook good.',
        'Yes.',
        'Signs point to yes.',
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        'Don\'t count on it.'
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.'
    ]
    closed_question = ['are', 'is', 'was', 'were', 'does', 'can', 'have', 'has', 'am', 'should', 'do', 'may', 'will',
                       'could', 'would', 'might', 'did', 'fuck']
    if message is None:
        await ctx.channel.send('Type a question you idiot.')
        return
    first_word = message.split(' ')[0]
    if message[-1] != '?' or first_word.lower() not in closed_question:
        await ctx.channel.send('Learn to formulate a question retard.')
        return
    answer = random.choice(answers)
    await ctx.channel.send(answer)


@bot.command(name='join', help='Join current voice channel')
async def join(ctx):
    guild = ctx.guild
    author: discord.Member = ctx.author
    voice_client: discord.VoiceClient = guild.voice_client
    channel: discord.VoiceChannel = author.voice.channel
    if not voice_client:
        vc = await channel.connect()
        return vc
    elif voice_client.channel != channel:
        await voice_client.disconnect()
        return await channel.connect()
    return voice_client


@bot.command(name='leave', help='Leaves voice channel')
async def leave(ctx):
    guild = ctx.guild
    voice_client: discord.VoiceClient = guild.voice_client
    if voice_client:
        await voice_client.disconnect()


@bot.command(name='wave', help='Cycle text in channel')
async def wave(ctx, *, text: str = None):
    if text is None:
        return
    message = await ctx.channel.send(text)
    for i in range(1, len(text) + 1):
        new_text = text[i:]
        new_text += text[:i]
        await message.edit(content=new_text)
        await asyncio.sleep(0.5)


@bot.command(name='eletter')
async def eletter(ctx, *, message: str = None):
    if message is None:
        return
    translated = ''
    first_letter = 'a'
    regional_letters = [
        '\N{Regional Indicator Symbol Letter A}',
        '\N{Regional Indicator Symbol Letter B}',
        '\N{Regional Indicator Symbol Letter C}',
        '\N{Regional Indicator Symbol Letter D}',
        '\N{Regional Indicator Symbol Letter E}',
        '\N{Regional Indicator Symbol Letter F}',
        '\N{Regional Indicator Symbol Letter G}',
        '\N{Regional Indicator Symbol Letter H}',
        '\N{Regional Indicator Symbol Letter I}',
        '\N{Regional Indicator Symbol Letter J}',
        '\N{Regional Indicator Symbol Letter K}',
        '\N{Regional Indicator Symbol Letter L}',
        '\N{Regional Indicator Symbol Letter M}',
        '\N{Regional Indicator Symbol Letter N}',
        '\N{Regional Indicator Symbol Letter O}',
        '\N{Regional Indicator Symbol Letter P}',
        '\N{Regional Indicator Symbol Letter Q}',
        '\N{Regional Indicator Symbol Letter R}',
        '\N{Regional Indicator Symbol Letter S}',
        '\N{Regional Indicator Symbol Letter T}',
        '\N{Regional Indicator Symbol Letter U}',
        '\N{Regional Indicator Symbol Letter V}',
        '\N{Regional Indicator Symbol Letter W}',
        '\N{Regional Indicator Symbol Letter X}',
        '\N{Regional Indicator Symbol Letter Y}',
        '\N{Regional Indicator Symbol Letter Z}']
    for letter in message:
        if letter == ' ':
            translated += '   '
        else:
            letter_to_add = ord(letter.lower()) - ord(first_letter)
            translated += regional_letters[letter_to_add] + ' '
    await ctx.channel.send(translated)


bot.run(TOKEN)
