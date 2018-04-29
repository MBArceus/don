## MODULES ##
import discord, pickle, sqlite3, os, glob
from discord.ext import commands
from os.path import join
from random import randint

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
don.remove_command('help')
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
	await don.change_presence(activity=discord.Game(name='Type ' + prefix + 'help for info!'))
	print("Client logged in! DON is ready for action!")
	#await don.get_channel(336623992209408001).send("```Prefix initialized as: !!.\nKey initialized.\nDiscord token authenticated.\nGuild ID initialized as: 103276521635999744.\n\nDon 2.0 is in development.```")
	

##    _____                                          _     
##  / ____|                                        | |    
## | |     ___  _ __ ___  _ __ ___   __ _ _ __   __| |___ 
## | |    / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
## | |___| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
##  \_____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/

#GENERAL COMMANDS
@don.command()
async def help(ctx, *args):
	# Describes how to use each command.
	if len(args) == 0: #General help. Lists all commands.
		with open('help/main.txt', 'r') as f:
			msg = f.read().format(PREFIX=prefix)
		for file in os.scandir("help"): # loop through all category names
			#print(file)
			if file.is_dir(): # check whether the current object is a folder or not
				msg += "\n\n**" + file.name + "**" #adds category name
				for fileWithin in os.scandir("help/" + file.name): #checks all commands within category
					if fileWithin.is_dir():
						msg += "\n**" + fileWithin.name + ":** " #adds command name
						with open('help/' + file.name + '/' + fileWithin.name + '/short.txt', 'r') as desc:
							msg += desc.read() #adds command description
						
		# for root, dirs, files in os.walk('help'):
			# print(dirs)
			# for name in dirs:
				# msg += "\n\n**" + name + "**"
				# for root, dirs, files in os.walk(join(root, name)):
					# for name in dirs:
						# msg += "\n**" + name + ":** "
		await ctx.send(msg)
	if len(args) == 1: # Help for a specific command.
		for filename in glob.iglob('help/*/' + args[0]):
			msg = "**" + filename.split("\\")[-1] + "**\n"
			with open(filename + "/long.txt") as f:
				msg += f.read().format(PREFIX=prefix)
		await ctx.send(msg)

@don.command()
async def git(ctx):
	#Links to open-source Github repo.
	await ctx.send("https://github.com/MBArceus/don")
		

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
	s+= ", ".join(roleNames)
	await ctx.send(s)
	
@don.command()
async def addrole(ctx, roleArg):
	# Adds open role to author.
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
		c = db.cursor() #creates cursor to access table
		#Checks if in db
		c.execute("select * from openroles where roleID = '" + str(role.id) + "'") #fetches rows with ID
		if c.fetchone() != None: #gate: if open role
			member = guild.get_member(ctx.author.id)
			if discord.utils.get(member.roles, id = role.id) != None: #gate: if author already has role
				await ctx.send("Error: You already have the " + role.name + " role!")
			else:
				await member.add_roles(role, reason="Use of addrole command")
				await ctx.send("Successfully added the " + role.name + " role!")
		else:
			await ctx.send("Error: " + role.name + " isn't an open role.")
			
@don.command()
async def removerole(ctx, roleArg):
	# Removes open role from author.
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
		c = db.cursor() #creates cursor to access table
		#Checks if in db
		c.execute("select * from openroles where roleID = '" + str(role.id) + "'") #fetches rows with ID
		if c.fetchone() != None: #gate: if open role
			member = guild.get_member(ctx.author.id)
			if discord.utils.get(member.roles, id = role.id) == None: #gate: if author already doesn't have role
				await ctx.send("Error: You already don't have the " + role.name + " role!")
			else:
				await member.remove_roles(role, reason="Use of removerole command")
				await ctx.send("Successfully removed the " + role.name + " role.")
		else:
			await ctx.send("Error: " + role.name + " isn't an open role.")

#FUN COMMANDS
@don.command()
async def roll(ctx, *args):
	if len(args) == 0:
		await ctx.send(file=discord.File("img/roll.gif"))
	elif len(args) == 1 and isInt(args[0]):
		if int(args[0]) >= 500:
			await ctx.send(content="Aaaaaah! Still too big of a number! Still too big of a number!",file=discord.File("icons/25.png"))
		dice = int(args[0])
		vals = []
		valStr = []
		for _ in range(dice):
			vals.append(randint(1,6))
			valStr.append(str(vals[-1]))
		await ctx.send(content="Rolled **" + str(dice) + "** 6-sided dice and got **" + str(sum(vals)) + "**.\n*(" + " + ".join(valStr) + ")*", file=discord.File("img/roll.gif"))
		
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