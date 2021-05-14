import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
load_dotenv(dotenv_path="../code bot/config")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name='regarde la nasa', url='https://www.twitch.tv/nasa'))
    print('Logged in as')
    print('{0.user}'.format(bot))
    print('------')


@bot.event
async def on_member_join(member):
    print(f"Un nouveau membre est arrivé : {member.display_name}")


@bot.event
async def test(ctx):
    if ctx == 290139158952017920:
        await ctx.send('sa va juan?'.format(ctx))


@bot.event
async def test(ctx):
    if ctx == 798950981609193532:
        await ctx.send('{0.author.mention} sa va le spam?'.format(ctx))


@bot.command(name="create")
async def create(ctx):
    channel = await ctx.guild.create_text_channel('Loup-garrou')

@bot.command(name="mp")
async def download(message):
    channel = message.channel
    await message.author.send('👀')


@bot.command(name="del")
async def delete(ctx, number: int):
    messages = await ctx.channel.history(limit=number + 1).flatten()

    for each_message in messages:
        await each_message.delete()


@bot.command(name='salut')
async def salut(ctx):
    await ctx.channel.send('Salut {0.author.mention}'.format(ctx))


@bot.command(name='ping')
async def ping(ctx):
    await ctx.channel.send('pong'.format(ctx))


@bot.command(name='oui')
async def oui(ctx):
    embed = discord.Embed(title="foo", description="bar", color=0xFF0000)
    await ctx.send(embed=embed)


@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = await channel.connect()


@bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    await ctx.guild.voice_client.disconnect()


bot.run(os.getenv("TOKEN"))
