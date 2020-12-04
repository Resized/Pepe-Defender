import os
import random

import discord
import requests
import boto3
from mutagen.mp3 import MP3

from discord.ext import commands

from utils import play_sound, save_obj_s3, get_filename_from_cd, load_obj_s3, sounds_location, obj_location, \
    MAX_MP3_LENGTH

AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')


class Sounds(commands.Cog):
    clips_volume = dict()
    clips_usage = dict()

    def __init__(self, bot):
        self.bot = bot
        self.s3 = boto3.resource(
            service_name='s3',
            region_name=AWS_DEFAULT_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        try:
            if not os.path.exists(f'{sounds_location}'):
                os.mkdir(f'{sounds_location}')
        except OSError:
            print(f"Creation of the directory {sounds_location} failed")

        try:
            if not os.path.exists(f'{obj_location}'):
                os.mkdir(f'{obj_location}')
        except OSError:
            print(f"Creation of the directory {obj_location} failed")

        # download all missing sound clips from s3 cloud
        for sound_clip in self.s3.Bucket(S3_BUCKET).objects.filter(Prefix=sounds_location):
            if not os.path.exists(f'{sound_clip.key}') and sound_clip.key.split('/')[-1]:
                try:
                    self.s3.Bucket(S3_BUCKET).download_file(f'{sound_clip.key}', f'{sound_clip.key}')
                    print(f'{sound_clip.key.split("/")[-1]} downloaded')
                except FileNotFoundError:
                    print(f'error downloading {sound_clip.key}')

        try:
            self.clips_volume = load_obj_s3('clips_volume', self.s3.Bucket(S3_BUCKET))
        except FileNotFoundError:
            print('clips_volume doesnt exist')
        try:
            self.clips_usage = load_obj_s3('clips_usage', self.s3.Bucket(S3_BUCKET))
        except FileNotFoundError:
            print('clips_usage doesnt exist')

    @commands.command(name='clip', help='Plays a sound clip')
    async def clip(self, ctx, filename, volume: float = 1.0):
        volume = min(1.0, volume)
        sound_clip = f'{sounds_location}{filename}.mp3'
        if filename in self.clips_volume.keys():
            volume *= self.clips_volume.get(filename)
        if filename == 'fart':
            fart_clips = []
            for fname in os.listdir(sounds_location):
                if fname.startswith('fart'):
                    fart_clips.append(fname)
            selected_clip = random.choice(fart_clips)
            sound_clip = f'{sounds_location}{selected_clip}'
        if sound_clip.split("/")[-1] not in os.listdir(sounds_location):
            await ctx.channel.send(f'{filename} clip was not found.')
            return
        current_room = ctx.message.author.voice.channel
        await play_sound(self.bot, current_room, sound_clip, volume)
        self.clips_usage[filename] = self.clips_usage.get(filename, 0) + 1
        save_obj_s3(self.clips_usage, 'clips_usage', self.s3.Bucket(S3_BUCKET))

    @commands.command(name='clips', help='Shows available sound clips')
    async def clips(self, ctx):
        embed = discord.Embed(title='Available sound clips:', colour=discord.Colour.blue())
        available_clips = []
        for filename in os.listdir(sounds_location):
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
        if filename.split('.')[-1] != 'mp3':
            await ctx.channel.send('File is not an mp3.')
            return
        try:
            print(filename)
            open(sounds_location + filename, 'wb').write(r.content)
            audio = MP3(sounds_location + filename)
            if audio.info.length > MAX_MP3_LENGTH:
                await ctx.channel.send(f'❌ `{filename}` exceeds {MAX_MP3_LENGTH} seconds and has not be added. ')
                os.remove(sounds_location + filename)
                return
            self.s3.Bucket(S3_BUCKET).upload_file(f'{sounds_location}{filename}',
                                                  f'sounds/{filename}')
            await ctx.channel.send(f'✅ {filename[:-4]} has been added to sound clips.')
        except OSError:
            await ctx.channel.send(f'❌ An error occurred, {filename} has not be added. ')

    @commands.command(name='removeclip', help='Removes a clip')
    async def removeclip(self, ctx, clipname):
        if (clipname + '.mp3').lower() in os.listdir(sounds_location):
            os.replace(rf'{sounds_location}{clipname}.mp3', rf'cogs/deletedsounds/{clipname}.mp3')
            self.s3.Object(S3_BUCKET, f'{sounds_location}{clipname}.mp3').delete()
            await ctx.channel.send(f'`{clipname}` has been removed.')

    @commands.command(name='renameclip', help='Renames a clip')
    async def renameclip(self, ctx, clipname: str, newname: str):
        if (clipname + '.mp3').lower() in os.listdir(sounds_location):
            os.rename(rf'{sounds_location}{clipname}.mp3', rf'{sounds_location}{newname}.mp3')
            self.s3.Object(S3_BUCKET, f'{sounds_location}{newname}.mp3').copy_from(CopySource=f'{S3_BUCKET}/{sounds_location}{clipname}.mp3')
            self.s3.Object(S3_BUCKET, f'{sounds_location}{clipname}.mp3').delete()
            self.clips_usage[newname] = self.clips_usage.pop(clipname)
            self.clips_volume[newname] = self.clips_volume.pop(clipname, 1)
            save_obj_s3(self.clips_usage, 'clips_usage', self.s3.Bucket(S3_BUCKET))
            save_obj_s3(self.clips_volume, 'clips_volume', self.s3.Bucket(S3_BUCKET))

            await ctx.channel.send(f'✅ `{clipname}` has been changed to `{newname}`.')
        else:
            await ctx.channel.send(f'❌ `{clipname}` was not found.')

    @commands.command(name='setvolume', help='Set clip volume')
    async def setvolume(self, ctx, clipname: str, volume: float):
        previous_volume = self.clips_volume.get(clipname, 1.0)
        if (clipname + '.mp3').lower() in os.listdir(sounds_location):
            if 1.0 >= volume >= 0.0:
                self.clips_volume[clipname] = volume
                save_obj_s3(self.clips_volume, 'clips_volume', self.s3.Bucket(S3_BUCKET))
                await ctx.channel.send(f'Volume of {clipname} changed from {previous_volume} to {volume}')
            else:
                await ctx.channel.send('Volume must be between 0 and 1.0')
        else:
            await ctx.channel.send(f'Clip named {clipname} does not exist')

    @commands.command(name='clip_leaderboards', help='Shows top 10 clips by usage')
    async def clip_leaderboards(self, ctx):
        sorted_clips = sorted(self.clips_usage, key=self.clips_usage.get, reverse=True)
        embed = discord.Embed(title='Clips Leaderboards', colour=discord.Colour.blue())
        description = ''
        counter = 1
        for key in sorted_clips:
            description += f'{counter}. {key}: {self.clips_usage[key]}\n'
            counter += 1
            if counter > 10:
                break
        embed.description = description
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Sounds(bot))
