import os
import random
import discord
from discord.ext import commands

from utils import play_sound


class Sounds(commands.Cog):
    location = 'cogs/sounds/'

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clip', help='')
    async def clip(self, ctx, filename, volume: float = 1.0):
        volume = min(1.0, volume)
        sound_clip = f'{self.location}{filename}.mp3'
        if filename == 'gravity':
            volume *= 0.3
        elif filename == 'rakdanim':
            volume *= 0.4
        elif filename == 'fart':
            volume *= 0.5
            fart_clips = []
            for fname in os.listdir(self.location):
                if fname.startswith('fart'):
                    fart_clips.append(fname)
            selected_clip = random.choice(fart_clips)
            sound_clip = f'{self.location}{selected_clip}'

        current_room = ctx.message.author.voice.channel
        await play_sound(self.bot, current_room, sound_clip, volume)


def setup(bot):
    bot.add_cog(Sounds(bot))
