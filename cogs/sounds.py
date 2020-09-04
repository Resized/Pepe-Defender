import os
import random
import discord
from discord.ext import commands

from utils import play_sound


class Sounds(commands.Cog):
    location = 'cogs/sounds/'
    clips_volume = {'gravity': 0.3,
                    'rakdanim': 0.4,
                    'missionfailed': 0.2,
                    'fart': 0.5,
                    'oof': 0.5,
                    'wow': 0.5,
                    'sadviolin': 0.3}

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clip', help='<filename> [volume=1.0]')
    async def clip(self, ctx, filename, volume: float = 1.0):
        volume = min(1.0, volume)
        sound_clip = f'{self.location}{filename}.mp3'
        if filename in self.clips_volume.keys():
            volume *= self.clips_volume.get(filename)
        if filename == 'fart':
            fart_clips = []
            for fname in os.listdir(self.location):
                if fname.startswith('fart'):
                    fart_clips.append(fname)
            selected_clip = random.choice(fart_clips)
            sound_clip = f'{self.location}{selected_clip}'

        current_room = ctx.message.author.voice.channel
        await play_sound(self.bot, current_room, sound_clip, volume)

    @commands.command(name='clips', help='Shows available sound clips')
    async def clips(self, ctx):
        embed = discord.Embed(title='Available sound clips:', colour=discord.Colour.blue())
        available_clips = []
        for filename in os.listdir(self.location):
            if filename.endswith('.mp3'):
                if not filename.startswith('fart'):
                    available_clips.append(filename[:-4])
        available_clips.append('fart')
        description = ', '.join(available_clips)
        description += '.'
        embed.description = description
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Sounds(bot))
