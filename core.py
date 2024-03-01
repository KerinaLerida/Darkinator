import discord
import bot
import common
import datetime
import threading
import os
import requests

#INIT VARS--------------------------------------
bool_start=False
bool_guess=False
hours_default=24
hours_x=hours_default
guess_champ=""
timer_x=datetime.datetime.now()
#-----------------------------------------------

def create_embed(title, description):
    color=discord.Color(0xb408ab) #couleur msg embed
    return discord.Embed(title=title, description=description, color=color)

# Get list of discord.Role and returns list of roles' names
def get_role_name(roleArray : list):
    return [i.name for i in roleArray]

#Command Validity checkers-------------------------
def check_roles(inter : discord.Interaction, rolesArr):
    for r in rolesArr:
        if r not in get_role_name(inter.user.roles):
            common.gInvalidCmdMsg = "You don't have privilege to access this command"
            return False
    return True

def check_channels(inter : discord.Interaction, channelsArr):
    if not inter.channel.id in channelsArr:
        common.gInvalidCmdMsg = "Invalid Channel"
        return False
    return True

def help_command(inter:discord.Interaction,message, msg_bureau, msg_cotisant): #msg de debug pour corriger sa commande
    s = ""
    if check_roles(inter, ["Bureau"]):
        s = " ,or , " + msg_bureau
    return create_embed("Help","Just try: " + msg_cotisant + s)

def help_embed(str_):
    return create_embed("Help",str_)

def update_embed(str_):
    return create_embed("Update",str_)

def telecharge_image(url, dossier,nom_image):
    chemin_destination = os.path.join(dossier, nom_image)
    if os.path.exists(chemin_destination):
        print("L'image", nom_image, "est déjà présente dans le dossier.")
        os.remove(chemin_destination)  # Supprimer l'ancienne image

    response=requests.get(url)
    if response.status_code==200:
        with open(chemin_destination,"wb") as f:
            f.write(response.content)
        print("Image téléchargée avec succès")
    else:
        print("Échec du téléchargement de l'image")

def check_user_exist(id):
    return common.DB.user_exist_by_id(id)

def check_champ_exist(name):
    return common.DB.champ_exist_by_name(name)

def affiche_point(id_author, id,title):
    s = ""
    if id == id_author:
        s = "You have " + str(common.DB.get_points_by_id(id_author))
    else:
        s = str(common.DB.get_user_name_by_id(id)) + " has " + str(common.DB.get_points_by_id(id))
    return create_embed(title, s + " Point(s)")

def how_long_guess_mode_active():
    duration = datetime.timedelta(hours=hours_x)
    result_datetime=duration-(datetime.datetime.now()-timer_x)
    total_seconds = result_datetime.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    return hours, minutes

def starting_mode(n_hours):
    guess_mode(n_hours)
    return create_embed("Start","Guess mode is activated every "+str(hours_x)+" hours.")

def guess_mode(n_hours):
    global bool_start, bool_guess, hours_x, timer_x,guess_champ
    hours_x=int(n_hours)
    bool_start=True
    bool_guess=True
    timer_x=datetime.datetime.now()
    guess_champ=common.DB.get_champ_random()
    print(guess_champ)

def compare(g,c):
    g = set(str(g).split())
    c = set(str(c).split())
    if g.issubset(c):  # tous les mots sont contenus
        return [":white_check_mark:", 1]
    elif len(g.intersection(c)) > 0 or len(c.intersection(g)) > 0:  # des mots sont partiellement présents
        return [":fire:", 3]
    else:  # aucun mot en commun
        if len(g)==1 and len(c)==1:
            try:
                emo=""
                g=int(list(g)[0])
                c=int(list(c)[0]) #FAIREVFONCTION QUI TESTE INT OU PAS
                if(g<c):
                    emo=":arrow_down:"
                elif g>c:
                    emo=":arrow_up:"
                return [emo, 3]
            except ValueError:
                return [":no_entry:", 0]
        return [":no_entry:", 0]

def guess_reponse(name_command,id):
    global guess_champ, bool_guess

    data_g=common.DB.get_champion_by_name(guess_champ)
    data_c=common.DB.get_champion_by_name(name_command)
    name_champ=common.DB.get_name_champ_by_search(name_command)

    t=["Gender","Role","Type","Race","Resource","Range type","Region(s)","Release year"]
    e=create_embed("Guessing",None)
    image_path="pictures/"+str(name_champ)+".png"
    file = discord.File(image_path, filename=str(name_champ)+".png")
    e.set_thumbnail(url="attachment://" + image_path)
    e.add_field(name="Champion",value=name_champ,inline=True)
    win=0
    for i in range(2,len(data_c)-1):
        comp=compare(data_g[i],data_c[i])
        print(str(data_g[i])+" ; "+str(data_c[i])+"\n")
        win+=comp[1]
        e.add_field(name=t[i-2],value=str(comp[0]) +" "+ str(data_c[i]),inline=True)
    if guess_champ==name_command:
        #someone_guessed(common.DB)
        bool_guess=False
        common.DB.update_points_by_id(10,id)
        e.description="gg ez ( ͡° ͜ʖ ͡°) You guessed "+str(name_champ)+" ! +10 points \n"+'"'+str(common.DB.get_champ_title_by_search(name_command))+'"'
    return e,file

