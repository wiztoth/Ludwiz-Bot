import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import utilites
from spellbook import Spellbook
from weaponsbook import WeaponsBook
import pymysql
from auth import *
import helpmenu
import utilites
import random
import os
import re

token = token
# bot initalization
bot = commands.Bot(command_prefix='!', description='Un taverniere che ti aiuta nella tua sessione D&D.')
bot.remove_command('help')

# get spells by class command - it gets a list with names of spells available

@bot.command()
async  def incantesimi(ctx,dnd_class: str,level: int):
    classes = ['barbaro', 'bardo', 'chierico', 'druido', 'guerriero', 'ladro', 'mago', 'monaco', 'paladino',
                  'stregone', 'ranger', 'warlock']
    #force arg to be lower
    dnd_class_lower = dnd_class.casefold()
    if(dnd_class_lower in classes and level<10):
        #await ctx.send("``` "+classe+" "+str(livello)+" ```")
        level = str(level)
        #embed limit is up to 25 fields, so i need a flag to create a new embed after 25 spells found
        flag=0
        manual_dnd = Spellbook("db_user", "db_psw", "db_host", "db_name")
        spells_found = manual_dnd.countSpells(dnd_class_lower, level)
        i=0
        spells = manual_dnd.get_spells_by_class_level(dnd_class_lower,level)
        embed = discord.Embed(title=dnd_class_lower.capitalize(), color=0x66ff66)
        embed2 = discord.Embed(title=dnd_class_lower.capitalize(), color=0x66ff66)
        for spell in spells:
            for spell_name,spell in spell.items():
                if(i<25):
                    embed.add_field(name="Livello"+level,value=spell,inline=True)
                    i=i+1
                else:
                    flag=1
                    embed2.add_field(name="Livello " + level, value=spell,inline=True)
                    i=i+1
        await ctx.send(embed=embed)
        if (flag == 1):
            await ctx.send(embed=embed2)
       

    else:
        if(level<10):
            await ctx.send("``` "+dnd_class+" non esistente e mentre livello "+str(level)+" valido ```")
        else:
            await ctx.send("``` " + dnd_class_lower + " non esistente e livello " + str(level) + " non valido ```")

# random-character generator command - just to have fun with your friends on generate strange characters :)
@bot.command()
async def generapg(ctx, *args):
        classes = ['Barbaro', 'Dardo', 'Chierico', 'Druido', 'Guerriero', 'Ladro', 'Mago', 'Monaco', 'Paladino',
              'Stregone', 'Ranger', 'Warlock']
        races = ['Elfo','Halfling','Nano','Umano','Dragonide','Gnomo','Mezzoelfo','Mezzorco','Tiefling']
        embed = discord.Embed(title="Generatore di personaggi", color=0x66ff66,description="Salve avventuriero! Siete nuovo da queste parti.. chi siete?")
        for i in range(3):
            dnd_class = random.choice(classes)
            race = random.choice(races)
            embed.add_field(name="Opzione " + str(i+1), value=dnd_class+" "+race, inline=False)
        await ctx.send(embed=embed)


# get single weapon with details command
@bot.command()
async def arma(ctx, *args):
            dnd_manual = WeaponsBook("db_user", "db_password", "db_host", "db_name")
            weapon = utilites.PasteStringSpace(args)
            weapon = weapon.lower()
            content_onBook = dnd_manual.getWeapons(weapon)
            if(content_onBook):
                for tupla in content_onBook:
                    embed = discord.Embed(title=weapon.capitalize(), color=0x66ff66)
                    for column, value in tupla.items():
                        if(column=="Nome"):
                            embed.title=value
                        embed = embed.add_field(name=column, value=value, inline=True)
                    await ctx.send(embed=embed)
                    
            else:
                await ctx.send("```Non trovo l'arma ["+weapon.capitalize()+"]```")
                

# get weapons by category command - it gets a list with weapon available in input category
@bot.command()
async def vediarmi(ctx,*args):
        #here there is a limiter and countFieldsMax to bypass embed limit on discord.py class that's up to 25 fields (i set up to 24)
        dnd_manual = WeaponsBook("db_user", "db_password", "db_host", "db_name")
        category = utilites.PasteStringSpace(args)
        category = category.lower()
        if('semplici' in category):
            category='arma semplice'
        bookContent = dnd_manual.getWeapons_by_category(category)
        if(bookContent):
            embed = discord.Embed(title=category.capitalize(), color=0x66ff66)
            embed_second = discord.Embed(title=category.capitalize(), color=0x66ff66)
            embed_third = discord.Embed(title=category.capitalize(), color=0x66ff66)
            i=0
            flag=0
            for tupla in bookContent:
                for column,value in tupla.items():
                    if(column != "Categoria"):
                        if(i<24):
                            embed.add_field(name=column,value=value)
                            i=i+1
                        elif(i<48):
                                flag=1
                                embed_second.add_field(name=column, value=value)
                                i = i + 1
                        elif(i<96):
                                flag=2
                                embed_third.add_field(name=column,value=value)
                                i=i+1
                    else:
                        embed.title=value
                        embed_second.title=value
                        embed_third.title=value
            await ctx.send(embed=embed)
            if(flag==1):
                await ctx.send(embed=embed_second)
            if(flag==2):
                await ctx.send(embed=embed_second)
                await ctx.send(embed=embed_third)
            
        else:
            await ctx.send("```Non trovo le armi di categoria [" + category.capitalize() + "]```")
           
