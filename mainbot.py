import os
import random

from discord import guild
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.utils import get

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
        await channel_vocal.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name="Villageois")
        await channel_vocal.set_permissions(role, read_messages=True, send_messages=True)
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
    embed = discord.Embed(title="tu as demande de l'aide ?", description="regarde tes mps 😉", color=0xFF0000)
    await ctx.send(embed=embed)
    await ctx.author.send("voici les commandes que tu peux utiliser".format(ctx))
    await ctx.author.send("!setup permet de créer les channels ".format(ctx))
    await ctx.author.send("!desetup permet de supprimer les channels créer par le bot".format(ctx))
    await ctx.author.send("!aled pour avoir la liste des commandes".format(ctx))



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

# Test random pour comprendre l'utilisation
@bot.command(name="randomtest")
async def randomtest(ctx):
    variable = ["pile", "face"]
    choice = random.choice(variable)
    await ctx.channel.send(choice)


@bot.command(name="randomvrs")
async def  randomvrs(ctx):
    variablee =["Atlas","Flo", "Léo", "Claire","Rémy"]
    random.shuffle(variablee)
    await ctx.send(variablee.pop())
    await ctx.send(variablee.pop())

async def liste_id_participant(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Participant')
    return role.members

@bot.command(name="randomUtilis")
async def randomUtilis(ctx):
    variable = await liste_id_participant(ctx)
    choice = random.choice(variable)
    user = bot.get_user(choice.id)
    return user

@bot.command(name="testUser")
async def testUser(ctx):
    user = randomUtilis()
    if user:
        await ctx.channel.send("l'ulisateur est : " + user.name.format(ctx))
    else:
        await ctx.channel.send("Utilisateur non trouvé")

@bot.command(name="assigner_membre")
async def assigner_membre(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, view_channel=True)

@bot.command(name="assigner_membre_rdm")
async def assigner_membre_rdm(ctx):
    user = await randomUtilis(ctx)
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)

bot.run(os.getenv("TOKEN"))