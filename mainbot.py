import json
import os
import random

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
    channel2 = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    channel3 = discord.utils.get(ctx.guild.text_channels, name='voyante')
    channel4 = discord.utils.get(ctx.guild.text_channels, name='cimetiere')
    channel5 = discord.utils.get(ctx.guild.text_channels, name="chasseur")
    if reaction.message.channel.id == channel.id or reaction.message.channel.id == channel2.id or reaction.message.channel.id == channel3.id or reaction.message.channel.id == channel4.id or reaction.message.channel.id == channel5.id:
        chan = bot.get_channel(reaction.message.channel.id)
    else:
        return
    role = discord.utils.get(ctx.guild.roles, name="Mort")
    if role in ctx.roles:
        if reaction.message.channel.id == channel4.id:
            with open("vars.json", "r") as f:
                vars = json.load(f)
            await add_var(ctx, ctx, 1)
            vote = vars[str(ctx.id)]["vote"]
            if vote > 0:
                await reaction.message.remove_reaction(reaction.emoji, ctx)
                await ctx.send("Il n'est pas possible de voter pour deux personnes différentes")
                await add_var(ctx, ctx, 1)
            return
    if reaction.emoji == "➕":
        role = discord.utils.get(ctx.guild.roles, name='Villageois')
        role2 = discord.utils.get(ctx.guild.roles, name='Participant')
        msg = await channel.fetch_message(reaction.message.id)
        if msg.content == (
                f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer, puis ✅ pour "
                f"lancer "
                f"la partie"):
            await ctx.add_roles(role)
            await ctx.add_roles(role2)
            await channel.send("{0.mention} est inscrit".format(ctx))
        else:
            print("autre channel add")
    if reaction.emoji == "✅":
        msg = await channel.fetch_message(reaction.message.id)
        if msg.content == (
                f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer, puis ✅ pour "
                f"lancer "
                f"la partie"):
            msg = await channel.fetch_message(reaction.message.id)
            await msg.delete()
            await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
            role = discord.utils.get(ctx.guild.roles, name='Villageois')
            await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
            if await count_villageois(ctx) < 4:
                await channel.send("impossible de lancer à moins de 4")
                await botdesetup(ctx, "new_game")
                await botsetup(ctx, "new game")
                return
            await liste_villageois(ctx)
            await nuit_un(ctx)
        if msg.content == "Voulez-vous relancer une partie ?":
            await botdesetup(ctx, "new game")
            await botsetup(ctx, "new game")
    if reaction.emoji == "❌":
        msg = await channel.fetch_message(reaction.message.id)
        if msg.content == "Voulez-vous relancer une partie ?":
            await botdesetup(ctx, "None")
    if "Faites le bon choix" in reaction.message.content:
        with open("vars.json", "r") as f:
            vars = json.load(f)
        await add_var(ctx, ctx, 1)
        vote = vars[str(ctx.id)]["vote"]
        if vote > 0:
            await reaction.message.remove_reaction(reaction.emoji, ctx)
            await ctx.send("Il n'est pas possible de voter pour deux personnes différentes")
            await add_var(ctx, ctx, 1)


async def add_var(ctx: commands.Context, user: discord.User, x):
    with open("vars.json", "r") as f:
        vars = json.load(f)

    await update_var(vars, user)
    await add_varr(vars, user, x)

    with open("vars.json", "w") as f:
        json.dump(vars, f)


async def add_role(ctx: commands.Context, user: discord.User, x):
    with open("vars.json", "r") as f:
        vars = json.load(f)

    await update_var(vars, user)
    await add_rrole(vars, user, x)

    with open("vars.json", "w") as f:
        json.dump(vars, f)


async def add_rrole(vars, user, x):
    vars[f"{user.id}"]["role"] += x


async def add_role2(ctx: commands.Context, user: discord.User, x):
    with open("vars.json", "r") as f:
        vars = json.load(f)

    await update_var(vars, user)
    await add_rrole2(vars, user, x)

    with open("vars.json", "w") as f:
        json.dump(vars, f)


async def add_rrole2(vars, user, x):
    vars[f"{user.id}"]["role2"] += x


async def update_var(vars, user):
    if not f"{user.id}" in vars:
        vars[f"{user.id}"] = {}
        vars[f"{user.id}"]["vote"] = 0
        vars[f"{user.id}"]["role"] = 0
        vars[f"{user.id}"]["role2"] = 0


async def add_varr(vars, user, x):
    vars[f"{user.id}"]["vote"] += x