# ready-bot command
@bot.event
async def on_ready():
    print('Sono pronto viandante!')

# get single spell with details command
@bot.command()
async def incanto(ctx, *args):
    MAX_SIZE = 1024
    spell = utilites.PasteStringSpace(args)
    print(spell)
    dnd_manual = Spellbook("db_user", "db_psw", "db_host", "db_name")
    content_onBook = dnd_manual.get_spells_by_name(spell)
    embed = discord.Embed(title=spell.capitalize(),color=0x66ff66)
    conts = []
    if (len(content_onBook)==1):
        embed = discord.Embed(title=spell.capitalize(),color=0x66ff66)
        tupla = content_onBook[0]
        for column,value in tupla.items():
            if (column == 'Nome'):
                spellName = value
                embed.title = value
            else:
                if(column == 'Descrizione'):
                    splits = [value[i:i+MAX_SIZE] for i in range(0,len(value),MAX_SIZE)]
                    embed.add_field(name=column,value=splits[0],inline=True)
                    splits = splits [1:]
                    for split in splits:
                        em = discord.Embed(title=spellName + " - Continua",color=0x66ff66)
                        conts.append(em.add_field(name="Descrizione",value=split,inline=True))
                else:
                    embed = embed.add_field(name=column,value=value,inline=True)
    else:
        spellToFind = spell
        for spell in content_onBook:
            if("Nome" in spell):
                embed.description="La parola "+str(spellToFind)+' ha dato molti risultati, specifica meglio tra i seguenti: '
                embed = embed.add_field(name="Nome",value=spell["Nome"],inline=True)

    await ctx.send(embed=embed)
    if len(conts) > 0 :
        for em in conts:
            await ctx.send(embed=em)


# Help commands
@bot.command()
async def aiuto(ctx, *args):
        await ctx.send(helpmenu.helpGeneral())
@bot.command()
async  def aiutodadi(ctx):
    await ctx.send(helpmenu.helpDices())
@bot.command()
async  def aiutoincantesimi(ctx):
    await ctx.send(helpmenu.helpSpells())
@bot.command()
async  def aiutoarmi(ctx):
    await ctx.send(helpmenu.helpWeapons())

