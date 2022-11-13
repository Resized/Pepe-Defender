import asyncio
import os
import random

import discord
import requests
import boto3
import botocore.exceptions
from mutagen.mp3 import MP3

from discord.ext import commands

from utils import play_sound, save_obj_s3, get_filename_from_cd, load_obj_s3, sounds_location, obj_location, \
    MAX_MP3_LENGTH, MAX_MP3_SIZE, find_clip

AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')


class Sounds(commands.Cog):
    clips_volume = dict()
    clips_usage = dict()

    def __init__(self, bot: commands.Bot):
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

    @commands.hybrid_command(name='clip', description='Plays a sound clip')
    async def clip(self, ctx: commands.Context, filename: str, volume: float = 1.0):
        volume = min(1.0, volume)
        available_clips = os.listdir(sounds_location)
        if filename in self.clips_volume.keys():
            volume *= self.clips_volume.get(filename)
        found_clip = find_clip(filename)
        if filename == 'fart':
            fart_clips = []
            for fname in available_clips:
                if fname.startswith('fart'):
                    fart_clips.append(fname)
            selected_clip = random.choice(fart_clips)
            found_clip = [f'{selected_clip}']
        if len(found_clip) != 1:
            if len(found_clip) > 1:
                clips_matching = ''
                for clip_name in found_clip:
                    clips_matching += f'`{clip_name.split(".")[0]}` '
                await ctx.send(f'{clips_matching} matches `{filename}`, pick one.')
                return
            await ctx.send(f'{filename} clip was not found.')
            return
        filename = found_clip[0].split(".")[0]
        current_room = ctx.message.author.voice.channel
        await ctx.send(f'Playing `{filename}`')
        await play_sound(self.bot, current_room, f'{sounds_location}{found_clip[0]}', volume)
        self.clips_usage[filename] = self.clips_usage.get(filename, 0) + 1
        save_obj_s3(self.clips_usage, 'clips_usage', self.s3.Bucket(S3_BUCKET))



    @commands.hybrid_command(name='clips', description='Shows available sound clips')
    async def clips(self, ctx: commands.Context, filename_to_find: str = None):
        if filename_to_find:
            embed = discord.Embed(title=f'Available sound clips with \'{filename_to_find}\' substring:',
                                  colour=discord.Colour.blue())
        else:
            embed = discord.Embed(title='Available sound clips:', colour=discord.Colour.blue())
        available_clips = []
        for filename in os.listdir(sounds_location):
            if filename.endswith('.mp3'):
                if not filename.startswith('fart'):
                    available_clips.append(filename[:-4])
        available_clips.append('fart')
        if filename_to_find:
            final_clips = [i for i in available_clips if filename_to_find in i]
        else:
            final_clips = available_clips
        description = ', '.join(sorted(final_clips))
        description += '.'
        embed.description = description
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='addclip', description=f'Add sound clip (mp3 < {MAX_MP3_SIZE / 1000}kb)')
    async def addclip(self, ctx: commands.Context):
        attachment_url = ctx.message.attachments[0].url
        r = requests.get(attachment_url, allow_redirects=True)
        if int(r.headers.get('content-length')) > MAX_MP3_SIZE:
            await ctx.send(f'File is too heavy (over {MAX_MP3_SIZE / 1000}kb)')
            return
        elif r.headers.get('content-type') != 'audio/mpeg':
            await ctx.send('File is not an mp3.')
            return
        filename = (get_filename_from_cd(r.headers.get('content-disposition'))).lower()
        if filename.split('.')[-1] != 'mp3':
            await ctx.send('File is not an mp3.')
            return
        try:
            print(filename)
            open(sounds_location + filename, 'wb').write(r.content)
            audio = MP3(sounds_location + filename)
            if audio.info.length > MAX_MP3_LENGTH:
                await ctx.send(f'❌ `{filename}` exceeds `{MAX_MP3_LENGTH}` seconds and has not be added. ')
                os.remove(sounds_location + filename)
                return
            self.s3.Bucket(S3_BUCKET).upload_file(f'{sounds_location}{filename}',
                                                  f'sounds/{filename}')
            await ctx.send(f'✅ `{filename[:-4]}` has been added to sound clips.')
        except OSError:
            await ctx.send(f'❌ An error occurred, `{filename[:-4]}` has not be added.')

    @commands.hybrid_command(name='removeclip', description='Removes a clip')
    async def removeclip(self, ctx: commands.Context, clipname: str):
        try:
            self.s3.Object(S3_BUCKET, f'{clipname}.mp3').load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                await ctx.send(f'❌ An error occurred, `{clipname}` was not found.')
            else:
                await ctx.send(f'❌ An error occurred.')
        else:
            os.remove(f'{sounds_location}{clipname}.mp3')
            self.s3.Object(S3_BUCKET, f'{sounds_location}{clipname}.mp3').delete()
            await ctx.send(f'`{clipname}` has been removed.')

    @commands.hybrid_command(name='renameclip', description='Renames a clip')
    async def renameclip(self, ctx: commands.Context, clipname: str, newname: str):
        if (clipname + '.mp3').lower() in os.listdir(sounds_location):
            os.rename(rf'{sounds_location}{clipname}.mp3', rf'{sounds_location}{newname}.mp3')
            self.s3.Object(S3_BUCKET, f'{sounds_location}{newname}.mp3').copy_from(
                CopySource=f'{S3_BUCKET}/{sounds_location}{clipname}.mp3')
            self.s3.Object(S3_BUCKET, f'{sounds_location}{clipname}.mp3').delete()
            self.clips_usage[newname] = self.clips_usage.pop(clipname)
            self.clips_volume[newname] = self.clips_volume.pop(clipname, 1)
            save_obj_s3(self.clips_usage, 'clips_usage', self.s3.Bucket(S3_BUCKET))
            save_obj_s3(self.clips_volume, 'clips_volume', self.s3.Bucket(S3_BUCKET))

            await ctx.send(f'✅ `{clipname}` has been changed to `{newname}`.')
        else:
            await ctx.send(f'❌ `{clipname}` was not found.')

    @commands.hybrid_command(name='setvolume', description='Set clip volume')
    async def setvolume(self, ctx: commands.Context, clipname: str, volume: float):
        previous_volume = self.clips_volume.get(clipname, 1.0)
        if (clipname + '.mp3').lower() in os.listdir(sounds_location):
            if 1.0 >= volume >= 0.0:
                self.clips_volume[clipname] = volume
                save_obj_s3(self.clips_volume, 'clips_volume', self.s3.Bucket(S3_BUCKET))
                await ctx.send(f'Volume of {clipname} changed from {previous_volume} to {volume}')
            else:
                await ctx.send('Volume must be between 0 and 1.0')
        else:
            await ctx.send(f'Clip named {clipname} does not exist')

    @commands.hybrid_command(name='clip_leaderboards', help='Shows top 10 clips by usage')
    async def clip_leaderboards(self, ctx: commands.Context):
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
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='notify', description='Notify user with message')
    async def notify(self, ctx: commands.Context, member: discord.Member, timer: float = 5.0, message: str = None,
                     clip_name: str = None):
        if message is None:
            message = f'{member.mention} you are being notified by {ctx.author.mention}.'
        else:
            message = f'{member.mention} notified with: {message}'
        if timer < 0:
            timer = 0
        if clip_name is None:
            clip_name = f'{sounds_location}ohno.mp3'
        msg = await ctx.send(content=f'Notifying {member.mention} in {timer} seconds')
        while timer > 0:
            await asyncio.sleep(1)
            timer -= 1
            await msg.edit(content=f'Notifying {member.mention} in {timer} seconds')
        if member.voice is None:
            await ctx.send(content=f'{member.mention} is not in voice channel', ephemeral=True)
        else:
            found_clip = find_clip(clip_name)
            if found_clip:
                await play_sound(self.bot, member.voice.channel, f'{sounds_location}{found_clip[0]}', volume=0.5)
            else:
                await ctx.send(content=f'Clip {clip_name} not found', ephemeral=True)
        await ctx.send(content=message, allowed_mentions=discord.AllowedMentions(users=True))


async def setup(bot):
    await bot.add_cog(Sounds(bot))
