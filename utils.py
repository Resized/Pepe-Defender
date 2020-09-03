import asyncio
import discord
import os

from dotenv import load_dotenv

load_dotenv()

FFMPEG = os.getenv('FFMPEG_LOCATION')


async def play_sound(bot, channel, sound_clip, volume=1.0):
    print(bot, channel, sound_clip)
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
