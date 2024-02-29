import bot
import discord
import logging
import datetime
import threading
import os
import requests

bool_start=False
bool_guess=False
hours_default=4
hours_x=0
guess_champ=""
timer_x=datetime.datetime.now()

def telecharge_image(url, dossier,nom_image):
    response=requests.get(url)
    if response.status_code==200:
        chemin_destination=os.path.join(dossier,nom_image)
        with open(chemin_destination,"wb") as f:
            f.write(response.content)
        print("Image téléchargée avec succès")
    else:
        print("Échec du téléchargement de l'image")
def create_embed(title, description):
    color=discord.Color(0xb408ab) #couleur msg embed
    return discord.Embed(title=title, description=description, color=color)

def help_command(message, msg_bureau, msg_cotisant): #msg de debug pour corriger sa commande
    s = ""
    if bot.check_role("Bureau", message):
        s = " ,or , " + msg_bureau
    return create_embed("Help","Just try: " + msg_cotisant + s)

def help_embed(str_):
    return create_embed("Help",str_)

def update_embed(str_):
    return create_embed("Update",str_)

def handle_response(message, strmessage, my_database):
    global bool_start, bool_guess, hours_x, timer_x,guess_champ
    p_message = strmessage.lower()
    author = message.author  #name
    id_author = author.id
    print("Message sent by " + str(message.author) + " : \"" + message.content + "\" [ id: " + str(id_author) + " ]")
    logging.info(
        "Message sent by " + str(message.author) + " : \"" + message.content + "\" [ id: " + str(id_author) + " ]")

    # Crée : un wallet si l'user n'en a pas
    name_author = str(author)
    if not check_user_exist(id_author, my_database):
        my_database.insert_user(id_author)
        return create_embed("You didn't have a profile to guess.. so", "Your profile has been created!")
    elif name_author != my_database.get_user_name_by_id(id_author):  # MAJ : name/pseudo user
        my_database.update_name_by_id(name_author, id_author)

    args = p_message.split() # Parsing commands and arguments

    command = args[0]  # Command word
    if command == 'hello' and len(args) == 1:
        return create_embed(None, "Hey there!")

    if command == "help":
        if len(args) == 1:
            command_summary = """
?hello : Be polite to Drakinia
?info : Display information about the bot
?point : Display your point(s)
?all : Show the list of users
?help : Display the help message
?user : Check ownership of a user profile 
?guess : Display guessing statut 
?g <name_champ> : In guess mode, Allow you to propose a champion
"""
            return create_embed("FridgeFund Bot Commands", command_summary)
        elif len(args) == 2 and args[1] == "bureau" and bot.check_role("Bureau", message):
            supremetie_bureau = """
?help bureau : Display the role-specific help message
?start : Launche the bot and the guesses every 4 hours
?start <x_hours> : Launche the bot and the guesses every x hours
?stop : Stop guessing mode
?point <id_user> : Show the balance of the specified user.
?champs : List all League of Legends champions
?create user <id_user> : Create a new user
?create champ <name> <title> <gender> <role> <type> <race> <resource> <typeautoattack> <region> <releaseyear> <search_name> <url_image_champ> : Create a new champ
?update point <id_user> <amount_added> : Update user's point(s) (add the amount to the point(s))
?delete user <id_user> : Delete a user
?delete champ <champ_name> : Delete a champion
"""
            return create_embed("FridgeFund Bot Commands Requiring 'Bureau' Role", supremetie_bureau)

    if command == "user" and check_user_exist(id_author, my_database):
        return create_embed(None,"You already have a profile..")

    if command == "point":
        if len(args) == 1:
            return affiche_point(id_author, id_author, my_database,"Point(s)")
        elif len(args) == 2 and bot.check_role("Bureau", message) and check_user_exist(args[1], my_database):
            return affiche_point(id_author, int(args[1]), my_database,"Point(s)")

        return help_command(message, "?point id_user", "?point")

    if command == "all":
        if len(args) == 1:
            data = my_database.get_all_users()
            s=""
            t=None
            if not data:
                s= "No user is in the database.."
            else :
                t = "Ranking of Drakiguessors"
                for user in data:
                    id_, name_, points_ = user
                    s += f"Id: {id_} | Pseudo: {name_}, Point(s) : {points_}\n"
            return create_embed(t,s)
        return help_embed("Just try : ?all.")

    if command == "info":
        if len(args) == 1:
            return create_embed(None,"My name is Drakinia, some people prefer to call me as Drakinator. I can help you ?help , to guess LoL Champions!")

    #GUESS MODE **************************************************
    if bool_guess==True and command=="g":
        if len(args)==2:
            name_champ=args[1]
            if check_champ_exist(name_champ,my_database):
                return guess_reponse(name_champ,my_database,id_author)
            else:
                l=len(name_champ)
                while my_database.get_champ_same_firstnletter(l,name_champ,l)==None:
                    l-=1
                data = my_database.get_champ_same_firstnletter(l,name_champ,l)
                s=""
                for champ in data:
                    name_ = champ[0]
                    s += f"{name_} "
                return create_embed("Suggestion(s)",s)
        else:
            return help_embed("Just try : ?g name_champ")
    #**************************************************************

    if command == "guess":
        if bot.choose_update:
            guess_mode(hours_x,my_database)
            bot.choose_update=False
        if len(args) == 1:
            #global bool_start, bool_guess
            if bool_start:
                if bool_guess:
                    return create_embed("Guess","A guess is in progress..")
                else:
                    hours,minutes=how_long_guess_mode_active() #vérifer : heure actuelle - timer_x rste temps avant prochain guess bool_guess
                    return create_embed("Guess","Next guess in "+str(hours)+ " hours and "+str(minutes)+" minutes.")
            else:
                return create_embed("Guess","Drakania is sleeping.. Contact a member of the Bureau!")
        return help_embed("Just try : ?guess.")

    # *************************************** Bureau Suprématie *********************************************
    if command == "start" and bot.check_role("Bureau", message) and not bool_start:
        if len(args)==1 :
            return starting_mode(hours_default,my_database)
        elif len(args) == 2 :
            if is_convertible_to_int(args[1]):
                return starting_mode(int(args[1]),my_database)
        return help_embed("Just try : ?start ,or , ?start x_hours")

    if command == "stop" and bot.check_role("Bureau", message):
        if bool_start :
            if len(args) == 1:
                bool_start=False
                bool_guess=False
                timer_x=datetime.datetime.now()
                return create_embed("Stop","The Drakinia bot has been stopped.")
            return help_embed("Just try : ?stop")
        else : return create_embed(None,"Drakinia is sleeping..")


    if command == "champs" and bot.check_role("Bureau", message) :
        if len(args) == 1:
            data = my_database.get_all_champions()
            s = ""
            av_name = ""
            for champ in data:
                name_ = champ[0].capitalize()  # Obtenez le premier élément du tuple (le nom du champion)
                if not av_name or av_name[0] != name_[0]:
                    s += "\n"
                s += f"{name_}, "
                av_name = name_
            # Supprimez la virgule finale et renvoyez la chaîne formatée
            return create_embed("League of Legends Champions", s[:-2])
        return help_embed("Just try : ?champs")

    if command == "create" and bot.check_role("Bureau", message):
        arg_2 = args[2]
        if len(args)==3 and args[1] == "user" and not check_user_exist(int(arg_2), my_database):
            my_database.insert_user(int(arg_2))
            return create_embed("Create","You created the user : " + str(arg_2))

        if len(args)==14 and args[1] == "champ" and not check_champ_exist(arg_2, my_database):
            my_database.insert_champion(arg_2, args[3], args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11],args[12])
            name_image=str(args[12])
            name_image=name_image[0].upper()+name_image[1:]
            telecharge_image(args[13],"pictures",name_image+".png")
            return create_embed("Create","You created the champion : " + str(arg_2))
        return help_embed("Create: ?create user id_user ,or , ?create champ name_champ title gender role type race resource typeautoattack region releaseyear search_name url_image_champ")

    if command == "update" and bot.check_role("Bureau", message):
        arg_1 = args[1]
        if len(args) == 4:
            arg_2 = args[2]
            arg_3 = args[3]
            if check_user_exist(arg_2, my_database):
                if arg_1 == "point":
                    old_points = my_database.get_points_by_id(arg_2)
                    my_database.update_points_by_id(arg_3, arg_2)
                    return affiche_point(int(id_author), int(arg_2), my_database,"Update") + " [ Old point(s): " + str(
                        old_points) + " ]"
            return help_embed("Try : ?update point id_user money_added")

    if command == "delete" and bot.check_role("Bureau", message):
        arg_1 = args[1]
        if len(args) == 3:
            arg_2 = args[2]
            s=""
            if arg_1 == "user" and check_user_exist(arg_2, my_database):
                name_delete_user = str(my_database.get_user_name_by_id(arg_2))
                my_database.delete_user_by_id(arg_2)
                s= "You have deleted the following user: " + name_delete_user
            elif arg_1 == "champ" and check_champ_exist(arg_2, my_database):
                my_database.delete_champ_by_name(arg_2)
                s= "You have deleted the following champ: " + str(arg_2)
            return create_embed("Delete",s)
        return help_embed("/!\ Delete: ?delete user id_user ,or , ?delete champ name_champ")


