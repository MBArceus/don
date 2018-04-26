## MODULES ##
import discord
from discord.ext import commands

print("Just An Assistant! Don\n")

# Accesses information from config:
with open('data/don.config', 'r') as f:
	f = f.read().split("\n")
	# f is list of each line in config
	i = 0
	while i < len(f):
		f[i] = f[i].split("=", 1)[1] #removes name of each entry in config
		i += 1
	#initializing vars...
	prefix = f[0]
	print("Prefix initialized as: " + prefix)
	key = f[1]
	print("Key initialized (and hidden.)")
	guildID = int(f[2])
	print("GuildID initialized as: " + str(guildID))
	botCommanderRoleName = f[3]
	print("Bot Commander role name initialized as: " + botCommanderRoleName)

# Initialize bot:
don = commands.Bot(command_prefix=">>")
print("\ndiscord.py ver. " + discord.__version__ + "\nBooting up...")

# Initialize more vars:
guild = don.get_guild(guildID)

## HELPER FUNCTIONS ##
def isBC(user):
	# tests if given user has Bot Commander role in designated guild
	# based off user, not member, so works in DMs as well
	role = discord.utils.get(guild.roles, name = botCommanderRoleName)
	member = guild.get_member(user.id)
	return role in member.roles

## EVENTS ##
@don.event
async def on_ready():
	print("Client logged in! DON is ready for action!")
	#await don.get_channel(336623992209408001).send("```Prefix initialized as: !!.\nKey initialized.\nDiscord token authenticated.\nGuild ID initialized as: 103276521635999744.\n\nDon 2.0 is in development.```")
	

## COMMANDS ##
@don.command()
async def speak(ctx, channelID, text):
	# Allows Don to speak what you want to say on command.
	# Can only be used by Bot Commanders.
	if isBC(ctx.message.author):
		await don.get_channel(int(channelID)).send(text)
	
@don.command()
async def checkbc(ctx):
	# Checks if user is a Bot Commander.
	# Tells user whether or not they are one.
	if isBC(ctx.message.author):
		await ctx.send("You are a " + botCommanderRoleName + "!")
	else:
		await ctx.send("You are not a " + botCommanderRoleName + ".")
	

## JANITORIAL ##

#Runs Don.
don.run(key)