# Se désinscrire
@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
    channel = discord.utils.get(guild.text_channels, name='village')
    channel2 = discord.utils.get(guild.text_channels, name='loup-garou')
    channel3 = discord.utils.get(guild.text_channels, name='voyante')
    channel4 = discord.utils.get(guild.text_channels, name='cimetiere')
    channel5 =  discord.utils.get(guild.text_channels, name='chasseur')
    if payload.channel_id == channel.id or payload.channel_id == channel2.id or payload.channel_id == channel3.id or payload.channel_id == channel4.id or payload.channel_id == channel5.id:
        role = discord.utils.get(guild.roles, name='Villageois')
        role2 = discord.utils.get(guild.roles, name='Participant')
        chan = bot.get_channel(payload.channel_id)
        msg = await chan.fetch_message(payload.message_id)
        if msg.content == (
                f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer, puis ✅ pour "
                f"lancer "
                f"la partie"):
            await member.remove_roles(role)
            await member.remove_roles(role2)
            await channel.send(f"{member.mention} est désinscrit".format(member))
        if "Faites le bon choix" in msg.content:
            # await var_add(guild, member)
            await add_var(guild, member, -2)
            with open("vars.json", "r") as f:
                vars = json.load(f)
            vote = vars[str(member.id)]["vote"]
            if vote < 0:
                await add_var(guild, member, 1)
    else:
        return


# Création d'un salon textuel
@bot.command(name="setup")
async def setup(ctx):
    await botsetup(ctx, "None")


# Fonction de desetup
@bot.command(name="desetup")
async def desetup(ctx):
    await unmute_all(ctx)
    await botdesetup(ctx, "None")


# Affichage des commandes
@bot.command(name="aled")
async def aled(ctx):
    embed = discord.Embed(title="as-tu besoin d'aide ?", description="regarde tes mps 😉", color=0xFF0000)
    await ctx.send(embed=embed)
    await ctx.author.send("voici les commandes que tu peux utiliser :".format(ctx))
    await ctx.author.send("- `!setup` permet de créer les channels".format(ctx))
    await ctx.author.send("- `!desetup` permet de supprimer les channels créé par le bot".format(ctx))
    await ctx.author.send("- `!aled` pour avoir la liste des commandes".format(ctx))
    await ctx.author.send("- `!roles` pour avoir la description des rôles".format(ctx))


# Message privé des rôles
@bot.command(name="roles")
async def roles(message):
    await message.author.send("Loup-Garou:\n"
                              "Vaincre les villageois est son objectif. Durant la nuit les loups-garous se réunissent "
                              "pour voter qui va être éliminé. Pendant la journée il ne doit pas être démasqué.\n "
                              "• Le Loup-Garou est appelé une fois par nuit. Il peut discuter avec les autres loups "
                              "durant leur phase de vote.\n "
                              "• Si le vote mène sur une égalité ou si les Loups ne ciblent personne"
                              "Aucun joueur ne meurt\n\n"
                              "Simple Villageois:\n"
                              "Vaincre les loups-garous est son objectif. Sa parole est son seul pouvoir de "
                              "persuasion pour les éliminer. Restez à l'affût d'indice, et identifiez les "
                              "coupables.\n"
                              "• En cas d'égalité lors du vote journalier et si aucun maire n'est élu, aucun joueur "
                              "ne meurt.\n "
                              "• Les votes des Simples Villageois peuvent être décisifs dans la lutte contre les "
                              "Loups-Garous.\n\n"
                              "Voyante:\n"
                              "Vaincre les loups-garous est son objectif. Chaque nuit elle peut connaître le rôle "
                              "d'un joueur qu'elle aura choisi. Elle doit aider les villageois sans se faire "
                              "démasquer.\n"
                              "• Utilise ton pouvoir chaque nuit en cliquant sur le joueur de ton choix pour "
                              "connaître son rôle.\n"
                              "• Copier le texte indiquant le rôle du joueur observé est considéré comme anti-jeu.\n\n"
                              "Chasseur:\n"
                              "Son objectif est de vaincre les Loups-Garous. Lorsque le Chasseur meurt, il a le "
                              "pouvoir d'amener un autre joueur avec lui dans sa tombe.\n "
                              "• Le Chasseur a la possibilité de ne tuer personne à sa mort s'il trouve cette option "
                              "stratégique.\n\n")


# Commande pour effacer des messages dans un channel
@bot.command(name="del")
async def delete(ctx, number: int):
    messages = await ctx.channel.history(limit=number + 1).flatten()

    for each_message in messages:
        await each_message.delete()


async def sup(channel):
    messages = await channel.history().flatten()
    for message in messages:
        if "Il vous reste" in message.content:
            await message.delete()


# Ping (pong)
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


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


