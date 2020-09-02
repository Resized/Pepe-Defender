# bot.py
import asyncio
import os
import random
import discord
import aiohttp
import json
import typing
import logging

from discord.ext.commands import BadArgument
from dotenv import load_dotenv

from discord.ext import commands

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
isDefendOn = False

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    game = discord.Game(name="with my balls")
    await bot.change_presence(status=discord.Status.online, activity=game)


"""
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
        message = await channel.send(user.mention + ' STFU <:DansGame:525949909204205579>', delete_after=10)


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

    lior = guild.get_member(PAZRIM)
    if lior.voice is not None and lior.voice.channel is not None:
        for member in lior.voice.channel.members:
            if member.id != PAZRIM:
                await member.move_to(escape_room)
        await ctx.channel.send('Discord has vanished <:pepeLaugh:672820944166977546>')
    else:
        await ctx.channel.send('No reason to vanish 😔')


@bot.command(name='defenceoff', help='Turns off Pazrims auto defence')
async def pazrim_defend_off(ctx):
    global isDefendOn
    isDefendOn = False
    await ctx.channel.send('Defense is off <:PepeHands:526494198858383361>')


@bot.command(name='defenceon', help='Turns on Pazrims auto defence')
async def pazrim_defend_on(ctx):
    global isDefendOn
    isDefendOn = True
    await ctx.channel.send('Defense is on <:pepeLaugh:672820944166977546>')
"""


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


@bot.command(name='clear', help='Clears last number of messages (can specify by specific user)')
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
    async for message in ctx.channel.history(limit=10):
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
        display_name_list.append(member.display_name)
    num_users = len(display_name_list)
    random.shuffle(display_name_list)
    team_1 = ', '.join(display_name_list[:num_users // 2])
    team_2 = ', '.join(display_name_list[num_users // 2:])
    embed.description = 'Team A:\n\t' + team_1 + '\n\n' + 'Team B:\n\t' + team_2
    await ctx.channel.send(embed=embed)


@bot.command(
    name='gravity',
    description='Plays a gravity voice clip in the voice channel')
async def gravity(ctx, volume=1.0):
    if volume > 1.0:
        volume = 1.0
    volume *= 0.3
    # grab the user who sent the command
    user = ctx.message.author

    # only play music if user is in a voice channel
    try:
        voice_channel = user.voice.channel
    except AttributeError:
        await ctx.channel.send('User is not in a channel.')
        return
    # create StreamPlayer
    voice_client = await voice_channel.connect()
    audio_source = discord.FFmpegPCMAudio(executable=FFMPEG, source="gravity.mp3")
    audio_source = discord.PCMVolumeTransformer(audio_source, volume)
    voice_client.play(audio_source)
    # disconnect after the player has finished
    while voice_client.is_playing():
        await asyncio.sleep(0.5)
    voice_client.stop()
    await voice_client.disconnect()


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
    pass


@bot.event
async def on_voice_state_update(member, before, after):
    time_to_move = 30
    game_list = ["VALORANT", "Counter-Strike: Global Offensive"]
    if member.id == BENCHUK and before.self_mute is False and after.self_mute is True \
            and before.self_deaf is False and after.self_deaf is False and member.activity \
            and member.activity.name in game_list:
        while time_to_move > 0:
            if after.self_mute is False or after.self_deaf is True:
                return
            time_to_move -= 1
            await asyncio.sleep(1)
            if time_to_move == 0:
                current_room = member.voice.channel
                await play_sound(current_room, "tzirman3.mp3", 1)
                time_to_move = 60


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


@bot.command(name='fart')
async def fart(ctx, volume: float = 0.5):
    volume = min(1.0, volume)
    volume *= 0.5
    farts = [
        'fart-01.mp3',
        'fart-02.mp3',
        'fart-03.mp3',
        'fart-04.mp3',
        'fart-05.mp3',
        'fart-06.mp3',
        'fart-07.mp3',
        'fart-08.mp3',
        'fart-squeak-01.mp3',
        'fart-squeak-02.mp3',
        'fart-squeak-03.mp3'
    ]
    fart_sound = random.choice(farts)
    current_room = ctx.message.author.voice.channel
    await play_sound(current_room, fart_sound, 0.5)


@bot.command(name='rakdanim', help='')
async def rakdanim(ctx, volume: float = 1.0):
    volume = min(1.0, volume)
    volume *= 0.5
    rakdan = 'rikigalweakness3.mp3'
    current_room = ctx.message.author.voice.channel
    await play_sound(current_room, rakdan, volume)


@bot.command(name='shit', help='Shieeeeeeeeeeeeeeeeeeeeeeeeeeeet')
async def shit(ctx, volume: float = 1.0):
    volume = min(1.0, volume)
    shit_clip = 'Shiiiit.mp3'
    current_room = ctx.message.author.voice.channel
    await play_sound(current_room, shit_clip, volume)


@bot.command(name='nice', help='Michael Rosen: Noice')
async def nice(ctx, volume: float = 1.0):
    volume = min(1.0, volume)
    shit_clip = 'click-nice.mp3'
    current_room = ctx.message.author.voice.channel
    await play_sound(current_room, shit_clip, volume)


@bot.command(name='crickets', help='Michael Rosen: Noice')
async def crickets(ctx, volume: float = 1.0):
    volume = min(1.0, volume)
    shit_clip = 'crickets.mp3'
    current_room = ctx.message.author.voice.channel
    await play_sound(current_room, shit_clip, volume)


@bot.command(name='connect', help='Join current voice channel')
async def connect(ctx):
    """channel = ctx.message.author.voice.channel
    member = bot.get_member(748511798831087667)
    try:
        await channel.connect()
    except discord.ClientException:
        await member.move_to(ctx.message.author.voice.channel)"""
    guild = ctx.guild
    author: discord.Member = ctx.author
    voice_client: discord.VoiceClient = guild.voice_client
    channel: discord.VoiceChannel = author.voice.channel
    if not voice_client:
        vc = await channel.connect()
        return vc
    elif voice_client.channel != channel:
        print('im here')
        return await voice_client.move_to(channel)
    return voice_client


@bot.command(name='disconnect', help='Join current voice channel')
async def disconnect(ctx):
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
    # \U0001f1e6 A
    # \U0001f1e7 B
    await ctx.channel.send(translated)


async def play_sound(channel, sound_clip, volume=1.0):
    to_disconnect = True
    try:
        voice_client = await channel.connect()
    except discord.ClientException:
        voice_client = bot.voice_clients[0]
        to_disconnect = False
    audio_source = discord.FFmpegPCMAudio(executable=FFMPEG, source=sound_clip)
    audio_source = discord.PCMVolumeTransformer(audio_source, volume)
    voice_client.play(audio_source)
    while voice_client.is_playing():
        await asyncio.sleep(0.5)
    if to_disconnect:
        voice_client.stop()
        await voice_client.disconnect()


bot.run(TOKEN)
