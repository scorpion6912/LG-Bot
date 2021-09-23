import os

from discord import guild
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext import tasks

bot = commands.Bot(command_prefix='!')
load_dotenv(dotenv_path="../code bot/config")


# login
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='!aled'))
    print('Logged in as')
    print('{0.user}'.format(bot))
    print('------')


# arriver membre (a tester)
@bot.event
async def on_member_join(member):
    print(f"Un nouveau membre est arrivé : {member.display_name}")


@bot.command(name="setup_role")
async def newrole(ctx):
    role = await ctx.guild.create_role(name="LoupGarou", colour=0xFF0F00, mentionable=True)
    await ctx.author.add_roles(role)
    await ctx.send(f"Successfully created and assigned {role.mention}!")


# creation d'un channel textuel
@bot.command(name="setup")
async def setup(ctx):
    guild = ctx.guild
    channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
    if channel_vocal is None:
        await guild.create_voice_channel('Village_vocal')
        channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
        await channel_vocal.set_permissions(ctx.guild.default_role, read_messages=False,send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name="LoupGarou")
        await channel_vocal.set_permissions(role, read_messages=True, send_messages=True)
    else:
        await ctx.send(f"Le vocal a daja été créer")
    channel = discord.utils.get(guild.text_channels, name='village')
    if channel is None:
        channel = await guild.create_text_channel('village')
        msg = await channel.send(
            f"Les salons ont bien été créer merci de réagir avec : ➕ a ce messsage pour participer et ✅ pour lancer "
            f"la partie")
        await msg.add_reaction('➕')
        await msg.add_reaction('✅')

    else:
        await ctx.send(f"Les salons de jeux ont deja ete creer")



@bot.event
async def on_reaction_add(reaction, ctx):
    if ctx.id == 834401250865840148:
        return
    if reaction.emoji == "➕":
        channel = discord.utils.get(ctx.guild.text_channels,name='village')
        role = discord.utils.get(ctx.guild.roles, name='LoupGarou')
        msg = await channel.fetch_message(reaction.message.id)
        if msg.content == (f"Les salons ont bien été créer merci de réagir avec : ➕ a ce messsage pour participer et ✅ pour lancer "
        f"la partie"):
            await ctx.add_roles(role)
            await channel.send("{0.mention} est inscrit".format(ctx))
        else:
            print("autre channel add")


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
    channel = discord.utils.get(guild.text_channels, name='village')
    role = discord.utils.get(guild.roles, name='LoupGarou')
    msg = await channel.fetch_message(payload.message_id)
    if msg.content == (f"Les salons ont bien été créer merci de réagir avec : ➕ a ce messsage pour participer et ✅ pour lancer "
    f"la partie"):
        await member.remove_roles(role)
        await channel.send(f"{member.mention} est désinscrit".format(member))
    else:
        print("autre channel remove")


@bot.command(name="desetup")
async def desetup(ctx):
    guild = ctx.guild
    channel = discord.utils.get(guild.channels, name='Village_vocal')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='village')
    await channel.delete()


@bot.command(name="aled")
async def aled(ctx):
    msg = await ctx.channel.send("Bonjour {0.author} tu as besoin d'aide?".format(ctx))
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    def checkEmoji(reaction2, user2):
        return ctx.message.author == user2 and msg.id == reaction2.message.id and (
                str(reaction2.emoji) == "✅" or str(reaction2.emoji) == "❌")

    try:

        reaction, user = await bot.wait_for("reaction_add", check=checkEmoji)
        if reaction.emoji == "✅":
            await ctx.author.send("voici les commandes que tu peux utiliser".format(ctx))
            await ctx.author.send("!setup permet de créer les channels ".format(ctx))
            await ctx.author.send("!desetup permet de supprimer les channels créer par le bot".format(ctx))
            await ctx.author.send("!aled pour avoir la liste des commandes".format(ctx))
            await ctx.channel.send("va voir tes mp".format(ctx))
        if reaction.emoji == "❌":
            await ctx.channel.send("D'accord n'hésite pas à me redemander si tu as besoin".format(ctx))
    finally:
        return


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
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


# embed pour que sa soit plus jolie
@bot.command(name='oui')
async def oui(ctx):
    embed = discord.Embed(title="foo", description="bar", color=0xFF0000)
    await ctx.send(embed=embed)


# connection dans channel vocal
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


# deconnection dans channel vocal
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


def loop(ctx):
    async def coro(l: tasks.Loop):
        await ctx.send(f"Il vous reste {(l.seconds * (l.count + 1)) // (l.current_loop + 1)}s")
    return coro


def end_loop(ctx):
    async def coro():
        await ctx.send("Done !")
    return coro


@bot.command(name='time')
async def startTime(ctx, time: int, count: int):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(end_loop(ctx))
    l.start(l)

bot.run(os.getenv("TOKEN"))