async def choix_lg(ctx):
    i = 0
    liste = await liste_id_participant(ctx)
    x = 0
    participant = len(liste)
    while x < len(liste):
        await add_role(ctx, liste[x], 1)
        await add_role2(ctx, liste[x], 1)
        x = x + 1
    random.shuffle(liste)
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    j = round(len(liste) / 5)
    text = "Les loup-garous sont: "
    if j == 0:
        j = 1
    while i < j:
        choice = liste.pop()
        user = bot.get_user(choice.id)
        await add_role(ctx, user, 2)
        await add_role2(ctx, user, 2)
        await assigner_lg(ctx, user)
        text = text + "<@" + str(user.id) + ">" + " "
        i = i + 1
    await channel.send(text.format(ctx))
    channel = discord.utils.get(ctx.guild.text_channels, name='voyante')
    choice = liste.pop()
    user = bot.get_user(choice.id)
    await add_role(ctx, user, 1)
    await add_role2(ctx, user, 1)
    await assigner_voyante(ctx, user)
    text2 = "La voyante est : "
    text2 = text2 + "<@" + str(user.id) + ">" + " "
    await channel.send(text2.format(ctx))
    if len(liste) >= 5:
        channel = discord.utils.get(ctx.guild.text_channels, name='chasseur')
        choice = liste.pop()
        user = bot.get_user(choice.id)
        await add_role(ctx, user, 3)
        await add_role2(ctx, user, 3)
        await assigner_voyante(ctx, user)
        text2 = "Le Chasseur est : "
        text2 = text2 + "<@" + str(user.id) + ">" + " "
        await channel.send(text2.format(ctx))
        channel = discord.utils.get(ctx.guild.text_channels, name='village')
        villageois = participant - i - 2
        await channel.send("Il y a " + str(villageois) + " villageois, " + str(i) + " loup garou, une voyante et un chasseur")
        return liste
    else:
        channel = discord.utils.get(ctx.guild.text_channels, name='village')
        villageois = participant - i - 1
        await channel.send("Il y a " + str(villageois) + " villageois, " + str(i) + " loup garou et une voyante")
        return liste


async def assigner_lg(ctx, user):
    channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
    await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)


async def assigner_voyante(ctx, user):
    channel = discord.utils.get(ctx.guild.text_channels, name='voyante')
    await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)


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
        userr = await bot.fetch_user(user)
        if userr in ctx.guild.members:
            names += f'{postion + 1} - <@!{user}> avec {top_users[user]["points"]} points \n'
    embed = discord.Embed(title=f'Classement dans le serveur: {ctx.guild.name}')
    embed.add_field(name="NOM", value=names, inline=False)
    await ctx.send(embed=embed)


async def kill(ctx, user: discord.User, tmp):
    guild = ctx.guild
    member = guild.get_member(user.id)
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    role2 = discord.utils.get(ctx.guild.roles, name='Mort')
    await member.remove_roles(role)
    await member.add_roles(role2)
    with open("vars.json", "r") as f:
        vars = json.load(f)
    role = vars[str(member.id)]["role"]
    if role == 4:
        role2 = "Chasseur"
        channel = discord.utils.get(ctx.guild.text_channels, name='chasseur')
        if tmp == "debut_jour":
            await sondage(channel, 10, 3, "chasseur_debut")
        if tmp == "fin_jour":
            await sondage(channel, 10, 3, "chasseur_fin")
    if role == 3:
        channel = discord.utils.get(ctx.guild.text_channels, name='loup-garou')
        await channel.set_permissions(user, read_messages=True, send_messages=False, view_channel=True)
        role2 = "loup garou"
    if role == 2:
        role2 = "voyante"
    if role == 1:
        role2 = "villageois"
    while role >= 1:
        await add_role(guild, member, -1)
        role = role - 1
    return role2


async def check_role(ctx, user: discord.User):
    guild = ctx.guild
    member = guild.get_member(user.id)
    with open("vars.json", "r") as f:
        vars = json.load(f)
    role = vars[str(member.id)]["role"]
    channel = discord.utils.get(ctx.guild.text_channels, name='voyante')
    if role == 1:
        await channel.send(member.name + " est villageois 🧍")
    if role == 2:
        await channel.send(member.name + " est voyante 🧙")
    if role == 3:
        await channel.send(member.name + " est loup garou 🐺")
    if role == 4:
        await channel.send(member.name + " est chasseur 🔫")
    await sup(channel)


async def mute(ctx, setting):
    voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
    role = discord.utils.get(ctx.guild.roles, name='Mort')
    for member in voice_channel.members:
        if setting.lower() == 'true':
            await member.edit(mute=True)
        elif setting.lower() == 'false':
            if role not in member.roles:
                await member.edit(mute=False)


async def unmute_all(ctx):
    voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
    for member in voice_channel.members:
        await member.edit(mute=False)


