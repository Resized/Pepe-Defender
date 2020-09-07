import os
import random
import discord
from discord.ext import commands
import requests

from utils import play_sound, save_obj, load_obj, get_filename_from_cd


class Sounds(commands.Cog):
    location = 'cogs/sounds/'
    clips_volume = dict()

    def __init__(self, bot):
        self.bot = bot
        try:
            self.clips_volume = load_obj('clips_volume')
        except FileNotFoundError:
            print('file doesnt exist')

    @commands.command(name='clip', help='Plays a sound clip')
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
        description = ', '.join(sorted(available_clips))
        description += '.'
        embed.description = description
        await ctx.channel.send(embed=embed)

    @commands.command(name='addclip', help='Add sound clip (mp3 < 250kb)')
    async def addclip(self, ctx):
        attachment_url = ctx.message.attachments[0].url
        r = requests.get(attachment_url, allow_redirects=True)
        if int(r.headers.get('content-length')) > 250000:
            await ctx.channel.send('File is too heavy (over 250kb)')
            return
        elif r.headers.get('content-type') != 'audio/mpeg':
            await ctx.channel.send('File is not an mp3.')
            return
        filename = (get_filename_from_cd(r.headers.get('content-disposition'))).lower()
        try:
            open(self.location + filename, 'wb').write(r.content)
            await ctx.channel.send(f'{filename} has been added to sound clips as {filename[:-4]}.')
        except OSError:
            await ctx.channel.send(f'An error occurred, {filename} has not be added. ')

    @commands.command(name='removeclip', help='Removes a clip')
    async def removeclip(self, ctx, clipname):
        if (clipname + '.mp3').lower() in os.listdir(self.location):
            os.replace(rf'{self.location}{clipname}.mp3', rf'cogs/deletedsounds/{clipname}.mp3')
            await ctx.channel.send(f'{clipname} has been removed.')

    @commands.command(name='renameclip', help='Renames a clip')
    async def renameclip(self, ctx, clipname: str, newname: str):
        if (clipname + '.mp3').lower() in os.listdir(self.location):
            os.rename(rf'{self.location}{clipname}.mp3', rf'{self.location}{newname}.mp3')
            await ctx.channel.send(f'{clipname} has been changed to {newname}.')

    @commands.command(name='setvolume', help='Set clip volume')
    async def setvolume(self, ctx, clipname: str, volume: float):
        if (clipname + '.mp3').lower() in os.listdir(self.location):
            if 1.0 >= volume >= 0.0:
                self.clips_volume[clipname] = volume
                save_obj(self.clips_volume, 'clips_volume')
            else:
                await ctx.channel.send('Volume must be between 0 and 1.0')
        else:
            await ctx.channel.send(f'Clip named {clipname} does not exist')
        await ctx.channel.send(f'Volume of {clipname} changed to {volume}')


def setup(bot):
    bot.add_cog(Sounds(bot))
