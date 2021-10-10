import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component, ComponentContext, create_select_option, create_select
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import ButtonStyle, SlashCommandPermissionType
import json

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix="eat my nuts")
slash = SlashCommand(client, sync_commands=True,debug_guild=766848554899079218,sync_on_cog_reload = True)

with open("tokenfile", "r") as tokenfile:
    token=tokenfile.read()

@client.event
async def on_ready():
    print("hello world")

@client.event
async def on_message(message):
    with open("points.json", "r") as pointsraw:
        points = json.loads(pointsraw.read())

    server = str(message.guild.id)
    user = str(message.author.id)

    try:
        points[server][user] += 1
    except KeyError:
        try:
            points[server][user] = 1
        except KeyError:
            points[server] = {}
            points[server][user] = 1

    with open("points.json", "w") as pointsraw:
        pointsraw.write(json.dumps(points))

@slash.slash()
async def invite(ctx):
	await ctx.send("https://discord.com/api/oauth2/authorize?client_id=737035126222880881&permissions=68608&scope=bot%20applications.commands", hidden=True)

client.run(token)