async def sondage(ctx, x, y, day):
    global msg_cim, liste_cim
    liste = await liste_id_villageois(ctx)
    liste2 = await liste_id_mort(ctx)
    liste_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '❤', '🧡', '💛', '💚', '💙', '💜', '🤎', '🤍']
    nb = await count_villageois(ctx)
    lst = [0] * nb
    i = 0
    guild = ctx.guild
    text = ""
    j = 0
    while j != len(liste2):
        await add_var(ctx, liste2[j], 0)
        with open("vars.json", "r") as f:
            vars = json.load(f)
        vote = vars[str(liste2[j].id)]["vote"]
        if vote > 0:
            await add_var(guild, liste2[i], -1)
        j += 1
    while i != len(liste):
        await add_var(ctx, liste[i], 0)
        with open("vars.json", "r") as f:
            vars = json.load(f)
        vote = vars[str(liste[i].id)]["vote"]
        if vote > 0:
            await add_var(guild, liste[i], -1)
        text = text + liste[i].name + " " + liste_emoji[i] + "\n"
        i += 1
    text = text + "Faites le bon choix"
    msg = await ctx.send(text)
    i = 0
    while i != len(liste):
        await msg.add_reaction(liste_emoji[i])
        i += 1
    if day == "nuit":
        await nuit_un_timer(ctx, int(x), int(y), msg)
    if day == "cimetiere":
        msg_cim, liste_cim = await cimetiere_timer(ctx, int(x), int(y), msg)
    if day == "jour":
        await jour_timer(ctx, int(x), int(y), msg, msg_cim, liste_cim)
    if day == "voyante":
        await voyante_timer(ctx, int(x), int(y), msg)
    if day == "chasseur_fin":
        await chasseur_timer(ctx, int(x), int(y), msg, "fin")
    if day == "chasseur_debut":
        await chasseur_timer(ctx, int(x), int(y), msg, "debut")


# -- A partir d'ici ce sont les fonctions appeler par le bot --

async def nuit_un_timer(ctx, time: int, count: int, msg):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(nuit_un_end_loop(ctx, msg))
    l.start(l)


async def chasseur_timer(ctx, time: int, count: int, msg, tmp):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(chasseur_end_loop(ctx, msg, tmp))
    l.start(l)


async def voyante_timer(ctx, time: int, count: int, msg):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(voyante_end_loop(ctx, msg))
    l.start(l)


async def cimetiere_timer(ctx, time: int, count: int, msg):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(cimetiere_end_loop(ctx, msg))
    l.start(l)
    liste = await liste_id_villageois(ctx)
    return msg, liste


def chasseur_end_loop(ctx, msg, tmp):
    async def coro():
        guild = ctx.guild
        liste = await liste_id_villageois(ctx)
        await ctx.send("Le temps est écoulé ! J'espère que votre choix vous sera bénéfique ! ✨")
        channel_chasseur = discord.utils.get(guild.text_channels, name='chasseur')
        await sup(channel_chasseur)
        channel_village = discord.utils.get(guild.text_channels, name='village')
        x, pos = await count_react(ctx, msg)
        await channel_village.send("Le Chasseur à décider...")
        channel = discord.utils.get(ctx.guild.text_channels, name='village')
        role = discord.utils.get(ctx.guild.roles, name='Villageois')
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
        voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
        if x >= 1:
            await channel_village.send("Il y a une égalité et personne ne meurt :🤔")
            await mute(voice_channel, "false")
            if tmp == "debut":
                await channel_village.send("Le village commence a débattre 📩")
                await timer_invisible(channel_village, 10, 3, "fin nuit 🌙")
            if tmp == "fin":
                await channel_village.send(
                    "C’est la nuit, tout le village s’endort, les joueurs ferment leurs micros 🎙️")
                channel = discord.utils.get(ctx.guild.text_channels, name='village')
                role = discord.utils.get(ctx.guild.roles, name='Villageois')
                await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True)
                voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
                await mute(voice_channel, "true")
                liste = await liste_id_participant(ctx)
                i = 0
                voyante = 0
                while i != len(liste):
                    await add_var(ctx, liste[i], 0)
                    with open("vars.json", "r") as f:
                        vars = json.load(f)
                    role = vars[str(liste[i].id)]["role"]
                    if role == 2:
                        voyante = 1
                    i = i + 1
                if voyante == 1:
                    await channel_village.send("La voyante se reveille pour decouvrit le role d'un joueur 👀")
                    channel_voyante = discord.utils.get(guild.text_channels, name='voyante')
                    await sondage(channel_voyante, 5, 3, "voyante")
                else:
                    await channel_village.send(
                        "Les Loups-Garous se réveillent, se reconnaissent et désignent une nouvelle victime !!! 🐺")
                    channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
                    await sondage(channel_lg, 10, 3, "nuit")
                    cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
                    await sondage(cimetiere, 10, 3, "cimetiere")
        else:
            role = await kill(ctx, liste[pos], "debut_jour")
            if role != "Chasseur":
                await channel_village.send(f"{liste[pos].mention} est mort, le rôle était {role}".format(ctx))
                await mute(voice_channel, "false")
                x = await check_fin(ctx)
                if x == 1:
                    await unmute_all(ctx)
                    await channel_village.send("La partie est terminée")
                    await classement(channel_village)
                    msg2 = await channel_village.send("Voulez-vous relancer une partie ?")
                    await msg2.add_reaction('✅')
                    await msg2.add_reaction('❌')
                    return -1
                else:
                    if tmp == "debut":
                        await channel_village.send("Le village commence a débattre 📩")
                        await timer_invisible(channel_village, 10, 3, "fin nuit 🌙")
                    if tmp == "fin":
                        await channel_village.send(
                            "C’est la nuit, tout le village s’endort, les joueurs ferment leurs micros 🎙️")
                        channel = discord.utils.get(ctx.guild.text_channels, name='village')
                        role = discord.utils.get(ctx.guild.roles, name='Villageois')
                        await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True)
                        voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
                        await mute(voice_channel, "true")
                        liste = await liste_id_participant(ctx)
                        i = 0
                        voyante = 0
                        while i != len(liste):
                            await add_var(ctx, liste[i], 0)
                            with open("vars.json", "r") as f:
                                vars = json.load(f)
                            role = vars[str(liste[i].id)]["role"]
                            if role == 2:
                                voyante = 1
                            i = i + 1
                        if voyante == 1:
                            await channel_village.send("La voyante se reveille pour decouvrit le role d'un joueur 👀")
                            channel_voyante = discord.utils.get(guild.text_channels, name='voyante')
                            await sondage(channel_voyante, 5, 3, "voyante")
                        else:
                            await channel_village.send(
                                "Les Loups-Garous se réveillent, se reconnaissent et désignent une nouvelle victime !!! 🐺")
                            channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
                            await sondage(channel_lg, 10, 3, "nuit")
                            cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
                            await sondage(cimetiere, 10, 3, "cimetiere")
            else:
                await channel_village.send(f"{liste[pos].mention} est mort, le rôle était {role}".format(ctx))
                await channel_village.send(f"Il se prépare a tirer".format(ctx))
    return coro


