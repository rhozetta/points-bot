import discord

import json

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

with open("tokenfile", "r") as tokenfile:
    token=tokenfile.read()

def getname(id):
    with open("names.json", "r") as namesraw:
        names = json.loads(namesraw.read())
        try:
            name = names[str(id)]
        except KeyError:
            name = "points"

    return name

def getoptions(ctx):
    with open("rewards.json","r") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    server = str(ctx.guild.id)
    rewards = rewards[server]

    options = []
    name = getname(ctx.guild.id)
    for x in rewards:
        options.append(discord.SelectOption(label=f"{x} - {rewards[x]} {name}", value=x))
    if options == []:
        return None
    return options

@bot.event
async def on_ready():
    print("hello world")

@bot.event
async def on_message(message):

    if message.author.bot:
        return

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

@bot.event
async def on_guild_join(guild):

    internetfunny = discord.utils.get(bot.guilds, id=987579392479858780)
    bots = discord.utils.get(internetfunny.channels, id=1023740794064097410)

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

@bot.event
async def on_guild_remove(guild):

    internetfunny = discord.utils.get(bot.guilds, id=987579392479858780)
    bots = discord.utils.get(internetfunny.channels, id=1023740794064097410)

    await bots.send(f"i just left a guild called **{guild.name}** and it had *{len(guild.members)}* members")

@bot.slash_command()
async def invite(ctx):
	await ctx.respond("https://discord.com/api/oauth2/authorize?client_id=737035126222880881&permissions=68608&scope=bot%20applications.commands", ephemeral=True)

@bot.slash_command()
async def points(ctx, user:discord.User=None, hidden:bool=True): 
    if user != bot.user:
        with open("points.json", "r") as pointsraw:
            points = json.loads(pointsraw.read())

        server = str(ctx.guild.id)
        if user is None:
            user = ctx.author

        try:
            points = points[server][str(user.id)]
        except KeyError:
            points = 0

        name = getname(ctx.guild.id)
        await ctx.respond(f"{user} has {points} {name} in this guild", ephemeral=hidden)
    else:
        await ctx.respond(f"I am in {len(bot.guilds)} servers", ephemeral=hidden)

@bot.slash_command()
async def addreward(ctx, name:str, cost:int, hidden:bool=True):
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.respond("you dont have permission to use this command",ephemeral=True)
        return
    if cost <= 0:
        await ctx.respond("please choose a cost that is higher than 0", ephemeral=True)

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

    pointsname = getname(ctx.guild.id)
    await ctx.respond(f"you made a new reward titled `{name}` that costs `{cost}` {pointsname}", ephemeral=hidden)

@bot.slash_command()
async def removereward(ctx):
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.respond("you dont have permission to use this command",ephemeral=True)
        return
    
    with open("rewards.json","r") as rewardsraw:
        rewards = json.loads(rewardsraw.read())

    server = str(ctx.guild.id)

    try:
        rewards = rewards[server]
        if rewards == []:
            await ctx.respond("this guild has no rewards set", ephemeral=True)
            return
    except KeyError:
        await ctx.respond("this guild has no rewards set", ephemeral=True)
        return

    options = getoptions(ctx)
    await ctx.respond("choose a reward to remove", view=RemoveViewFunc(options), ephemeral=True)

@bot.slash_command()
async def redeem(ctx, hidden:bool=True):
    options = getoptions(ctx)
    
    if options == []:
        await ctx.respond("this guild has no rewards set", ephemeral=True)
        return
    
    await ctx.respond("choose a reward", view=RedeemViewFunc(options), ephemeral=hidden)

@bot.slash_command()
async def modchannel(ctx, channel:discord.TextChannel):
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.respond("you dont have permission to use this command",ephemeral=True)
        return
    if not type(channel) == discord.channel.TextChannel:
        await ctx.respond("you need to specify a text channel, not a category or voice channel", ephemeral=True)

    with open("modchannels.json","r") as channelsraw:
        channels = json.loads(channelsraw.read())

    server = str(ctx.guild.id)
    channels[server] = channel.id

    with open("modchannels.json","w") as channelsraw:
        channelsraw.write(json.dumps(channels))

    await ctx.respond(f"changed the mod channel to {channel.mention}",ephemeral=True)
    await channel.send(f"{ctx.author.display_name} changed the mod channel to this channel")

