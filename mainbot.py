import json
import os
import random
import time

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
    if "Faite le bon choix" in reaction.message.content:
        with open("vars.json", "r") as f:
            vars = json.load(f)
        await add_var(ctx, ctx, 1)
        vote = vars[str(ctx.id)]["vote"]
        if vote > 0:
            await reaction.message.remove_reaction(reaction.emoji, ctx)
            await channel.send("Il n'est pas possible de voter pour deux personne différente")
            await add_var(ctx, ctx, 1)
            print("add")


async def add_var(ctx: commands.Context, user: discord.User, x):
    with open("vars.json", "r") as f:
        vars = json.load(f)

    await update_var(vars, user)
    await add_varr(vars, user, x)

    with open("vars.json", "w") as f:
        json.dump(vars, f)


async def update_var(vars, user):
    if not f"{user.id}" in vars:
        vars[f"{user.id}"] = {}
        vars[f"{user.id}"]["vote"] = 0


async def add_varr(vars, user, x):
    vars[f"{user.id}"]["vote"] += x


@bot.command()
async def var_add(ctx: commands.Context, user: discord.User = None):
    with open("vars.json", "r") as f:
        vars = json.load(f)
    await set_varr(ctx, vars, user.id, 0)
    with open("vars.json", "w") as f:
        json.dump(vars, f)


async def set_varr(ctx: commands.Context, vars, user, x):
    vars[f"{user}"]["vote"] = x


# Se désinscrire
@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
    channel = discord.utils.get(guild.text_channels, name='village')
    if payload.channel_id != channel.id:
        print('wtf')
        return
    role = discord.utils.get(guild.roles, name='Villageois')
    msg = await channel.fetch_message(payload.message_id)
    if msg.content == (
            f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer puis ✅ pour lancer "
            f"la partie"):
        await member.remove_roles(role)
        await channel.send(f"{member.mention} est désinscrit".format(member))
    if "Faite le bon choix" in msg.content:
        #await var_add(guild, member)
        await add_var(guild, member, -2)
        with open("vars.json", "r") as f:
            vars = json.load(f)
        vote = vars[str(member.id)]["vote"]
        if vote < 0:
            await add_var(guild, member, 1)


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


async def liste_villageois(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='village')
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    name = ""
    for member in role.members:
        name = name + member.name + " "
    await channel.send(str(len(role.members)) + " joueurs :" + name + "vont jouer".format(ctx))


# Test random pour comprendre l'utilisation
@bot.command(name="randomtest")
async def randomtest(ctx):
    variable = ["pile", "face"]
    choice = random.choice(variable)
    await ctx.channel.send(choice)


@bot.command(name="randomvrs")
async def randomvrs(ctx):
    variablee = ["Atlas", "Flo", "Léo", "Claire", "Rémy"]
    random.shuffle(variablee)
    await ctx.send(variablee.pop())
    await ctx.send(variablee.pop())


@bot.command(name="randomUtilis")
async def randomUtilis(ctx):
    variable = await liste_id_participant(ctx)
    choice = random.choice(variable)
    user = bot.get_user(choice.id)
    return user


async def assigner_membre_rdm(ctx):
    user = await randomUtilis(ctx)
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)


@bot.command(name="testUser")
async def testUser(ctx):
    user = randomUtilis()
    if user:
        await ctx.channel.send("l'ulisateur est : " + user.name.format(ctx))
    else:
        await ctx.channel.send("Utilisateur non trouvé")


async def assigner_membre(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, view_channel=True)


@bot.command(name="debut")
async def debut(ctx):
    i = 0
    liste = await liste_id_participant(ctx)
    random.shuffle(liste)
    # pour deux loup-garou
    while (i < 2):
        choice = liste.pop()
        user = bot.get_user(choice.id)
        print("l'utilisateur va être : ", user.name.format(ctx))
        await assigner_membre_fct(ctx, user)
        print("l'utilisateur a bien été assigné")
        i = i + 1
    return liste


async def assigner_membre_fct(ctx, user):
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)


@bot.command(name='time')
async def startTime(ctx, time: int, count: int,msg):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(end_loop(ctx,msg))
    l.start(l)


