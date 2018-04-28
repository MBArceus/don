## MODULES ##
import discord, pickle, sqlite3
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
	#The guild cannot be initialized as a guild model in the beginning.
	#It must be called with each command in order to have the most recent possible data concerning the guild.
	botCommanderRoleName = f[3]
	print("Bot Commander role name initialized as: " + botCommanderRoleName)

# Initialize bot:
don = commands.Bot(command_prefix=prefix)
print("\ndiscord.py ver. " + discord.__version__ + "\nEstablishing connection...")

## HELPER FUNCTIONS ##
def isBC(user):
	# tests if given user has Bot Commander role in designated guild
	# based off user, not member, so works in DMs as well
	guild = don.get_guild(guildID)
	role = discord.utils.get(guild.roles, name = botCommanderRoleName)
	member = guild.get_member(user.id)
	return role in member.roles
def isInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

## EVENTS ##
@don.event
async def on_ready():
	print("Client logged in! DON is ready for action!")
	#await don.get_channel(336623992209408001).send("```Prefix initialized as: !!.\nKey initialized.\nDiscord token authenticated.\nGuild ID initialized as: 103276521635999744.\n\nDon 2.0 is in development.```")
	

## COMMANDS ##

#MOD COMMANDS
@don.command()
async def speak(ctx, channelID : int, text):
	# Allows Don to speak what you want to say on command.
	# Can only be used by Bot Commanders.
	if isBC(ctx.message.author):
		await don.get_channel(channelID).send(text)
		
##ROLE COMMANDS
@don.command()
async def addopenrole(ctx, roleArg):
	# Adds role to the list of open roles.
	# Can only be used by Bot Commanders.
	if isBC(ctx.message.author):
		guild = don.get_guild(guildID)
		
		if isInt(roleArg): #if role is accessed via ID
			role = discord.utils.get(guild.roles, id = int(roleArg))
		else: #if role is accessed via name
			role = discord.utils.get(guild.roles, name = roleArg)
		
		if role is None: #gate: if role doesn't exist / argument invalid
			await ctx.send("Error: That role doesn't seem to exist...")
		else:
			#establish SQL connection
			db = sqlite3.connect("data/don_data.db")
			c = db.cursor()
			#Checks if already in db
			c.execute("select * from openroles where roleID = '" + str(role.id) + "'") #fetches rows with ID
			if c.fetchone() == None: #gate: if no rows found
				#Inserts data
				c.execute("insert into openroles (roleID, name) values('" + str(role.id) + "', '" + role.name + "')") #adds to db
				db.commit() #commits changes
				await ctx.send(role.name + " has been added as an open role.")
			else:
				await ctx.send("Error: " + role.name + " is already an open role.")
	else:
		await ctx.send("Error: You are not a " + botCommanderRoleName + ".")
@don.command()
async def removeopenrole(ctx, roleArg):
	# Removes role from the list of open roles.
	if isBC(ctx.message.author):
		guild = don.get_guild(guildID)
		
		if isInt(roleArg): #if role is accessed via ID
			role = discord.utils.get(guild.roles, id = int(roleArg))
		else: #if role is accessed via name
			role = discord.utils.get(guild.roles, name = roleArg)
		
		if role is None: #if role doesn't exist / argument invalid
			await ctx.send("Error: That role doesn't seem to exist...")
		else:
			#establish SQL connection
			db = sqlite3.connect("data/don_data.db")
			c = db.cursor()
			#Checks if already in db
			c.execute("select * from openroles where roleID = '" + str(role.id) + "'") #fetches rows with ID
			if c.fetchone() != None: #if no rows found
				#Inserts data
				c.execute("delete from openroles where roleID = '" + str(role.id) + "'") #removes from db
				db.commit() #commits changes
				await ctx.send(role.name + " has been removed from the list of open roles.")
			else:
				await ctx.send("Error: " + role.name + " isn't an open role.")
	else:
		await ctx.send("Error: You are not a " + botCommanderRoleName + ".")
@don.command()
async def openroles(ctx):
	# Returns list of all open roles.
	
	s = "The open roles are: "
	guild = don.get_guild(guildID)
	#establish SQL connection
	db = sqlite3.connect("data/don_data.db")
	c = db.cursor()
	c.execute("select * from openroles")
	rows = c.fetchall()
	roleNames = []
	#print(rows)
	for r in rows:
		#print(r)
		roleNames += [discord.utils.get(guild.roles, id = int(r[0])).name]
	roleNames.sort()
	for i in roleNames:
		#print(r)
		s += i + ", "
	await ctx.send(s[:-2])

#TEST COMMANDS
@don.command()
async def checkbc(ctx):
	# Checks if user is a Bot Commander.
	# Tells user whether or not they are one.
	if isBC(ctx.message.author):
		await ctx.send("You are a " + botCommanderRoleName + "!")
	else:
		await ctx.send("You are not a " + botCommanderRoleName + ".")
	
@don.command()
async def ping(ctx):
	# Tests connection.
	print("Received ping.")
	await ctx.send(content="Pong!", file=discord.File("icons/4.png"))
	

## JANITORIAL ##

#Runs Don.
don.run(key)