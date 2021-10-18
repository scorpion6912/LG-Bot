import os
import time

from discord import guild
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext import tasks
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
load_dotenv(dotenv_path="../code bot/config")


# Bot event:
# Login
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='!aled'))
    print('Logged in as')
    print('{0.user}'.format(bot))
    print('------')


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
        role2 = discord.utils.get(ctx.guild.roles, name='Participant')
        msg = await channel.fetch_message(reaction.message.id)
        if msg.content == (
                f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer puis ✅ pour "
                f"lancer "
                f"la partie"):
            await ctx.add_roles(role)
            await ctx.add_roles(role2)
            await channel.send("{0.mention} est inscrit".format(ctx))
        else:
            print("autre channel add")
    if reaction.emoji == "✅":
        msg = await channel.fetch_message(reaction.message.id)
        await msg.delete()
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name='Villageois')
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
        if await count_villageois(ctx) < 2:
            await channel.send("impossible de lancer a moins de 4")
            time.sleep(3)
            await botdesetup(ctx)
            await botsetup(ctx)
            return
        await liste_villageois(ctx)
        await game(ctx)


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


# Bot commande:
@bot.command(name="test")
async def test(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, view_channel=True)


# Création d'un salon textuel
@bot.command(name="setup")
async def setup(ctx):
    await botsetup(ctx)


# Fonction de desetup
@bot.command(name="desetup")
async def desetup(ctx):
    await botdesetup(ctx)


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


@bot.command(name='time')
async def startTime(ctx, time: int, count: int):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(end_loop(ctx))
    l.start(l)

# A partir d'ici se sont les fonctions appeler par le bot
def loop(ctx):
    async def coro(l: tasks.Loop):
        await ctx.send(f"Il vous reste {((l.seconds*l.count)-(l.current_loop*l.seconds))}s")
    return coro


def end_loop(ctx):
    async def coro():
        await ctx.send("Le temps est écoulé ! J'espère que votre choix vous sera bénéfique !")
        #ajouter ici les inscrutions pour faire des actions
    return coro

    
async def count_villageois(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    print(len(role.members))
    return len(role.members)


async def liste_id_participant(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Participant')
    return role.members


async def liste_villageois(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='village')
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    name = ""
    for member in role.members:
        name = name + member.name + " "
    await channel.send(str(len(role.members)) + " joueurs :" + name + "vont jouer".format(ctx))


async def liste_id_villageois(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    return role.members


async def botdesetup(ctx):
    guild = ctx.guild
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    await role.delete()
    role = discord.utils.get(ctx.guild.roles, name="Participant")
    await role.delete()
    role = discord.utils.get(ctx.guild.roles, name="Mort")
    await role.delete()
    channel = discord.utils.get(guild.channels, name='Village_vocal')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='village')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='sorciere')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='voyante')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='cupidon')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='cimetiere')
    await channel.delete()


async def botsetup(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Mort")
    if role is None:
        await ctx.guild.create_role(name="Mort", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été créer")
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    if role is None:
        await ctx.guild.create_role(name="Villageois", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été créer")
    role = discord.utils.get(ctx.guild.roles, name="Participant")
    if role is None:
        await ctx.guild.create_role(name="Participant", mentionable=True)
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
        role = discord.utils.get(ctx.guild.roles, name="Participant")
        await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True)
        role = discord.utils.get(ctx.guild.roles, name="Villageois")
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
        await msg.add_reaction('➕')
        await msg.add_reaction('✅')
    else:
        await ctx.send(f"village est déjà créer")
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    if channel is None:
        channel = await guild.create_text_channel('loup-garou')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"loup-garou est déjà créer")
    channel = discord.utils.get(guild.text_channels, name='cimetiere')
    if channel is None:
        channel = await guild.create_text_channel('cimetiere')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name="Mort")
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
    else:
        await ctx.send(f"cimetiere est déjà créer")
    channel = discord.utils.get(guild.text_channels, name='cupidon')
    if channel is None:
        channel = await guild.create_text_channel('cupidon')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"cupidon est déjà créer")
    channel = discord.utils.get(guild.text_channels, name='sorciere')
    if channel is None:
        channel = await guild.create_text_channel('sorciere')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"sorciere est déjà créer")
    channel = discord.utils.get(guild.text_channels, name='voyante')
    if channel is None:
        channel = await guild.create_text_channel('voyante')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"voyante est déjà créer")


async def game(ctx):
    guild = ctx.guild
    channel_village = discord.utils.get(guild.text_channels, name='village')
    channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
    channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
    role_villageois = discord.utils.get(ctx.guild.roles, name="Villageois")
    await channel_village.send("Il fait sombre, la lumière de la lune traverse à peine les nuages pour révéler le "
                               "village de "
                               "Thiercelieux. Une petite bourgade sans prétention et paisible coincée dans les "
                               "montagnes. Pourtant, "
                               "une malédiction a frappé ce village si innocent, tous les 100 ans un éclair noir "
                               "tombe sur la stèle "
                               "de la place centrale du village. Les démons viennent s’emparer de l’âme des pauvres "
                               "villageois et "
                               "réveillent en certains la présence d’un être plein de malice et de poils, "
                               "le loup-garou. Le village "
                               "cherche à éradiquer la menace tandis que les loup-garous infiltrés au sein de ce "
                               "dernier profite de "
                               "la nuit pour dévorer les innocents. Aideriez-vous le village à survivre ou au "
                               "contraire "
                               "tenterez-vous de le précipiter dans la mort ?")
    time.sleep(4)

    await channel_village.send("C’est la nuit, tout le village s’endort, les joueurs ferment leurs micros")
    await channel_village.send("Les Loups-Garous se réveillent, se reconnaissent et désignent une nouvelle victime !!!")
    await channel_lg.send("C'est le moment de voter")
    time.sleep(5)
    await channel_village.send("Les Loups-Garous repus se rendorment et rêvent de prochaines victimes savoureuses")
    await channel_village.send(await liste_id_villageois(ctx))


bot.run(os.getenv("TOKEN"))
