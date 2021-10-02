import os
import time

from discord import guild
from dotenv import load_dotenv
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
load_dotenv(dotenv_path="../code bot/config")


# Login
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='!aled'))
    print('Logged in as')
    print('{0.user}'.format(bot))
    print('------')


# Création d'un salon textuel
@bot.command(name="setup")
async def setup(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    if role is None:
        await ctx.guild.create_role(name="Villageois", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été créer")
    guild = ctx.guild
    channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
    if channel_vocal is None:
        await guild.create_voice_channel('Village_vocal')
        channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
        await channel_vocal.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False,
                                            view_channel=False)
        role = discord.utils.get(ctx.guild.roles, name="Villageois")
        await channel_vocal.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
    else:
        await ctx.send(f"Le vocal a déjà été créer")
    channel = discord.utils.get(guild.text_channels, name='village')
    if channel is None:
        channel = await guild.create_text_channel('village')
        msg = await channel.send(
            f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer puis ✅ pour lancer "
            f"la partie")
        await msg.add_reaction('➕')
        await msg.add_reaction('✅')
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    if channel is None:
        channel = await guild.create_text_channel('loup-garou')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)

    else:
        await ctx.send(f"Les salons de jeux ont deja ete creer")


# Création message après setup,à réagir pour savoir qui veut s'inscrire
# S'inscrire
@bot.event
async def on_reaction_add(reaction, ctx):
    if ctx.id == bot.user.id:
        return
    channel = discord.utils.get(ctx.guild.text_channels, name='village')
    if reaction.message.channel.id != channel.id:
        return
    if reaction.emoji == "➕":
        role = discord.utils.get(ctx.guild.roles, name='Villageois')
        msg = await channel.fetch_message(reaction.message.id)
        if msg.content == (
                f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer puis ✅ pour lancer "
                f"la partie"):
            await ctx.add_roles(role)
            await channel.send("{0.mention} est inscrit".format(ctx))
        else:
            print("autre channel add")
    if reaction.emoji == "✅":
        msg = await channel.fetch_message(reaction.message.id)
        await msg.delete()
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name='Villageois')
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
        if await count_villageois(ctx) < 4:
            await liste_villageois(ctx)
            return
        await liste_villageois(ctx)


# Se désinscrire
@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
    channel = discord.utils.get(guild.text_channels, name='village')
    if payload.channel_id != channel.id:
        return
    role = discord.utils.get(guild.roles, name='Villageois')
    msg = await channel.fetch_message(payload.message_id)
    if msg.content == (
            f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer puis ✅ pour lancer "
            f"la partie"):
        await member.remove_roles(role)
        await channel.send(f"{member.mention} est désinscrit".format(member))
    else:
        print("autre channel remove")


@bot.command(name="test")
async def test(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, view_channel=True)


# Fonction de desetup
@bot.command(name="desetup")
async def desetup(ctx):
    guild = ctx.guild
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    await role.delete()
    channel = discord.utils.get(guild.channels, name='Village_vocal')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='village')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    await channel.delete()


# Affichage des commandes
@bot.command(name="aled")
async def aled(ctx):
    embed = discord.Embed(title="foo", description="bar", color=0xFF0000)
    await ctx.send(embed=embed)
    await ctx.author.send("voici les commandes que tu peux utiliser".format(ctx))
    await ctx.author.send("!setup permet de créer les channels ".format(ctx))
    await ctx.author.send("!desetup permet de supprimer les channels créer par le bot".format(ctx))
    await ctx.author.send("!aled pour avoir la liste des commandes".format(ctx))
    await ctx.channel.send("va voir tes mp".format(ctx))


# Message privé une personne
@bot.command(name="mp")
async def download(message):
    await message.author.send('👀')


# Commande pour effacer des messages dans un channel
@bot.command(name="del")
async def delete(ctx, number: int):
    messages = await ctx.channel.history(limit=number + 1).flatten()

    for each_message in messages:
        await each_message.delete()


# Commande bonjour
@bot.command(name='bonjour')
async def bonjour(ctx):
    await ctx.channel.send('Bonjour {0.author.mention} !'.format(ctx))


# Ping (pong)
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


# Embed pour que ce soit plus joli
@bot.command(name='oui')
async def oui(ctx):
    embed = discord.Embed(title="foo", description="bar", color=0xFF0000)
    await ctx.send(embed=embed)


# Connexion dans salon vocal
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


# Déconnexion dans salon vocal
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


# A partir d'ici se sont les fonctions appeler par le bot

async def count_villageois(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    i = 0
    for member in ctx.guild.members:
        if role in member.roles:
            print("what")
        else:
            i = i + 1
    return i


async def liste_villageois(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='village')
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    text = ""
    i = 0
    for member in ctx.guild.members:
        if role in member.roles:
            print("what")
        else:
            text = text + ctx.name + " "
            i = i + 1
    if i < 4:
        await channel.send("impossible de lancer à moins de quatre".format(ctx))
        time.sleep(2)
        await botdesetup(ctx)
        await botsetup(ctx)
        return
    await channel.send(str(i) + " joueurs :" + text + "vont jouer".format(ctx))


async def botdesetup(ctx):
    guild = ctx.guild
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    await role.delete()
    channel = discord.utils.get(guild.channels, name='Village_vocal')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='village')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    await channel.delete()


async def botsetup(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    if role is None:
        await ctx.guild.create_role(name="Villageois", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été créer")
    guild = ctx.guild
    channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
    if channel_vocal is None:
        await guild.create_voice_channel('Village_vocal')
        channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
        await channel_vocal.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False,
                                            view_channel=False)
        role = discord.utils.get(ctx.guild.roles, name="Villageois")
        await channel_vocal.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
    else:
        await ctx.send(f"Le vocal a déjà été créer")
    channel = discord.utils.get(guild.text_channels, name='village')
    if channel is None:
        channel = await guild.create_text_channel('village')
        msg = await channel.send(
            f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer puis ✅ pour lancer "
            f"la partie")
        await msg.add_reaction('➕')
        await msg.add_reaction('✅')
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    if channel is None:
        channel = await guild.create_text_channel('loup-garou')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)

    else:
        await ctx.send(f"Les salons de jeux ont deja ete creer")


bot.run(os.getenv("TOKEN"))