@bot.command(name="add_xp")
async def add_xp(ctx: commands.Context, user: discord.User, p):
    await add_xp2(ctx, user, p)


@bot.command(name="xp")
async def xp(ctx, user: discord.User = None):
    if not user:
        id = ctx.message.author.id
        with open("users.json", "r") as f:
            users = json.load(f)
        xp = users[str(id)]["points"]
        await ctx.send(f"Tu as {xp} xp!")
    else:
        id = user.id
        with open("users.json", "r") as f:
            users = json.load(f)
        xp = users[str(id)]["points"]
        await ctx.send(f"{user} a {xp} xp!")


@bot.command(name="classement")
async def classement(ctx):
    with open('users.json', 'r') as f:
        data = json.load(f)

    top_users = {k: v for k, v in sorted(data.items(), key=lambda item: item[1]['points'], reverse=True)}

    names = ''
    for postion, user in enumerate(top_users):
        names += f'{postion + 1} - <@!{user}> avec {top_users[user]["points"]} points \n'

    embed = discord.Embed(title=f'Classment dans le serveur: {ctx.guild.name}')
    embed.add_field(name="NOM", value=names, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="kill")
async def kill(ctx, user: discord.User):
    guild = ctx.guild
    member = guild.get_member(user.id)
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    role2 = discord.utils.get(ctx.guild.roles, name='Mort')
    await member.remove_roles(role)
    await member.add_roles(role2)


@bot.command(name="mute")
async def mute(ctx, setting):
    voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
    for member in voice_channel.members:
        if setting.lower() == 'true':
            await member.edit(mute=True)
        elif setting.lower() == 'false':
            await member.edit(mute=False)


@bot.command(name='sondage')
async def sondage(ctx, x, y):
    liste = await liste_id_villageois(ctx)
    liste_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    nb = await count_villageois(ctx)
    lst = [0] * nb
    i = 0
    guild = ctx.guild
    channel_village = discord.utils.get(guild.text_channels, name='village')
    text = ""
    while i != len(liste):
        await add_var(ctx, liste[i], 0)
        with open("vars.json", "r") as f:
            vars = json.load(f)
        vote = vars[str(liste[i].id)]["vote"]
        if vote > 0:
            await add_var(guild, liste[i], -1)
        text = text + liste[i].name + " " + liste_emoji[i] + "\n"
        i += 1
    text = text + "Faite le bon choix"
    msg = await channel_village.send(text)
    i = 0
    while i != len(liste):
        await msg.add_reaction(liste_emoji[i])
        i += 1
    await startTime(ctx, int(x), int(y),msg)


# A partir d'ici se sont les fonctions appeler par le bot
def loop(ctx):
    async def coro(l: tasks.Loop):
        await ctx.send(f"Il vous reste {((l.seconds * l.count) - (l.current_loop * l.seconds))}s")

    return coro


def end_loop(ctx,msg):
    async def coro():
        await ctx.send("Le temps est écoulé ! J'espère que votre choix vous sera bénéfique !")
        liste = await liste_id_villageois(ctx)
        liste_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        nb = await count_villageois(ctx)
        lst = [0] * nb
        guild = ctx.guild
        channel_village = discord.utils.get(guild.text_channels, name='village')
        if "Faite le bon choix" in msg.content:
            print(msg)
        v = 0
        while (v < len(liste)):
            emojii = liste_emoji[v]
            m = await channel_village.fetch_message(msg.id)
            react = discord.utils.get(m.reactions, emoji=emojii)
            a = react.count
            lst[v] += a
            v = v + 1
        await channel_village.send(lst)

    return coro


async def count_villageois(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    print(len(role.members))
    return len(role.members)


async def liste_id_participant(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Participant')
    return role.members


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


async def add_xp2(ctx: commands.Context, user: discord.User, p):
    with open("users.json", "r") as f:
        users = json.load(f)

    await update_data(users, user)
    await add_points(users, user, int(p))

    with open("users.json", "w") as f:
        json.dump(users, f)


async def update_data(users, user):
    if not f"{user.id}" in users:
        users[f"{user.id}"] = {}
        users[f"{user.id}"]["points"] = 0


async def add_points(users, user, p):
    users[f"{user.id}"]["points"] += p


bot.run(os.getenv("TOKEN"))