#-------------------------------------------------
#Cmds in order, "z" prefix is reserved to cmds accessible only to administrators, such prefix is used for discord command sorting which is alphabetical
# -hello
# -info
# -point
# -all
# -guess
# -g
# -zstart
# -zstop
# -zpoint
# -zchamps
# -zcreate_user
# -zcreate_champ
# -zupdate_point
# -zupdate_champ_url
# -zdelete_user
# -zdelete_champ

@bot.tree.command(name="hello", description="Say hello to the bot", guild=discord.Object(id=common.SERVER_ID))
async def helloCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    return await inter.response.send_message(embed=create_embed(None, "Hey there!"))

@bot.tree.command(name="info", description="Get info about the bot", guild=discord.Object(id=common.SERVER_ID))
async def infoCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    return await inter.response.send_message(embed=create_embed(None, "My name is Darkinator, but my creator prefer to call me as Darkinia. Have fun and guess LoL Champions!"))

@bot.tree.command(name="point", description="Get your points", guild=discord.Object(id=common.SERVER_ID))
async def pointCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    return await inter.response.send_message(embed=affiche_point(inter.user.id, inter.user.id, "Point(s)"))

@bot.tree.command(name="all", description="Get all points", guild=discord.Object(id=common.SERVER_ID))
async def allCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    data= common.DB.get_all_users()
    msg=""
    title=None
    if not data:
        msg="No user is in the database.."
    else:
        title="Ranking of Drakiguessors"
        for user in data:
            msg += "```"
            msg += str(user[0]) + " ‎" * 4
            msg += "Point(s): " + str(user[1]) + " ‎" * 4
            msg+= "```"
    return await inter.response.send_message(embed=create_embed(title, msg))

@bot.tree.command(name="guess", description="Guess state", guild=discord.Object(id=common.SERVER_ID))
async def guessCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    global hours_x, bool_guess, bool_start
    if bot.choose_update:
        guess_mode(hours_x)
        bot.choose_update = False
    title="Guess"
    if bool_start:
        msg="A guess is in progress.."
        if bool_guess:
            return await inter.response.send_message(embed=create_embed(title,msg))
        else:
            hours, minutes = how_long_guess_mode_active()  # vérifer : heure actuelle - timer_x rste temps avant prochain guess bool_guess
            msg = "Next guess in " + str(hours) + " hours and " + str(minutes) + " minutes."
            return await inter.response.send_message(embed=create_embed(title, msg))
    else:
        msg="Drakania is sleeping.. Contact a member of the Bureau!"
        return await inter.response.send_message(embed=create_embed(title, msg))

@bot.tree.command(name="g", description="Guess a champion with this command.", guild=discord.Object(id=common.SERVER_ID))
async def questionCmd(inter:discord.Interaction, champion:str):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not bool_guess:
        return await inter.response.send_message(embed=create_embed("Guess", "Guess not in progresed."))
    champ_name= champion.lower()
    if check_champ_exist(champ_name):
        e,file=guess_reponse(champ_name, inter.user.id)
        return await inter.response.send_message(embed=e, file=file)
    else:
        bdd= common.DB
        l=len(champ_name)
        while bdd.get_champ_same_firstnletter(l,champ_name,l)==None:
            l-=1
        data=bdd.get_champ_same_firstnletter(l,champ_name,l)
        msg=""
        if data :
            for champ in data:
                msg = "```"
                msg += champ[0] + " ‎" * 4
                msg += "```"
            return await inter.response.send_message(embed=create_embed("Did you mean.. ", msg))
        else:
            return await inter.response.send_message(embed=create_embed("No suggestion(s)", "Are you sure about the name of the champion?"))

@bot.tree.command(name="zstart", description="Start the guess mode", guild=discord.Object(id=common.SERVER_ID))
async def zstartCmd(inter:discord.Interaction, hours:int=-1):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    global bool_start
    if bool_start:
        return await inter.response.send_message(embed=create_embed("Start", "Guess mode is already activated."))
    if hours==-1:
        hours=hours_default
    return await inter.response.send_message(embed=starting_mode(hours))