def cimetiere_end_loop(ctx, msg):
    async def coro():
        guild = ctx.guild
        channel = discord.utils.get(guild.text_channels, name='cimetiere')
        role = discord.utils.get(ctx.guild.roles, name='Mort')
        await channel.set_permissions(role, read_messages=False, send_messages=False, view_channel=False)
    return coro


def voyante_end_loop(ctx, msg):
    async def coro():
        guild = ctx.guild
        liste = await liste_id_villageois(ctx)
        channel_village = discord.utils.get(guild.text_channels, name='village')
        x, pos = await count_react(ctx, msg)
        channel_voyante = discord.utils.get(ctx.guild.text_channels, name='voyante')
        await check_role(channel_voyante, liste[pos])
        await channel_village.send("La voyante se rendort après avoir decouvert le role d'un joueur👀")
        await channel_village.send("Les Loups-Garous se réveillent, se reconnaissent et désignent une victime !🐺")
        channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
        await sondage(channel_lg, 10, 3, "nuit")
        cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
        await sondage(cimetiere, 10, 3, "cimetiere")
    return coro


async def jour_timer(ctx, time: int, count: int, msg, msg_cim, liste_cim):
    l = tasks.Loop(loop(ctx), time, 0, 0, count, True, None)
    l.after_loop(jour_end_loop(ctx, msg, msg_cim, liste_cim))
    l.start(l)


