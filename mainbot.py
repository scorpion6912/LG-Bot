import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
load_dotenv(dotenv_path="../code bot/config")


# login
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name='regarde la nasa', url='https://www.twitch.tv/nasa'))
    print('Logged in as')
    print('{0.user}'.format(bot))
    print('------')


# arriver membre (a tester)
@bot.event
async def on_member_join(member):
    print(f"Un nouveau membre est arrivé : {member.display_name}")


# spam juan (inutile)
@bot.event
async def test(ctx):
    if ctx == 290139158952017920:
        await ctx.send('sa va juan?'.format(ctx))


# spam bot (inutile)
@bot.event
async def test(ctx):
    if ctx == 798950981609193532:
        await ctx.send('{0.author.mention} sa va le spam?'.format(ctx))


# bot.command(name="setup_role")
# async def newrole(ctx):
#     role = await ctx.guild.create_role(name="LoupGarou", mentionable=True)
#     await ctx.author.add_roles(role)
#     await ctx.send(f"Successfully created and assigned {role.mention}!")


# creation d'un channel textuel
@bot.command(name="setup")
async def setup(ctx):
    guild = ctx.guild
    channel_vocal = discord.utils.get(guild.channels, name='loupgarou_vocal')
    if channel_vocal is None:
        await guild.create_voice_channel('loupgarou_vocal')
    else:
        await ctx.send(f"Les salons vocaux ont deja ete creer")
    channel = discord.utils.get(guild.text_channels, name='loupgarou')
    if channel is None:
        channel = await guild.create_text_channel('loupgarou')
        msg = await channel.send(
            f"Les salons ont bien été créer merci de réagir a ce messsage pour participer nb Joueur/nb "
            f"max Joueur")
        await msg.add_reaction('👀')

    else:
        await ctx.send(f"Les salons de jeux ont deja ete creer")


# mp une personne :eyes:
@bot.command(name="mp")
async def download(message):
    await message.author.send('👀')


# commande pour del des messages dans un channel
@bot.command(name="del")
async def delete(ctx, number: int):
    messages = await ctx.channel.history(limit=number + 1).flatten()

    for each_message in messages:
        await each_message.delete()


# bonjour c'est la moindre des choses
@bot.command(name='salut')
async def salut(ctx):
    await ctx.channel.send('Salut {0.author.mention}'.format(ctx))


# ping pong (a faire avec reponse des ms)
@bot.command(name='ping')
async def ping(ctx):
    await ctx.channel.send('pong'.format(ctx))


# embed pour que sa soit plus jolie
@bot.command(name='oui')
async def oui(ctx):
    embed = discord.Embed(title="foo", description="bar", color=0xFF0000)
    await ctx.send(embed=embed)


# test connection dans channel vocal marche pas
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


# test deconnection dans channel vocal marche pas
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


bot.run(os.getenv("TOKEN"))
