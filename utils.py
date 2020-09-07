import asyncio
import pickle
import re
import discord
import os

from dotenv import load_dotenv

load_dotenv()

FFMPEG = os.getenv('FFMPEG_LOCATION')
location = 'cogs/sounds/'


async def play_sound(bot, channel, sound_clip, volume=1.0):
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


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        f.close()


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