def jour_end_loop(ctx, msg, msg_cim, liste_cim):
    async def coro():
        guild = ctx.guild
        liste = await liste_id_villageois(ctx)
        await ctx.send("Le temps est écoulé ! J'espère que votre choix vous sera bénéfique ! ✨")
        channel_village = discord.utils.get(guild.text_channels, name='village')
        channel_cim = discord.utils.get(guild.text_channels, name='cimetiere')
        await sup(channel_village)
        await sup(channel_cim)
        await nom_react(ctx, msg)
        x, pos = await count_react(ctx, msg)
        await channel_village.send("Le Village a fait son choix 🪓")
        if x >= 1:
            await channel_village.send("Il y a une égalité et personne ne meurt 🤔")
            cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
            role = discord.utils.get(ctx.guild.roles, name='Mort')
            await cimetiere.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
            await channel_village.send("C’est la nuit, tout le village s’endort, les joueurs ferment leurs micros 🎙️")
            channel = discord.utils.get(ctx.guild.text_channels, name='village')
            role = discord.utils.get(ctx.guild.roles, name='Villageois')
            await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True)
            voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
            await mute(voice_channel, "true")
            liste = await liste_id_participant(ctx)
            i = 0
            voyante = 0
            while i != len(liste):
                await add_var(ctx, liste[i], 0)
                with open("vars.json", "r") as f:
                    vars = json.load(f)
                role = vars[str(liste[i].id)]["role"]
                if role == 2:
                    voyante = 1
                i = i + 1
            if voyante == 1:
                await channel_village.send("La voyante se reveille pour decouvrit le role d'un joueur 👀")
                channel_voyante = discord.utils.get(guild.text_channels, name='voyante')
                await sondage(channel_voyante, 5, 3, "voyante")
            else:
                await channel_village.send(
                    "Les Loups-Garous se réveillent, se reconnaissent et désignent une nouvelle victime !!! 🐺")
                channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
                await sondage(channel_lg, 10, 3, "nuit")
                cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
                await sondage(cimetiere, 10, 3, "cimetiere")
        else:
            role = await kill(ctx, liste[pos], "fin_jour")
            if role != "Chasseur":
                cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
                role2 = discord.utils.get(ctx.guild.roles, name='Mort')
                await cimetiere.set_permissions(role2, read_messages=True, send_messages=True, view_channel=True)
                await verif_cimetiere(ctx, liste[pos], msg_cim, liste_cim)
                await channel_village.send(f"{liste[pos].mention} est mort, il était {role}".format(ctx))
                x = await check_fin(ctx)
                if x == 1:
                    await unmute_all(ctx)
                    await channel_village.send("La partie est terminée")
                    await classement(channel_village)
                    msg2 = await channel_village.send("Voulez-vous relancer une partie ?")
                    await msg2.add_reaction('✅')
                    await msg2.add_reaction('❌')
                    return -1
                else:
                    await channel_village.send("C’est la nuit, tout le village s’endort, les joueurs ferment leurs micros 🎙️")
                    channel = discord.utils.get(ctx.guild.text_channels, name='village')
                    role = discord.utils.get(ctx.guild.roles, name='Villageois')
                    await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True)
                    voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
                    await mute(voice_channel, "true")
                    liste = await liste_id_participant(ctx)
                    i = 0
                    voyante = 0
                    while i != len(liste):
                        await add_var(ctx, liste[i], 0)
                        with open("vars.json", "r") as f:
                            vars = json.load(f)
                        role = vars[str(liste[i].id)]["role"]
                        if role == 2:
                            voyante = 1
                        i = i + 1
                    if voyante == 1:
                        await channel_village.send("La voyante se reveille pour decouvrit le role d'un joueur 👀")
                        channel_voyante = discord.utils.get(guild.text_channels, name='voyante')
                        await sondage(channel_voyante, 5, 3, "voyante")
                    else:
                        await channel_village.send(
                            "Les Loups-Garous se réveillent, se reconnaissent et désignent une nouvelle victime !!! 🐺")
                        channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
                        await sondage(channel_lg, 10, 3, "nuit")
                        cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
                        await sondage(cimetiere, 10, 3, "cimetiere")
            else:
                await channel_village.send(f"{liste[pos].mention} est mort, le rôle était {role}".format(ctx))
                await channel_village.send(f"Il se prépare a tirer".format(ctx))
    return coro


async def tiiime(ctx, x, y):
    await timer_invisible(ctx, int(x), int(y), None)


async def timer_invisible(ctx, time: int, count: int, msg):
    l = tasks.Loop(loop_invisible(ctx), time, 0, 0, count, True, None)
    l.after_loop(end_loop_invisible(ctx, msg))
    l.start(l)


def loop_invisible(ctx):
    async def coro(l: tasks.Loop):
        x = 0
    return coro


def end_loop_invisible(ctx, msg):
    async def coro():
        channel = discord.utils.get(ctx.guild.text_channels, name='village')
        await channel.send("C'est le moment de voter 📩")
        await sondage(channel, 10, 6, "jour")
    return coro


def loop(ctx):
    async def coro(l: tasks.Loop):
        await ctx.send(f"Il vous reste {((l.seconds * l.count) - (l.current_loop * l.seconds))}s")

    return coro


async def verif_cimetiere(ctx, mort, msg, liste_cim):
    guild = ctx.guild
    cimetiere = discord.utils.get(guild.text_channels, name='cimetiere')
    i = 0
    while liste_cim[i] != mort:
        i = i + 1
    liste_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '❤', '🧡', '💛', '💚', '💙', '💜', '🤎', '🤍']
    emojii = liste_emoji[i]
    m = await cimetiere.fetch_message(msg.id)
    react = discord.utils.get(m.reactions, emoji=emojii)
    users = await react.users().flatten()
    text = ""
    for user in users:
        if user != bot.user:
            await add_xp2(ctx, user, 1)
            text = text + user.name + " "
    text = text + " ont gagné de l'xp"
    await cimetiere.send(text)
    await msg.delete()


