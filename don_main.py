## MODULES ##
import discord, pickle, sqlite3, os, glob, math, asyncio, random
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
	timeout = int(f[4])
	print("Timeout duration initialized as: " + str(timeout) + " secs")

# Initialize bot:
don = commands.Bot(command_prefix=prefix)
don.remove_command('help')
print("\ndiscord.py ver. " + discord.__version__ + "\nEstablishing connection...")

## HELPER FUNCTIONS ##
def getGuild():
	return don.get_guild(guildID)
def isBC(user):
	# tests if given user has Bot Commander role in designated guild
	# based off user, not member, so works in DMs as well
	guild = getGuild()
	role = discord.utils.get(guild.roles, name = botCommanderRoleName)
	member = guild.get_member(user.id)
	return role in member.roles
def isInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
def invIntToStr(i):
	if i == 0:
		return "NPC"
	elif i == 1:
		return "Red"
	elif i == 2:
		return "Yellow"
	elif i == 3:
		return "Green"
	elif i == 4:
		return "Blue"
	elif i == 5:
		return "Purple"
	raise ValueError("Invalid investigation score")
def gameIntToStr(i):
	if i == 0:
		return "Future Zone"
	elif i > 0:
		return "Game " + str(i)
	raise ValueError("Invalid game number")
def STRBar(str,maxstr):
	text = "`STR {} / {}\n[".format(str, maxstr)
	for _ in range(str):
		text += "■ "
	for _ in range(maxstr-str):
		text += "- "
	text = text[:-1] + "]`"
	return text
def inchesToStr(i):
	return str(math.floor(i/12.0)) + "'" + str(i%12) + '" (' + str(math.floor(i*2.54)) + " cm)"
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
		
@don.command()
async def inject(ctx, *, arg):
	if isBC(ctx.author):
		db = sqlite3.connect("data/don_data.db")
		#db.row_factory = sqlite3.Row
		c = db.cursor()
		c.execute(arg)
		db.commit()
		await ctx.send("Successfully injected command.")
	else:
		await ctx.send("Error: You're not a " + botCommanderRoleName + "! And this is... um... some pretty dangerous code...")
		
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
			
#RP COMMANDS

   # ___  _                                  .                      .___           .           _                          
 # .'   \ /        ___  .___    ___    ___  _/_     ___  .___       /   `    ___  _/_     ___  \ ___    ___    ____   ___ 
 # |      |,---.  /   ` /   \  /   ` .'   `  |    .'   ` /   \      |    |  /   `  |     /   ` |/   \  /   `  (     .'   `
 # |      |'   ` |    | |   ' |    | |       |    |----' |   '      |    | |    |  |    |    | |    ` |    |  `--.  |----'
  # `.__, /    | `.__/| /     `.__/|  `._.'  \__/ `.___, /          /---/  `.__/|  \__/ `.__/| `___,' `.__/| \___.' `.___,