@bot.slash_command()
async def leaderboard(ctx, hidden: bool = True):
    server = str(ctx.guild.id)
    user = str(ctx.author.id)

    with open("points.json", "r") as pointsraw:
        points = json.loads(pointsraw.read())
        points = points[server]

    leaderboard = sorted(points,reverse=True,key=lambda x: points[x])

    message = ""
    for x in leaderboard:
        score = points[x]

        if x == user:
            addtomessage = f"**<@{x}> - {score}**\n"
        else:
            addtomessage = f"<@{x}> - {score}\n"

        if len(addtomessage) + len(message) > 4096:
            break
        else:
            message += addtomessage

    embed = discord.Embed(title=f"leaderboard for {ctx.guild.name}", description=message, color=discord.Color.blurple())
    await ctx.respond(embed=embed,ephemeral=hidden)

@bot.slash_command()
async def name(ctx, name:str = "points"):
    with open("names.json", "r") as namesraw:
        names = json.loads(namesraw.read())

    names[str(ctx.guild_id)] = name

    with open("names.json", "w") as namesraw:
        namesraw.write(json.dumps(names))

    await ctx.respond(f"name of server points changed to {name}",ephemeral=True)

def RedeemViewFunc(options):
    if options is None:
        return None

    class RedeemView(discord.ui.View):
        @discord.ui.select(placeholder = "choose a reward", min_values = 1, max_values = 1, options=options)
        async def redeemcallback(self, Select, Interaction):
            with open("rewards.json") as rewardsraw:
                rewards = json.loads(rewardsraw.read())
            
            with open("points.json") as pointsraw:
                points = json.loads(pointsraw.read())

            server = str(Interaction.guild_id)
            user = str(Interaction.user.id)

            reward = Select.values[0]
            rewards = rewards[server]
            options = getoptions(Interaction)

            try:
                if not points[server][user] >= rewards[reward]:
                    await Interaction.response.send_message("poor",ephemeral=True)
                    return
                points[server][user] -= rewards[reward]

                name = getname(server)
                await Interaction.response.send_message(f"you redeemed **{reward}** for `{rewards[reward]}` {name}",ephemeral=True)

                with open("modchannels.json","r") as channelsraw:
                    channel = json.loads(channelsraw.read())
                    channel = channel[server]
                    channel = Interaction.guild.get_channel(channel)

                name = getname(Interaction.guild_id)
                await channel.send(f"{Interaction.user.mention} redeemed **{reward}** for `{rewards[reward]}` {name}", view=ModView())

                with open("points.json","w") as pointsraw:
                    pointsraw.write(json.dumps(points))
            except KeyError:
                await Interaction.response.send_message("poor",ephemeral=True)

    return RedeemView()

class ModView(discord.ui.View):
    @discord.ui.button(label="Done", row=0, style=discord.ButtonStyle.green)
    async def done_button_callback(self, Button, Interaction):
        message = Interaction.message
        rewardname = message.content.split("**")
        rewardname = rewardname[1]
        await message.mentions[0].send(f"{rewardname} was marked as done")
        await Interaction.message.edit(content="Marked as done!",view=None,delete_after=5)

    @discord.ui.button(label="Refund", row=0, style=discord.ButtonStyle.red)
    async def refund_button_callback(self, Button, Interaction):
        message = Interaction.message

        with open("points.json","r") as pointsraw:
            points = json.loads(pointsraw.read())
        
        rewardname = message.content.split("**")
        rewardname = rewardname[1]
        rewardcost = message.content.split("`")
        rewardcost = int(rewardcost[1])

        guild = Interaction.guild
        user = Interaction.message.mentions[0]

        points[str(guild.id)][str(user.id)] += rewardcost

        with open("points.json","w") as pointsraw:
            pointsraw.write(json.dumps(points))
        
        name = getname(Interaction.guild_id)

        await user.send(f"Your reward, {rewardname}, was refunded to you for {rewardcost} {name} by {Interaction.user} in {guild.name}")
        await Interaction.message.edit(content="Refunded!",view=None,delete_after=5)

def RemoveViewFunc(options):
    if options is None:
        return None

    class RemoveView(discord.ui.View):
        @discord.ui.select(placeholder = "choose a reward to remove", min_values = 1, max_values = 1, options=options)
        async def removecallback(self, Select, Interaction):
            with open("rewards.json","r") as rewardsraw:
                rewards = json.loads(rewardsraw.read())

            server = str(Interaction.guild_id)

            del rewards[server][Select.values[0]]

            with open("rewards.json","w") as rewardsraw:
                rewardsraw.write(json.dumps(rewards))

            await Interaction.response.send_message(content=f"removed {Select.values[0]} from this guild's rewards",view=RemoveViewFunc(options=getoptions(ctx=Interaction)),ephemeral=True)

    return RemoveView()


bot.run(token)