def check_user_exist(id, my_database):
    return my_database.user_exist_by_id(id)

def check_champ_exist(name, my_database):
    return my_database.champ_exist_by_name(name)

def affiche_point(id_author, id, my_database,title):
    s = ""
    if id == id_author:
        s = "You have " + str(my_database.get_points_by_id(id_author))
    else:
        s = str(my_database.get_user_name_by_id(id)) + " has " + str(my_database.get_points_by_id(id))
    return create_embed(title, s + " Point(s)")

def is_convertible_to_int(s):
    try:
        int(s)  # Tente de convertir la chaîne en entier
        return True  # La conversion a réussi
    except ValueError:
        return False  # La conversion a échoué

def how_long_guess_mode_active():
    duration = datetime.timedelta(hours=hours_x)
    result_datetime=duration-(datetime.datetime.now()-timer_x)
    total_seconds = result_datetime.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    return hours, minutes

def guess_reponse(name_command,my_database,id):
    global guess_champ, bool_guess
    #"""g_gender, g_role, g_type,g_race,g_resource,g_typeautoattack, g_region, g_year=my_database.get_champion_by_name(guess_champ)
    #c_gender, c_role, c_type,c_race,c_resource,c_typeautoattack, c_region, c_year=my_database.get_champion_by_name(command)"""

    data_g=my_database.get_champion_by_name(guess_champ)
    data_c=my_database.get_champion_by_name(name_command)
    name_champ=my_database.get_name_champ_by_search(name_command)

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
    #'if win==len(t):
    if guess_champ==name_command:
        someone_guessed(my_database)
        bool_guess=False
        my_database.update_points_by_id(10,id)
        e.description="gg ez ( ͡° ͜ʖ ͡°) You guessed "+str(name_champ)+" ! +10 points \n"+'"'+str(my_database.get_champ_title_by_search(name_command))+'"'
    return e,file #voir comment je passe le file, sachant que par défaut None sauf ici !

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

def starting_mode(n_hours,my_database):
    guess_mode(n_hours,my_database)
    return create_embed("Start","Guess mode is activated every "+str(hours_x)+" hours.")

def guess_mode(n_hours,my_database):
    global bool_start, bool_guess, hours_x, timer_x,guess_champ
    hours_x=int(n_hours)
    bool_start=True
    bool_guess=True
    timer_x=datetime.datetime.now()
    guess_champ=my_database.get_champ_random()
    print(guess_champ)

def someone_guessed(my_database):
    print("alled")
    delay_seconds = hours_x * 60 * 60
    timer = threading.Timer(delay_seconds, end_timer, args=(my_database,))
    print(timer)
    timer.start()
    return

def end_timer(my_database):
    print("caca")
    guess_mode(hours_x,my_database)
    return

#Créer une fonction pour les bureaux pour ajouter un nouveau champion : et pour joindre l'image issu de : https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/