@don.command()
async def addcharacter(ctx, *args):
	# Adds characters.
	# Can be used in 3 ways:
	# - addcharacter
	#    - Walks user step-by-step through each required parameter.
	#    - Non-required parameters can be edited later.
	#    - Does not write to database until all steps complete.
	# - addcharacter <param> = <value> <param> = <value> <param> = <value> ... TODO
	#    - Allows user to enter params all at once in any given order.
	#    - Cannot exclude required (not null) params.
	#    - Params can be entered with quotes like this: desc="This is a description."
	# - addcharacter <value> <value> <value> ... TODO
	#    - Allows user to enter params all at once.
	#    - Must encompass at least all required params.
	# Integers are converted from str arguments to int as necessary.
	
	db = sqlite3.connect("data/don_data.db")
	db.row_factory = sqlite3.Row
	c = db.cursor()
	
	# get param list
	c.execute('select * from characters')
	r = c.fetchone()
	paramList = r.keys()
	
	if len(args) == 0:
		requiredParams = ['id', 'name', 'nick', 'mun', 'game', 'investigation', 'maxstr', 'str']
		#characterDict = {} # where data will be stored for the character from each step before being committed to db
		#characterDict['mun'] = str(ctx.author.id)
		await ctx.send("Enter your character's unique ID.")
		
		def userCheck(m): #predicate
			return m.channel == ctx.channel and m.author == ctx.author
		
		#loop to determine id
		doLoop = True
		while doLoop:
			waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
			#some hedge trimming
			waitContent = "".join(waitResponse.content.lower().split())
			#check if id exists
			c.execute('select * from characters where id = ?', (waitResponse.content,))
			if c.fetchone() == None:
				doLoop = False
				id = waitContent
				c.execute("insert into characters (id, mun) values (?, ?)", (id, str(ctx.author.id)))
				await ctx.send("Character ID registered as `{}`.\n\nNext, enter your character's full name.".format(waitContent))
			else:
				await ctx.send("Error: That ID is already taken!")
				
		#determine name
		waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
		#some hedge trimming
		waitContent = waitResponse.content.strip()
		#characterDict['name'] = waitContent
		c.execute("update characters set name = ? where id = ?",(waitContent,id))
		await ctx.send("Character name registered as `{}`.\n\nNext, enter your character's shorthand name. This can be a nickname or their first name.".format(waitContent))
		
		#determine nick
		waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
		#some hedge trimming
		waitContent = waitResponse.content.strip()
		#characterDict['nick'] = waitContent
		c.execute("update characters set nick = ? where id = ?",(waitContent,id))
		await ctx.send("Character nickname registered as `{}`.\n\nNext, enter your character's resident game. It must be an integer. For Future Zone characters, enter 0.".format(waitContent))
		
		#loop to determine game
		doLoop = True
		while doLoop:
			waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
			#some hedge trimming
			waitContent = waitResponse.content.strip()
			if isInt(waitContent):
				if int(waitContent) >= 0:
					doLoop = False
					#characterDict['game'] = int(waitContent)
					c.execute("update characters set game = ? where id = ?",(int(waitContent),id))
					if int(waitContent) == 0:
						await ctx.send("Character registered as a Future Zone character.\n\nNext, enter your character's investigation color. This must be a number from 0 to 3. 0 is NPC, 1 is red, 2 is yellow, 3 is green.")
					else:
						await ctx.send("Character registered as a Game {} character.\n\nNext, enter your character's investigation color. This must be a number from 0 to 3. 0 is NPC, 1 is red, 2 is yellow, 3 is green.".format(waitContent))
				else:
					await ctx.send("Error: That's an invalid number!")
			else:
				await ctx.send("Error: That's not an integer!")
		
		#loop to determine investigation color
		doLoop = True
		while doLoop:
			waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
			#some hedge trimming
			waitContent = waitResponse.content.strip()
			if isInt(waitContent):
				if int(waitContent) >= 0 and int(waitContent) < 4:
					doLoop = False
					#characterDict['investigation'] = int(waitContent)
					c.execute("update characters set investigation = ? where id = ?",(int(waitContent),id))
					await ctx.send("Character's investigation score registered as `{}`.\n\nNext, enter your character's STR score. This is an integer from 3 to 7, with 3 being an extremely weak person, 5 being average, and 7 being an exceptionally skilled and fit fighter.".format(waitContent))
				else:
					await ctx.send("Error: That's an invalid number!")
			else:
				await ctx.send("Error: That's not an integer!")
		
		#loop to determine str
		doLoop = True
		while doLoop:
			waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
			#some hedge trimming
			waitContent = waitResponse.content.strip()
			if isInt(waitContent):
				if int(waitContent) >= 3 and int(waitContent) < 8:
					doLoop = False
					#characterDict['maxstr'] = int(waitContent)
					#characterDict['str'] = int(waitContent)
					c.execute("update characters set maxstr = ? where id = ?",(int(waitContent),id))
					c.execute("update characters set str = ? where id = ?",(int(waitContent),id))
					await ctx.send("Character's STR registered as `{}`.\n\nNext, enter your character's description. This can be as long or as brief as you want!".format(waitContent))
				else:
					await ctx.send("Error: That's an invalid number!")
			else:
				await ctx.send("Error: That's not an integer!")
				
		#determine desc
		waitResponse = await don.wait_for("message", check=userCheck, timeout=timeout)
		#some hedge trimming
		waitContent = waitResponse.content.strip()
		#characterDict['description'] = waitContent
		c.execute("update characters set description = ? where id = ?",(waitContent,id))
		await ctx.send("Character description registered!")
		await ctx.send("Committing changes...")
		await asyncio.sleep(random.uniform(2.0,5.0)) # fake delay, to make people feel like something's happening
		
		#finally, commit values
		# c.execute("insert into characters (id) values (?)", (characterDict['id'],))
		# for k in characterDict.keys():
			# c.execute("update characters set ? = ? where id = ?",(k,characterDict[k],characterDict['id']))
		db.commit()
		
		await ctx.send("Success! The character has been added to the database.\nUse `" + prefix + "editcharacter` to edit later or add miscellaneous details.")
			