def nuit_un_end_loop(ctx, msg):
    async def coro():
        guild = ctx.guild
        liste = await liste_id_villageois(ctx)
        await ctx.send("Le temps est écoulé ! J'espère que votre choix vous sera bénéfique ! ✨")
        channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
        await sup(channel_lg)
        channel_village = discord.utils.get(guild.text_channels, name='village')
        x, pos = await count_react(ctx, msg)
        await channel_village.send("Les Loups-Garous repus se rendorment et rêvent de prochaines victimes savoureuses "
                                   "🐺")
        await channel_village.send("Le Village se réveille et apprend que durant la nuit 🌙:")
        channel = discord.utils.get(ctx.guild.text_channels, name='village')
        role = discord.utils.get(ctx.guild.roles, name='Villageois')
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
        voice_channel = discord.utils.get(ctx.guild.channels, name="Village_vocal")
        if x >= 1:
            await channel_village.send("Il y a une égalité et personne ne meurt :🤔")
            await mute(voice_channel, "false")
            await channel_village.send("Le village commence a débattre 📩")
            await timer_invisible(channel_village, 10, 3, "fin nuit 🌙")
        else:
            role = await kill(ctx, liste[pos], "debut_jour")
            if role != "Chasseur":
                await channel_village.send(f"{liste[pos].mention} est mort, le rôle était {role}".format(ctx))
                await mute(voice_channel, "false")
                x = await check_fin(ctx)
                if x == 1:
                    await unmute_all(ctx)
                    await channel_village.send("La partie est terminée")
                    await classement(channel_village)
                    msg2 = await channel_village.send("Voulez-vous relancer une partie ?")
                    await msg2.add_reaction('✅')
                    await msg2.add_reaction('❌')
                    return -1
                else:
                    await channel_village.send("Le village commence a débattre 📩")
                    await timer_invisible(channel_village, 10, 3, "fin nuit 🌙")
            else:
                await channel_village.send(f"{liste[pos].mention} est mort, le rôle était {role}".format(ctx))
                await channel_village.send(f"Il se prépare a tirer".format(ctx))
    return coro


async def nom_react(ctx, msg):
    liste = await liste_id_villageois(ctx)
    liste_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '❤', '🧡', '💛', '💚', '💙', '💜', '🤎', '🤍']
    v = 0
    text = ""
    channel = discord.utils.get(ctx.guild.text_channels, name='village')
    while v < len(liste):
        emojii = liste_emoji[v]
        m = await ctx.fetch_message(msg.id)
        react = discord.utils.get(m.reactions, emoji=emojii)
        users = await react.users().flatten()
        text = text + liste[v].name + " a été voté par : "
        a = react.count
        if a > 1:
            for user in users:
                if user != bot.user:
                    text = text + user.name + " "
            await channel.send(text)
        text = " "
        v = v + 1


async def count_react(ctx, msg):
    liste = await liste_id_villageois(ctx)
    liste_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '❤', '🧡', '💛', '💚', '💙', '💜', '🤎', '🤍']
    nb = await count_villageois(ctx)
    lst = [0] * nb
    v = 0
    while v < len(liste):
        emojii = liste_emoji[v]
        m = await ctx.fetch_message(msg.id)
        react = discord.utils.get(m.reactions, emoji=emojii)
        a = react.count
        lst[v] += a
        v = v + 1
    i = 0
    j = lst[i]
    i = 1
    x = 0
    pos = 0
    while i != len(lst):
        if lst[i] == j:
            x = x + 1
        if lst[i] > j:
            pos = i
            j = lst[i]
            x = 0
        i = i + 1
    await msg.delete()
    return x, pos


async def count_villageois(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    return len(role.members)


async def liste_id_participant(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Participant')
    return role.members


async def liste_id_mort(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Mort')
    return role.members


async def liste_id_villageois(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    return role.members


async def botdesetup(ctx, par):
    guild = ctx.guild
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    await role.delete()
    role = discord.utils.get(ctx.guild.roles, name="Participant")
    await role.delete()
    role = discord.utils.get(ctx.guild.roles, name="Mort")
    await role.delete()
    if par != "new game":
        channel = discord.utils.get(guild.channels, name='Village_vocal')
        await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='village')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='chasseur')
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


async def botsetup(ctx, par):
    role = discord.utils.get(ctx.guild.roles, name="Mort")
    if role is None:
        await ctx.guild.create_role(name="Mort", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été crée")
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    if role is None:
        await ctx.guild.create_role(name="Villageois", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été crée")
    role = discord.utils.get(ctx.guild.roles, name="Participant")
    if role is None:
        await ctx.guild.create_role(name="Participant", mentionable=True)
    else:
        await ctx.send(f"Le rôle a déjà été crée")
    guild = ctx.guild
    if par != "new game":
        channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
        if channel_vocal is None:
            await guild.create_voice_channel('Village_vocal')
            channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
            await channel_vocal.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False,
                                                view_channel=False)
            role = discord.utils.get(ctx.guild.roles, name="Villageois")
            await channel_vocal.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
            role = discord.utils.get(ctx.guild.roles, name="Mort")
            await channel_vocal.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
        else:
            await ctx.send(f"Le vocal a déjà été crée")
    channel = discord.utils.get(guild.text_channels, name='village')
    if channel is None:
        channel = await guild.create_text_channel('village')
        msg = await channel.send(
            f"Les salons ont bien été créés, merci de réagir avec : ➕ à ce messsage pour participer, puis ✅ pour "
            f"lancer "
            f"la partie")
        role = discord.utils.get(ctx.guild.roles, name="Participant")
        await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True,
                                      add_reactions=False)
        role = discord.utils.get(ctx.guild.roles, name="Villageois")
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True,
                                      add_reactions=True)
        await msg.add_reaction('➕')
        await msg.add_reaction('✅')
    else:
        await ctx.send(f"village est déjà crée")
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    if channel is None:
        channel = await guild.create_text_channel('loup-garou')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"loup-garou est déjà crée")
    channel = discord.utils.get(guild.text_channels, name='cimetiere')
    if channel is None:
        channel = await guild.create_text_channel('cimetiere')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name="Mort")
        await channel.set_permissions(role, read_messages=True, send_messages=True, view_channel=True)
    else:
        await ctx.send(f"cimetiere est déjà crée")
    channel = discord.utils.get(guild.text_channels, name='cupidon')
    if channel is None:
        channel = await guild.create_text_channel('cupidon')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"cupidon est déjà crée")
    channel = discord.utils.get(guild.text_channels, name='sorciere')
    if channel is None:
        channel = await guild.create_text_channel('sorciere')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"sorciere est déjà crée")
    channel = discord.utils.get(guild.text_channels, name='voyante')
    if channel is None:
        channel = await guild.create_text_channel('voyante')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"voyante est déjà crée")
    channel = discord.utils.get(guild.text_channels, name='chasseur')
    if channel is None:
        channel = await guild.create_text_channel('chasseur')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
    else:
        await ctx.send(f"chasseur est déjà crée")


