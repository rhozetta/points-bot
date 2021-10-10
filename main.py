import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component, ComponentContext, create_select_option, create_select
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import ButtonStyle, SlashCommandPermissionType
import json

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix="eat my nuts")
slash = SlashCommand(client, sync_commands=True,sync_on_cog_reload = True)

with open("tokenfile", "r") as tokenfile:
    token=tokenfile.read()

buttons1 = [create_button(style=ButtonStyle.red, label="refund",custom_id="refund"), create_button(style=ButtonStyle.green, label="mark as done",custom_id="done")]
mod_action_row = create_actionrow(*buttons1)

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

@client.event
async def on_guild_join(guild):

    internetfunny = discord.utils.get(client.guilds, id=766848554899079218)
    bots = discord.utils.get(internetfunny.channels, id=782228427880267776)

    await bots.send(f"i just joined a guild called **{guild.name}** and it has *{len(guild.members)}* members")

    modchannel = None
    for x in guild.channels:
        try:
            await x.send("i will use this channel as the one to post when a user redeems something, if this is not a good channel use /modchannel and change it")
            modchannel = x
            break
        except:
            continue

    with open("modchannels.json","r") as channelsraw:
        channels = json.loads(channelsraw.read())
    with open("modchannels.json","w") as channelsraw:
        channels[str(guild.id)] = modchannel.id
        channelsraw.write(json.dumps(channels))

@client.event
async def on_guild_remove(guild):

    internetfunny = discord.utils.get(client.guilds, id=766848554899079218)
    bots = discord.utils.get(internetfunny.channels, id=782228427880267776)

    await bots.send(f"i just left a guild called **{guild.name}** and it had *{len(guild.members)}* members")

@slash.slash()
async def invite(ctx):
	await ctx.send("https://discord.com/api/oauth2/authorize?client_id=737035126222880881&permissions=68608&scope=bot%20applications.commands", hidden=True)

@slash.slash()
async def points(ctx, hidden:bool=True):
    with open("points.json", "r") as pointsraw:
        points = json.loads(pointsraw.read())

    server = str(ctx.guild.id)
    user = str(ctx.author.id)

    try:
        points = points[server][user]
    except KeyError:
        points = 0

    await ctx.send(f"you have {points} points in this guild", hidden=hidden)

@slash.slash()
async def addreward(ctx, name:str, cost:int, hidden:bool=True):
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.send("you dont have permission to use this command",hidden=True)
        return
    if cost <= 0:
        await ctx.send("please choose a cost that is higher than 0", hidden=True)

    with open("rewards.json","r") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    server = str(ctx.guild.id)

    try:
        rewards[server][name] = cost
    except KeyError:
        rewards[server] = {}
        rewards[server][name] = cost

    with open("rewards.json","w") as rewardsraw:
        rewardsraw.write(json.dumps(rewards))

    await ctx.send(f"you made a new reward titled `{name}` that costs `{cost}` points", hidden=hidden)

@slash.slash()
async def removereward(ctx):
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.send("you dont have permission to use this command",hidden=True)
        return
    
    with open("rewards.json","r") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    server = str(ctx.guild.id)


    try:
        rewards = rewards[server]
    except KeyError:
        await ctx.send("this guild has no rewards set", hidden=True)
        return

    options = []
    for x in rewards:
        options.append(create_select_option(f"{x} - {rewards[x]} points", value=x))
    
    if options == []:
        await ctx.send("this guild has no rewards set", hidden=True)
        return
    
    select = create_select(options, placeholder="choose a reward", min_values=1,custom_id="remove")
    selectionrow = create_actionrow(select)
    await ctx.send("choose a reward to remove", components=[selectionrow], hidden=True)

@slash.slash()
async def redeem(ctx, hidden:bool=True):
    with open("rewards.json","r") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    server = str(ctx.guild.id)

    try:
        rewards = rewards[server]
    except KeyError:
        await ctx.send("this guild has no rewards set", hidden=True)
        return

    options = []
    for x in rewards:
        options.append(create_select_option(f"{x} - {rewards[x]} points", value=x))
    
    if options == []:
        await ctx.send("this guild has no rewards set", hidden=True)
        return
    
    select = create_select(options, placeholder="choose a reward", min_values=1,custom_id="redeem")
    selectionrow = create_actionrow(select)
    await ctx.send("choose a reward", components=[selectionrow], hidden=hidden)
    
@slash.slash()
async def modchannel(ctx, channel:discord.TextChannel):
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.send("you dont have permission to use this command",hidden=True)
        return
    if not type(channel) == discord.channel.TextChannel:
        await ctx.send("you need to specify a text channel, not a category or voice channel", hidden=True)

    with open("modchannels.json","r") as channelsraw:
        channels = json.loads(channelsraw.read())

    server = str(ctx.guild.id)
    channels[server] = channel.id

    with open("modchannels.json","w") as channelsraw:
        channelsraw.write(json.dumps(channels))

    await ctx.send(f"changed the mod channel to {channel.mention}",hidden=True)
    await channel.send(f"{ctx.author.display_name} changed the mod channel to this channel")

@slash.component_callback(components=["redeem"])
async def redeemcallback(ctx):
    with open("rewards.json") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    with open("points.json") as pointsraw:
        points = json.loads(pointsraw.read())

    server = str(ctx.guild.id)
    user = str(ctx.author.id)

    reward = ctx.selected_options[0]

    options = []
    for x in rewards:
        options.append(create_select_option(f"{x} - {rewards[x]} points", value=x))
    
    select = create_select(options, placeholder="choose a reward", min_values=1,custom_id="redeem")
    selectionrow = create_actionrow(select)
    await ctx.edit_origin(content="choose a reward",components=[selectionrow],hidden=True)

    try:
        points[server][user] -= rewards[server][reward]

        await ctx.send(f"{ctx.author.display_name} redeemed {reward} for {rewards[server][reward]} points",hidden=True)

        with open("modchannels.json","r") as channelsraw:
            channel = json.loads(channelsraw.read())
            channel = channel[server]
            channel = ctx.guild.get_channel(channel)

        await channel.send(f"{ctx.author.mention} redeemed {reward} for {rewards[server][reward]} points", components=[mod_action_row])
    except KeyError:
        await ctx.send("poor",hidden=True)

    with open("points.json","w") as pointsraw:
        pointsraw.write(json.dumps(points))

@slash.component_callback(components=["done"])
async def donecallback(ctx):
    await ctx.origin_message.delete()
    await ctx.send("marked that redeem as done")
    await user.send("your reward was fulfilled")

@slash.component_callback(components=["refund"])
async def refundcallback(ctx):
    with open("points.json","r") as pointsraw:
        points = json.loads(pointsraw.read())
    
    guild = str(ctx.guild.id)
    user = str(ctx.origin_message.mentions[0].id)

    content = ctx.origin_message.content.split(" ")
    cost = int(content[-2])

    points[guild][user] += cost

    with open("points.json","w") as pointsraw:
        pointsraw.write(json.dumps(points))

    user = ctx.origin_message.mentions[0]

    await ctx.send(f"refunded {cost} points to {user.display_name}", hidden=True)
    await user.send("your reward was refunded")
    await ctx.origin_message.delete()

@slash.component_callback(components=["remove"])
async def removecallback(ctx):
    with open("rewards.json","r") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    server = str(ctx.guild.id)

    del rewards[server][ctx.selected_options[0]]

    with open("rewards.json","w") as rewardsraw:
        rewardsraw.write(json.dumps(rewards))

    await ctx.send(f"removed {ctx.selected_options[0]} from this guild's rewards",hidden=True)

client.run(token)