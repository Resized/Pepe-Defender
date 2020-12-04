import asyncio
import re
import discord
import os
import pickle5 as pickle

from dotenv import load_dotenv

load_dotenv()

FFMPEG = os.getenv('FFMPEG_LOCATION')
MAX_MP3_LENGTH = 5
sounds_location = 'sounds/'
obj_location = 'obj/'


async def play_sound(bot, channel, sound_clip, volume=1.0):
    to_disconnect = True
    try:
        voice_client = await channel.connect()
    except discord.ClientException:
        voice_client = bot.voice_clients[0]
        to_disconnect = False
    audio_source = discord.FFmpegPCMAudio(source=sound_clip)
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
    with open(f'obj/{name}.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def save_obj_s3(obj, name, bucket):
    save_obj(obj, name)
    bucket.upload_file(f'obj/{name}.pkl', f'obj/{name}.pkl')


def load_obj(name):
    with open(f'obj/{name}.pkl', 'rb') as f:
        return pickle.load(f)


def load_obj_s3(name, bucket):
    bucket.download_file(f'obj/{name}.pkl', f'obj/{name}.pkl')
    return load_obj(name)