@don.command()
async def readcharacter(ctx, arg):
	# Returns information concerning a particular character.
	db = sqlite3.connect("data/don_data.db")
	db.row_factory = sqlite3.Row # allows rows to be accessed by key
	c = db.cursor()
	c.execute("select * from characters where id = ?", (arg,)) 
	character = c.fetchone()
	
	if c == None: #if not found
		await ctx.send("Error: No character with ID `" + arg + "` found!")
		return
		
	params = character.keys()
	
	# accessory STRs for formatting
	
	gameStr = gameIntToStr(character['game'])
	invStr = invIntToStr(character['investigation'])
	
	guild = getGuild()
	mun = guild.get_member(int(character['mun']))
	munStr = mun.nick + " (" + mun.name + ")"
	
	if character['talent'] == None:
		talentStr = ""
	else:
		talentStr = "SHSL " + character['talent'] + "\n"
		
	if character['gender'] == None:
		genderStr = ""
	else:
		genderStr = character['gender'] + "\n"
		
	if character['age'] == None:
		ageStr = ""
	else:
		ageStr = "Age " + str(character['age']) + "\n"
		
	if character['height'] == None:
		heightStr = ""
	else:
		heightStr = inchesToStr(character['height']) +"\n"
		
	STRStr = STRBar(character['str'], character['maxstr'])
	
	#format
	msgContent = """__**{}**__ `({})`

**{}{}{}{}, {}
{}{}
Mun:** {}

__Description__
{}""".format(character['name'], character['id'], talentStr, genderStr, ageStr, invStr, gameStr, heightStr, STRStr, munStr, character['description'])
	
	params.remove("id")
	params.remove("name")
	params.remove("nick")
	params.remove("str")
	params.remove("maxstr")
	params.remove("mun")
	params.remove("game")
	params.remove("description")
	params.remove("talent")
	params.remove("gender")
	params.remove("investigation")
	params.remove("age")
	params.remove("height")
	
	params.sort() #sort parameters after main params removed. only misc info should be left
	
	if len(params) > 0: #adds miscellaneous parameters to string
		msgContent += "\n"
		for p in params:
			if character[p] != None:
				msgContent += "\n**" + p.capitalize() + ":** " + str(character[p])
	
	await ctx.send(msgContent)
	
@don.command()
async def editcharacter(ctx, *args):
	# Edits characters.
	# Uses syntax "editcharacter <param> = <value> <param> = <value> ...
	
	db = sqlite3.connect("data/don_data.db")
	db.row_factory = sqlite3.Row
	c = db.cursor()
	c.execute("select* from characters limit 1")
	row = c.fetchone()
	params = row.keys()
	intParams = ['game','investigation','maxstr','str','height','age'] #list of params that are int, not text. todo: maybe automate somehow?
	
	if len(args) == 0: #lists params
		await ctx.send("The possible parameters are: `" + ", ".join(params) + "`")
	elif len(args) == 1:
		c.execute("select * from characters where id = ?", (args[0],)) 
		character = c.fetchone()
		if character == None:
			await ctx.send(content="Error: That character doesn't exist! You didn't even give me anything to edit, anyway!",file=discord.File("icons/5.png"))
		elif character['mun'] == str(ctx.author.id) or isBC(ctx.author):
			await ctx.send(content="Your character has been successfully edited to... exactly the way it was before...",file=discord.File("icons/12.png"))
		else:
			await ctx.send(content="Error: You didn't give me anything to edit! Besides, that's not even your character!",file=discord.File("icons/5.png"))
	else:
		c.execute("select * from characters where id = ?", (args[0],)) 
		character = c.fetchone()
		if character == None:
			await ctx.send("Error: That character doesn't exist!")
		elif character['mun'] == str(ctx.author.id) or isBC(ctx.author):
			if len(args)%3 != 1: #if modulo is not 1, therefore invalid syntax
				await ctx.send("Error: Invalid parameters! Did you make sure to use the correct syntax, using spaces and quotes properly?")
				return
			
			paramsToEdit = []
			valsToEdit = []
				
			i = 2
			while i < len(args):
				paramToEdit = args[i-1].lower()
				valToEdit = args[i+1]
				if args[i] != "=": #if not =
					await ctx.send("Error: Invalid parameters! Did you make sure to use the correct syntax, using spaces and quotes properly?")
					return
				if args[i-1].lower() not in params: #if invalid param
					await ctx.send("Error: Invalid parameters! Did you misspell something?")
					return
				if paramToEdit in intParams and not isInt(valToEdit):
					await ctx.send("Error: `" + paramToEdit + "` is an integer parameter, and you didn't enter an integer!")
					return
				if paramToEdit in intParams and int(valToEdit) < 0:
					await ctx.send("Error: You can't enter negative integers!")
					return
				if paramToEdit == 'mun' and not isBC(ctx.author):
					await ctx.send("Error: You're not allowed to change ownership of your character!")
					return
				if paramToEdit == 'investigation' and int(valToEdit) > 3:
					await ctx.send("Error: You can't edit `investigation` to value `" + valToEdit + "`! It has to be from 0 to 3!")
					return
				#todo: if paramToEdit == mun, convert valToEdit from mention to id
				if paramToEdit in paramsToEdit:
					await ctx.send("Error: Requested to edit the same parameter twice!")
					return
				
				#phew. we finally got past all of that
				if paramToEdit in intParams:
					valToEdit = int(valToEdit)
				
				paramsToEdit.append(paramToEdit)
				valsToEdit.append(valToEdit)
				
				i += 3
			
			i = 0
			while i < len(paramsToEdit):
				c.execute("update characters set " + paramsToEdit[i] + " = ? where id = ?", (valsToEdit[i],args[0]))
				# This is injection-safe, I swear. 'Cuz... 'cuz... it's gotta be in the list of defined params, yeah. Yeah.
				# Honest.
				i += 1
			db.commit()
			
			c.execute("select * from characters where id = ?", (args[0],))
			chara = c.fetchone()
			
			await ctx.send("Edits successfully made to " + chara['name'] + ".")
		else:
			await ctx.send("Error: You don't have permission to edit that character!")
		
		
	
