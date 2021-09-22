import os

from discord import guild
from dotenv import load_dotenv
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
load_dotenv(dotenv_path="../code bot/config")


# login
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='!aled'))
    print('Logged in as')
    print('{0.user}'.format(bot))
    print('------')


# creation d'un channel textuel
@bot.command(name="setup")
async def setup(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    if role is None:
        await ctx.guild.create_role(name="Villageois", colour=0xFF0F00, mentionable=True)
    else:
        await ctx.send(f"Le rôle a deja été créer")
    guild = ctx.guild
    channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
    if channel_vocal is None:
        await guild.create_voice_channel('Village_vocal')
        channel_vocal = discord.utils.get(guild.channels, name='Village_vocal')
        await channel_vocal.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        role = discord.utils.get(ctx.guild.roles, name="Villageois")
        await channel_vocal.set_permissions(role, read_messages=True, send_messages=True)
    else:
        await ctx.send(f"Le vocal a deja été créer")
    channel = discord.utils.get(guild.text_channels, name='village')
    if channel is None:
        channel = await guild.create_text_channel('village')
        msg = await channel.send(
            f"Les salons ont bien été créer merci de réagir avec : ➕ a ce messsage pour participer et ✅ pour lancer "
            f"la partie")
        await msg.add_reaction('➕')
        await msg.add_reaction('✅')
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    if channel is None:
        channel = await guild.create_text_channel('loup-garou')
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)

    else:
        await ctx.send(f"Les salons de jeux ont deja ete creer")


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
        if msg.content == (f"Les salons ont bien été créer merci de réagir avec : ➕ a ce messsage pour participer et ✅ pour lancer "
        f"la partie"):
            await ctx.add_roles(role)
            await channel.send("{0.mention} est inscrit".format(ctx))
        else:
            print("autre channel add")
    if reaction.emoji == "✅":
        msg = await channel.fetch_message(reaction.message.id)
        await msg.delete()
        await channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
    channel = discord.utils.get(guild.text_channels, name='village')
    if payload.channel_id != channel.id:
        return
    role = discord.utils.get(guild.roles, name='Villageois')
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
    role = discord.utils.get(ctx.guild.roles, name="Villageois")
    await role.delete()
    channel = discord.utils.get(guild.channels, name='Village_vocal')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='village')
    await channel.delete()
    channel = discord.utils.get(guild.text_channels, name='loup-garou')
    await channel.delete()


@bot.command(name="aled")
async def aled(ctx):
    await ctx.author.send("voici les commandes que tu peux utiliser".format(ctx))
    await ctx.author.send("!setup permet de créer les channels ".format(ctx))
    await ctx.author.send("!desetup permet de supprimer les channels créer par le bot".format(ctx))
    await ctx.author.send("!aled pour avoir la liste des commandes".format(ctx))
    await ctx.channel.send("va voir tes mp".format(ctx))


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


bot.run(os.getenv("TOKEN"))