async def nuit_un(ctx):
    guild = ctx.guild
    channel_village = discord.utils.get(guild.text_channels, name='village')
    channel_lg = discord.utils.get(guild.text_channels, name='loup-garou')
    channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
    role_villageois = discord.utils.get(ctx.guild.roles, name="Villageois")
    i = 0
    liste = await liste_id_villageois(ctx)
    while i != len(liste):
        await add_var(ctx, liste[i], 0)
        with open("vars.json", "r") as f:
            vars = json.load(f)
        role = vars[str(liste[i].id)]["role"]
        while role > 0:
            await add_role(guild, liste[i], -1)
            role = role - 1
        role2 = vars[str(liste[i].id)]["role2"]
        while role2 > 0:
            await add_role2(guild, liste[i], -1)
            role2 = role2 - 1
        i += 1
    await choix_lg(channel_village)
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
    await channel_village.send("C’est la nuit, tout le village s’endort, les joueurs ferment leurs micros")
    channel = discord.utils.get(ctx.guild.text_channels, name='village')
    role = discord.utils.get(ctx.guild.roles, name='Villageois')
    await channel.set_permissions(role, read_messages=True, send_messages=False, view_channel=True)
    await mute(channel_vocal, "true")
    await channel_village.send("La voyante se reveille pour decouvrit le role d'un joueur")
    channel_voyante = discord.utils.get(guild.text_channels, name='voyante')
    await sondage(channel_voyante, 5, 3, "voyante")


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


async def check_fin(ctx):
    liste = await liste_id_participant(ctx)
    channel_village = discord.utils.get(ctx.guild.text_channels, name='village')
    i = 0
    lg = 0
    villageois = 0
    while i != len(liste):
        await add_var(ctx, liste[i], 0)
        with open("vars.json", "r") as f:
            vars = json.load(f)
        role = vars[str(liste[i].id)]["role"]
        if role == 3:
            lg = lg + 1
        if role == 1 or role == 2:
            villageois = villageois + 1
        if role == 4:
            villageois = villageois + 2
        i = i + 1
    if lg > villageois:
        x = 0
        while x < len(liste):
            with open("vars.json", "r") as f:
                vars = json.load(f)
            role2 = vars[str(liste[x].id)]["role2"]
            if role2 == 3:
                if liste[x].id != bot.user.id:
                    await add_xp2(ctx, liste[x], 6)
            else:
                if liste[x].id != bot.user.id:
                    await add_xp2(ctx, liste[x], 2)
            x = x + 1
        await channel_village.send("Les loup garous ont gagné")
        return 1
    if lg == 0:
        x = 0
        while x < len(liste):
            with open("vars.json", "r") as f:
                vars = json.load(f)
            role2 = vars[str(liste[x].id)]["role2"]
            if role2 == 3:
                if liste[x].id != bot.user.id:
                    await add_xp2(ctx, liste[x], 2)
            else:
                if liste[x].id != bot.user.id:
                    await add_xp2(ctx, liste[x], 6)
            x = x + 1
        await channel_village.send("Les villageois ont gagné")
        return 1
    if villageois >= lg:
        return 0


bot.run(os.getenv("TOKEN"))