@bot.tree.command(name="zstop", description="Stop the guess mode", guild=discord.Object(id=common.SERVER_ID))
async def zstopCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    global bool_start, bool_guess,timer_x
    if not bool_start:
        return await inter.response.send_message(embed=create_embed(None, "Guess mode is already deactivated. Drakinator is sleeping.."))
    else:
        bool_start = False
        bool_guess = False
        timer_x = datetime.datetime.now()
        return await inter.response.send_message(embed=create_embed("Stop", "The Drakinator bot has been stopped."))

@bot.tree.command(name="zpoint", description="Get points of a user", guild=discord.Object(id=common.SERVER_ID))
async def zpointCmd(inter:discord.Interaction, user:discord.User):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not check_user_exist(user.id):
        return await inter.response.send_message(embed=create_embed(None, "User not found."))
    return await inter.response.send_message(embed=affiche_point(inter.user.id, user.id, "Point(s)"))

@bot.tree.command(name="zchamps", description="Get all champions", guild=discord.Object(id=common.SERVER_ID))
async def zchampsCmd(inter:discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    data= common.DB.get_all_champions()
    msg=""
    title=None
    if not data:
        msg="No champion is in the database.."
    else:
        av_name=""
        title="League of Legends Champions"
        names=""
        for champ in data:
            name = champ[0].capitalize()
            if av_name!="":
                if av_name[0] != name[0]:
                    msg+=f"```{names}```"
                    names=""
            names+=f"{name} "
            av_name=name
    return await inter.response.send_message(embed=create_embed(title, msg))

@bot.tree.command(name="zcreate_user", description="Create a user", guild=discord.Object(id=common.SERVER_ID))
async def zcreate_userCmd(inter:discord.Interaction, user:discord.User):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if check_user_exist(user.id):
        return await inter.response.send_message(embed=create_embed(None, "User already exists."))
    common.DB.insert_user(user.id, user.name)
    return await inter.response.send_message(embed=create_embed("Create", "User has been created."))

@bot.tree.command(name="zcreate_champ", description="Create a champion", guild=discord.Object(id=common.SERVER_ID))
async def zcreate_champCmd(inter:discord.Interaction, name:str, title:str,gender:str,role:str,type:str,race:str,resource:str,typeautoattack:str,region:str,releaseyear:int, search_name:str,url:str):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if check_champ_exist(search_name):
        return await inter.response.send_message(embed=create_embed(None, "Champion already exists."))
    try:
        telecharge_image(url,"pictures",search_name.capitalize()+".png")
    except:
        return await inter.response.send_message(embed=create_embed(None, "Invalid URL."))
    common.DB.insert_champion(name, title, gender, role, type, race, resource, typeautoattack, region, releaseyear, search_name)
    return await inter.response.send_message(embed=create_embed("Create", "Champion has been created."))

@bot.tree.command(name="zupdate_point", description="Update points of a user by adding points", guild=discord.Object(id=common.SERVER_ID))
async def zupdate_pointCmd(inter:discord.Interaction, user:discord.User, points:int):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not check_user_exist(user.id):
        return await inter.response.send_message(embed=create_embed(None, "User not found."))
    common.DB.update_points_by_id(points, user.id)
    return await inter.response.send_message(embed=create_embed("Update", "Points have been updated."))

@bot.tree.command(name="zupdate_champ_url", description="Update a champion", guild=discord.Object(id=common.SERVER_ID))
async def zupdate_champ_urlCmd(inter:discord.Interaction, search_name:str="",url:str=""):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not check_champ_exist(search_name):
        return await inter.response.send_message(embed=create_embed(None, "Champion not found."))
    search_name = search_name.capitalize()
    try:
        telecharge_image(url, "pictures", search_name + ".png")
    except:
        return await inter.response.send_message(embed=create_embed(None, "Invalid URL."))

@bot.tree.command(name="zdelete_user", description="Delete a user", guild=discord.Object(id=common.SERVER_ID))
async def zdelete_userCmd(inter:discord.Interaction, user:discord.User):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not check_user_exist(user.id):
        return await inter.response.send_message(embed=create_embed(None, "User not found."))
    common.DB.delete_user_by_id(user.id)
    return await inter.response.send_message(embed=create_embed("Delete", "User has been deleted."))

@bot.tree.command(name="zdelete_champ", description="Delete a champion", guild=discord.Object(id=common.SERVER_ID))
async def zdelete_champCmd(inter:discord.Interaction, search_name:str):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not check_champ_exist(search_name):
        return await inter.response.send_message(embed=create_embed(None, "Champion not found."))
    common.DB.delete_champion_by_search_name(search_name)
    return await inter.response.send_message(embed=create_embed("Delete", "Champion has been deleted."))


