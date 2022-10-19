import discord
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class Images(commands.Cog):
    location = 'cogs/images/'

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='mask', description='Why do you wear that mask?')
    async def mask(self, ctx: commands.Context, *, member: discord.Member):
        await member.display_avatar.with_size(128).with_format('jpg').save(f'{self.location}avatar.jpg')

        im1 = Image.open(f'{self.location}mask.jpg')
        im2 = Image.open(f'{self.location}avatar.jpg')

        back_im = im1.copy()
        back_im.paste(im2, (150, 650))
        back_im.save(f'{self.location}mask_final.jpg', quality=95)

        file = discord.File(f'{self.location}mask_final.jpg', filename='mask_final.jpg')

        await ctx.send(file=file)

    @commands.hybrid_command(name='adolf', description='Why do you wear that mask?')
    async def adolf(self, ctx: commands.Context, *, member: discord.Member):
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
            file_request = requests.get(attachment_url)

        await member.display_avatar.with_size(64).with_format('jpg').save(f'{self.location}avatar.jpg')

        im1 = Image.open(f'{self.location}adolf.jpg')
        im2 = Image.open(f'{self.location}avatar.jpg')

        back_im = im1.copy()
        back_im.paste(im2, (180, 120))
        back_im.save(f'{self.location}adolf_final.jpg', quality=95)

        file = discord.File(f'{self.location}adolf_final.jpg', filename='adolf_final.jpg')

        await ctx.send(file=file)

    @commands.hybrid_command(name='whiteboard', description='Why do you wear that mask?')
    async def whiteboard(self, ctx: commands.Context, *, text: str):
        im1 = Image.open(f'{self.location}whiteboard.jpg')
        im2 = Image.open(f'{self.location}whiteboard.jpg')
        mask = Image.open(f'{self.location}whiteboard_mask.jpg').convert('L').resize(im1.size)
        fontname = f'{self.location}fonts/DryWhiteboardMarker-Regular.ttf'
        draw = ImageDraw.Draw(im1)
        lines, font = text_wrap(text, fontname, 350, 260)
        line_height = font.getsize('hg')[1]
        color = 'rgb(25,25,25)'
        x, y = 55, 70
        for line in lines:
            draw.text((x, y), line, fill=color, font=font)

            y = y + line_height  # update y-axis for new line

        im = Image.composite(im1, im2, mask)
        im.save(f'{self.location}whiteboard_final.jpg', quality=95)

        file = discord.File(f'{self.location}whiteboard_final.jpg', filename='whiteboard_final.jpg')

        await ctx.send(file=file)


def text_wrap(text, fontname, max_width, max_height):
    """Wrap text base on specified width.
    This is to enable text of width more than the image width to be display
    nicely.
    @params:
        text: str
            text to wrap
        font: obj
            font of the text
        max_width: int
            width to split the text with
    @return
        lines: list[str]
            list of sub-strings
    """
    font = ImageFont.truetype(fontname, 104)
    lines = []
    font_size = 108
    # If the text width is smaller than the image width, then no need to split
    # just add it to the line list and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        lines_height = 0
        i = 0
        # append every word to a line while its width is shorter than the image width
        while i < len(words):
            line = str()
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines_height += font.getsize(line)[1]
            if lines_height >= max_height:
                font_size -= 4
                font = ImageFont.truetype(fontname, font_size)
                lines_height = 0
                i = 0
                lines.clear()
                line = str()
            if line:
                lines.append(line)
    return lines, font


async def setup(bot):
    await bot.add_cog(Images(bot))