# dice-rolling command
@bot.command()
async def lancia(ctx,*args):
        arg = args
        regex = re.compile('^(\d{0,4}d\d{1,3})((\s*\+\s*)(\d*))?\s*$')
        vault = 0
        stop = 0
        atLeastOneTime = 0
        minus = str(arg).find('-')
        division = str(arg).find('/')
        multiplicate = str(arg).find('*')
        converted = utilites.PasteString(arg)
        risultato = regex.match(converted)
        if risultato != None:
            if( minus == -1 and division == -1 and multiplicate == -1):
                for arg in args:
                    argstring = str(arg)
                    found = argstring.find('d')
                    foundSign = argstring.find('+')
                    if (found != -1):
                        atLeastOneTime = 1
                        diceToRoll = argstring.split('d')
                        quantity = diceToRoll.__getitem__(0)
                        valueOfDice = diceToRoll.__getitem__(1)
                        print(' Devo lanciare il dado '+valueOfDice)
                        print(' Devo lanciarlo per n: '+quantity)
                        if('+' in valueOfDice):
                            await ctx.send("```Hai dimenticato lo spazio? devi scrivere !lancia d[valore] + [modificatore] ```")
                            break
                        if(int(valueOfDice)>200):
                            stop = 1
                            await ctx.send("```Mi spiace ma non abbiamo un dado con "+str(valueOfDice)+"```")

                        if(stop == 1):
                            break
                        if(quantity != ''):
                            if (quantity != '-'):
                                if int(quantity)>9:
                                    await ctx.send("```Mi spiace, non puoi lanciare " + str(quantity) + " dadi```")
                                    stop = 1
                                for i in range(int(quantity)):
                                    if(stop == 0):
                                        num = utilites.rolling(int(valueOfDice))
                                        vault = num+vault
                                        vault = utilites.store(vault)
                                        await ctx.send("```Il lancio del tuo dado d"+str(valueOfDice)+" è : [" + str(num) + "]```")

                        else:
                            num = utilites.rolling(int(valueOfDice))
                            vault= utilites.store(num)
                            await ctx.send("```Il lancio del tuo dado d"+str(valueOfDice)+" è : [" + str(num) + "]```")

                    if (foundSign == -1 and found == -1):
                        if (atLeastOneTime == 0):
                            await ctx.send("```Sintassi errata! - devi scrivere !lancia [numero]d[valore dado] + [modificatore]```")
                        vault = utilites.store(vault)
                        Modifier = argstring
                        TotalDiceRollWithModifier = int(Modifier)+vault
                        await ctx.send("```Il lancio dei tuoi dadi è di " + str(vault) + " con modificatore [" + str(Modifier) + "]"+" = "+ str(TotalDiceRollWithModifier)+"```")
                    else:
                        Modifier = arg.split(',')
                        succ = Modifier.__getitem__(0)
                        wrong=1
                        error_flag=0
                        if(succ == '+'):
                            succ = Modifier.__getitem__(0)
                            print("succ "+succ)
                        else:
                            wrong = wrong + 1
                            if(wrong>1):
                                error_flag=1
                        print(error_flag)
                        if(error_flag==1 and foundSign != -1):
                            await ctx.send("```Non hai messo lo spazio, devi scrivere !lancia d"+str(valueOfDice)+" + [Modificatore] con lo spazio```")
                            break

        else:
            if(minus != -1):
                for arg in args:
                    argstring = str(arg)
                    found = argstring.find('d')
                    foundSign = argstring.find('-')
                    if (found != -1):
                        atLeastOneTime = 1
                        diceToRoll = argstring.split('d')
                        quantity = diceToRoll.__getitem__(0)
                        valueOfDice = diceToRoll.__getitem__(1)
                        print(' Devo lanciare il dado '+valueOfDice)
                        print(' Devo lanciarlo per n: '+quantity)
                        if(int(valueOfDice)>200):
                            stop = 1
                            await ctx.send("```Mi spiace ma non abbiamo un dado con "+str(valueOfDice)+"```")

                        if(stop == 1):
                            break
                        if(quantity != ''):
                            if (quantity != '-'):
                                if int(quantity)>9:
                                    await ctx.send("```Mi spiace, non puoi lanciare " + str(quantity) + " dadi```")
                                    stop = 1
                                for i in range(int(quantity)):
                                    if(stop == 0):
                                        num = utilites.rolling(int(valueOfDice))
                                        vault = num+vault
                                        vault = utilites.store(vault)
                                        await ctx.send("```Il lancio del tuo dado d"+str(valueOfDice)+" è : [" + str(num) + "]```")

                        else:
                            num = utilites.rolling(int(valueOfDice))
                            vault= utilites.store(num)
                            await ctx.send("```Il lancio del tuo dado d"+str(valueOfDice)+" è : [" + str(num) + "]```")

                    if (foundSign == -1 and found == -1):
                        if (atLeastOneTime == 0):
                            await ctx.send("```Sintassi errata! - devi scrivere !lancia [numero]d[valore dado] + [modificatore]```")
                        vault = utilites.store(vault)
                        Modifier = argstring
                        TotalDiceRollWithModifier = vault - int(Modifier)
                        await ctx.send("```Il lancio dei tuoi dadi è di " + str(vault) + " con modificatore [-" + str(Modifier) + "]"+" = "+ str(TotalDiceRollWithModifier)+"```")
                    else:
                        Modifier = arg.split(',')
                        succ = Modifier.__getitem__(0)
                        wrong=1
                        error_flag=0
                        if(succ == '-'):
                            succ = Modifier.__getitem__(0)
                            print("succ "+succ)
                        else:
                            wrong = wrong + 1
                            if(wrong>1):
                                error_flag=1
                        print(error_flag)
                        if(error_flag==1 and foundSign != -1):
                            await ctx.send("```Non hai messo lo spazio, devi scrivere !lancia d"+str(valueOfDice)+" + [Modificatore] con lo spazio```")
                            break


            else:
                 await ctx.send("```Hai sbagliato qualcosa?\n"
                               "Ti ricordo che NON puoi fare le seguenti cose:\n"
                               "> Lanciare dadi sopra le 200 facce.\n"
                               "> Lanciare contemporaneamente piu' di 9 dadi per volta.\n"
                               "> Usare moltiplicazione o divisione per i tuoi modificatori.\n"
                               "> Non mettere lo spazio tra dado e modificatore, il lancio del dado sarà eseguito lo stesso ma senza modificatore.\n"   
                               "> Utilizzare piu' di un modificatore, è consentito !lancia 2d20 + 3, ma non !lancia 2d20 + 3 + 4.\n\n"
                               "> Esempio corretto di sintassi per il lancio dei dadi: !lancia d20 + 1 - !lancia 2d20 + 3 - !lancia d8 - !lancia 3d8 + 4"
                               "```")


#cleaning chat-text channel with this command - keep attention using this
@bot.command()
async def pulisci(ctx, amount: str):
    if('tutto' in amount):
        amount=100000
        await ctx.channel.purge(limit=amount)
        await ctx.send("```Ecco fatto! La taverna adesso è pulita```")
        print('pulito tutto')

#token is in auth.py
bot.run(token)