@don.command()
async def listcharacters(ctx, *args):
	# Returns list of characters.
	# Can use additional parameters to only return characters with certain attributes, such as "investigation=green" or "mun=me".
	# Only returns in pageLength sized portions. Following the command with an integer will return that page of characters.
	pageLength = 25 # amount of characters to display per page
	msgContent = "**List of Characters**\n"
	where = [] # list of clauses
	if len(args) != 0 and isInt(args[-1]): # if page number is specified
		page = int(args[-1])
	else:
	 page = 1
	db = sqlite3.connect("data/don_data.db")
	db.row_factory = sqlite3.Row # allows rows to be accessed by key
	c = db.cursor()
	
	c.execute("select count(*) from characters") # gets number of characters
	characterCount = c.fetchone()[0] #gets int from row
	
	maxPage = math.ceil(characterCount/pageLength)
	
	if page > maxPage or page <= 0:
		await ctx.send("Error: That's an invalid page number. There are only " + str(maxPage) + " pages.")
		return
	
	c.execute("select * from characters where rowid>" + str( (page-1)*pageLength ) + " and rowid<=" + str( (page)*pageLength)) #fetches characters
	rows = c.fetchall()
	for r in rows:
		msgContent += "\n" + r["name"] + " `(" + r["id"] + ")`"
	msgContent += "\n\n*Displaying " + str(len(rows)) + " characters on page " + str(page) + " out of " + str(maxPage) + " pages.*"
	await ctx.send(msgContent)
	
		

#FUN COMMANDS
@don.command()
async def roll(ctx, *args):
	if len(args) == 0:
		await ctx.send(file=discord.File("img/roll.gif"))
	elif len(args) == 1 and isInt(args[0]):
		if int(args[0]) >= 1000000:
			await ctx.send(content="Aaaaaah! Still too big of a number! Still too big of a number!",file=discord.File("icons/25.png"))
			return
		dice = int(args[0])
		vals = []
		valStr = []
		for _ in range(dice):
			vals.append(randint(1,6))
			valStr.append(str(vals[-1]))
		try:
			await ctx.send(content="Rolled **" + str(dice) + "** 6-sided dice and got **" + str(sum(vals)) + "**.\n*(" + " + ".join(valStr) + ")*", file=discord.File("img/roll.gif"))
		except discord.errors.HTTPException:
			await ctx.send(content="Rolled **" + str(dice) + "** 6-sided dice and got **" + str(sum(vals)) + "**.", file=discord.File("img/roll.gif"))
		
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