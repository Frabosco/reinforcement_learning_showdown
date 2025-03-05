import random
import requests
import time
import csv
import os
import pandas as pd
from costant import ITEM, MOVES, POKEDEX, CONDICTION, FIELD, WEATHER, STATUS, STS, TYPE, NC,NF,NI,NMV,NPKM,NS,NT,NW

def matchParcer(file, match):
    turnLogs=[]
    for log in file.split("|turn|"):  #extraing the battle log
        turnLogs.append(log.split("\n"))
    turnLogs.pop(-1)
    
    teams=[{},{}]
    activePK=[[["",""],["",""]]]
    backPK=[[[],[]]]
    weaters=[-1]
    fields=[-1]
    sCondictions=[-1]
    tMoves=[[["",""],["",""]]]
    pos1=1
    pos2=1
    pk={"pos":-1,"n":-1,"t1":-1,"t1":-1,"hp":1,"moves":[-1,-1,-1,-1],"item":-1,"eff":-1,"tera":-1, "atk":0,"def":0,"spa":0,"spd":0,"spe":0,"accuracy":0,"evasion":0}
    turns1=[[-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,1,-1,1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,1,-1,1,-1,-1,-1]]
    turns2=[[-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,1,-1,1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,-1,1,-1,1,-1,-1,-1]]
    matchLog=match
    for i in range(len(turnLogs)):
        activePK.append(activePK[i].copy())
        backPK.append(backPK[i].copy())
        weaters.append(weaters[i])
        fields.append(fields[i])
        sCondictions.append(sCondictions[i])
        tMoves.append([["",""],["",""]])
        matchLog=matchLog+"\nTURN: "+str(i)
        for l in turnLogs[i]:
            line=l.lower().split("|")
            prefix=""
            if len(line)<2:
                continue
            else:
                prefix=line[1]
            if prefix=="move":
                team1=int(line[2][1])-1
                if line[4]!="":
                    team2=int(line[4][1])-1
                pokemon=line[2].split(": ")[1].split("-")[0].replace(" ","")
                pos=int(activePK[i+1][team1].index(pokemon))
                ab=line[2][2]
                
                if line[4]=="":
                    target=str(random.randint(1,4))
                elif team1==team2:
                    target=str(pos+1)
                else:
                    target=str(activePK[i+1][team2].index(line[4].split(": ")[1].split("-")[0].replace(" ",""))+2)
                move=MOVES[line[3].replace(" ","").replace("-","")]["num"]/NMV
                if move not in teams[team1][pokemon]["moves"]:
                    teams[team1][pokemon]["moves"].append(move)
                    teams[team1][pokemon]["moves"].pop(0)
                st=str(teams[team1][pokemon]["moves"].index(move)+1)+target+ab
            
                if teams[team1][pokemon]["tera"]>0:
                    st+="t"
                tMoves[i][team1][pos]=st
                matchLog=matchLog+"\nMove pokemon: "+pokemon+" move: "+line[3]+" to: "+target
            elif  prefix=="poke":
                team=line[2]
                if team=="p1":
                    t=0
                    pos=pos1
                    pos1+=1
                else:
                    t=1
                    pos=pos2
                    pos2+=1
                name=line[3].split(",")[0].replace(" ","").strip("*")
                pk=POKEDEX[name.replace("-","")]
                n=pk["num"]/NPKM
                t1=getattr(TYPE, pk["types"][0].upper()).value/NT
                t2=getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1
                pokemon={
                "pos":pos,
                "n":n,
                "t1":t1,
                "t2":t2,
                "hp":1,
                "moves":[-1,-1,-1,-1],
                "item":-1,
                "tera":-1,
                "eff":-1,
                "atk":0,"def":0,"spa":0,"spd":0,"spe":0,"accuracy":0,"evasion":0
                }
                teams[t][name.split("-")[0]]=pokemon
            elif prefix=="-damage":
                team=int(line[2][1])-1
                pokemon=line[2].split(": ")[1].split("-")[0].replace(" ","")
                hp=int(line[3].split("/")[0].replace("fnt",""))/100
                teams[team][pokemon]["hp"]=hp
                matchLog=matchLog+"\n"+pokemon+" hp: "+str(hp)
            elif prefix=="switch" or prefix=="drag" or prefix=="replace":
                pokemon=line[3].split(",")[0].split("-")[0].replace(" ","").strip("*").replace("crowned","")
                if pokemon!=line[2].split(": ")[1].split("-")[0].replace(" ","").strip("*").replace("crowned",""):
                    return
                team=int(line[2][1])-1
                if line[2][2]=="a":
                    slot=0
                else:
                    slot=1
                sPokemon=activePK[i][team][slot]
                if sPokemon!="":
                    teams[team][sPokemon]["pos"]=slot+3
                    if teams[team][sPokemon]["hp"]==0:
                        sPokemon=-1
                    if pokemon in backPK[i+1][team]:
                        backPK[i+1][team][backPK[i+1][team].index(pokemon)]=sPokemon
                    else:
                        backPK[i+1][team].append(sPokemon)
                    teams[team][pokemon]["pos"]=slot+1
                activePK[i+1][team][slot]=pokemon
                if(tMoves[i][team][slot]==""):
                    tMoves[i][team][slot]=str(slot+1)+"s"+str(teams[team][pokemon]["pos"])
                else:
                    tMoves[i][team].append(str(slot+1)+"s"+str(teams[team][pokemon]["pos"]))
                teams[team][pokemon]["pos"]=slot+1
                matchLog=matchLog+"\nswitch team:"+str(team)+" in: "+pokemon+" out: "+str(sPokemon)
            elif prefix=="-weather":
                w=line[2].upper()
                if w!="NONE":
                    weaters[i+1]=getattr(WEATHER,w).value/NW
                else:
                    weaters[i+1]=0
                matchLog=matchLog+"\nweathers : "+line[2]
            elif prefix=="-clearallboost":
                for pokemon in teams[0]:
                    for sts in STS:
                        teams[0][pokemon][sts]=0
                    matchLog=matchLog+"\ncelar boost: "+pokemon
                for pokemon in teams[1]:
                    for sts in STS:
                        teams[1][pokemon][sts]=0
                    matchLog=matchLog+"\ncelar boost: "+pokemon
            elif prefix=="-copyboost":
                team1=int(line[2][1])-1
                team2=int(line[3][1])-1
                pk1=line[2].split(": ")[1].replace(" ","").split("-")[0]
                pk2=line[3].split(": ")[1].replace(" ","").split("-")[0]
                for sts in STS:
                    teams[team1][pk1][sts]=teams[team2][pk2][sts]
            elif prefix=="-clearboost" or prefix=="-clearnegativeboost":
                team=int(line[2][1])-1
                for pokemon in teams[team]:
                    for sts in STS:
                        teams[team][pokemon][sts]=0
                    matchLog=matchLog+"\ncelar boost: "+pokemon
            elif prefix=="-unboost" or prefix=="-boost":
                team=int(line[2][1])-1
                pokemon=line[2].split(": ")[1].split("-")[0].replace(" ","")
                sts=line[3]
                if line[1]=="-unboost":
                    teams[team][pokemon][sts]-=(int(line[4])/6)
                else:
                    teams[team][pokemon][sts]+=(int(line[4])/6)
                matchLog=matchLog+"\n"+line[1]+": "+pokemon+" sts: "+line[3]+" of: "+line[4]
            elif prefix=="-heal":
                team=int(line[2][1])-1
                pokemon=line[2].split(": ")[1].split("-")[0].replace(" ","")
                hp=int(line[3].split("/")[0].replace("fnt",""))/100
                teams[team][pokemon]["hp"]=hp
                matchLog=matchLog+"\n"+pokemon+" hp: "+str(hp)
            elif prefix=="-status":
                team=int(line[2][1])-1
                pokemon=line[2].split(": ")[1].replace(" ","").split("-")[0]
                sts=line[3].upper()
                teams[team][pokemon]["eff"]=getattr(STATUS,sts).value/NS
                matchLog=matchLog+"\nstaus: "+pokemon+sts
            elif prefix=="-enditem":
                team, name=line[2].split(": ")
                teams[int(team[1])-1][name.replace(" ","").split("-")[0]]["item"]=ITEM[line[3].replace(" ","")]/NI
            elif prefix=="faint":
                team=int(line[2][1])-1
                pokemon=line[2].split(": ")[1].split("-")[0].replace(" ","")
                teams[team][pokemon]["hp"]=0
                matchLog=matchLog+"\nfaint, team: "+str(team)+" pk: "+pokemon
            elif prefix=="-fieldstart":
                fields[i+1]=getattr(FIELD,line[2].split(": ")[1].upper().replace(" ","_")).value/NF
                matchLog=matchLog+"\nfield: "+line[2].split(": ")[1]
            elif prefix=="-terastallize":
                team=int(line[2][1])-1
                pokemon=line[2].split(": ")[1].replace(" ","").split("-")[0]
                type=line[3].upper()
                teams[team][pokemon]["tera"]=getattr(TYPE, type).value/NT
                matchLog=matchLog+"\ntera:"+pokemon+" type: "+type
            elif prefix=="showteam":
                team=int(line[2][1])-1
                pokemons=l.lower().split("]")
                pokemons[0]=pokemons[0][13:]
                pos=1
                for pokemon in pokemons:
                    info=pokemon.split("|")
                    name=info[0].replace(" ","")
                    item=ITEM[info[2]]/NI

                    moves=info[4].split(",")
                    for m in range(len(moves)):
                        moves[m]=MOVES[moves[m]]["num"]/NMV
                    tera=getattr(TYPE, info[11].split(",")[-1].upper()).value/NT
                    pk=POKEDEX[name.replace("-","")]
                    n=pk["num"]/NPKM
                    t1=getattr(TYPE, pk["types"][0].upper()).value/NT
                    t2=getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1
                    pokemon={
                    "pos":pos,
                    "n":n,
                    "t1":t1,
                    "t2":t2,
                    "hp":1,
                    "moves":[-1,-1,-1,-1],
                    "item":-1,
                    "tera":tera,
                    "eff":-1,
                    "atk":0,"def":0,"spa":0,"spd":0,"spe":0,"accuracy":0,"evasion":0
                    }
                    teams[team][name.split("-")[0]]=pokemon
                    pos+=1
            elif prefix=="-sidestart":
                if line[3].upper().replace(" ","_").split(":_")[0]!="MOVE":
                    cond=line[3].upper().replace(" ","_").split(":_")[0]
                else:
                    cond=line[3].upper().replace(" ","_").split(":_")[1]
                sCondictions[i+1]=getattr(CONDICTION,cond).value/NC
            elif prefix=="swap":
                team=int(line[2][1])-1
                pk1, pk2=activePK[i+1][team]
                activePK[i+1][team]=[pk2,pk1]
                teams[team][pk1]["pos"]=2
                teams[team][pk2]["pos"]=1
        pk1=teams[0][activePK[i+1][0][0]].copy()
        m1=pk1["moves"]
        pk1=[v for v in pk1.values()]
        pk1=pk1[1:5]+m1+pk1[6:]
        pk2=teams[0][activePK[i+1][0][1]].copy()
        m2=pk2["moves"]
        pk2=[v for v in pk2.values()]
        pk2=pk2[1:5]+m2+pk2[6:]
        pk3=teams[1][activePK[i+1][1][0]].copy()
        m3=pk3["moves"]
        pk3=[v for v in pk3.values()]
        pk3=pk3[1:5]+m3+pk3[6:]
        pk4=teams[1][activePK[i+1][1][1]].copy()
        m4=pk4["moves"]
        pk4=[v for v in pk4.values()]
        pk4=pk4[1:5]+m4+pk4[6:]
        bk1=[-1,-1,-1,1,-1,-1,-1,1]
        bk2=[-1,-1,-1,1,-1,-1,-1,1]
        if not backPK[i+1][0]:
            for j in range(len(backPK[i+1][0])):
                bk1[j]=teams[0][backPK[i+1][0][j]]["n"]+teams[0][backPK[i+1][0][j]]["t1"]+teams[0][backPK[i+1][0][j]]["t2"]+teams[0][backPK[i+1][0][j]]["hp"]
        if not backPK[i+1][1]:
            for j in range(len(backPK[i+1][1])):
                bk2[j]=teams[1][backPK[i+1][1][j]]["n"]+teams[1][backPK[i+1][1][j]]["t1"]+teams[1][backPK[i+1][1][j]]["t2"]+teams[1][backPK[i+1][1][j]]["hp"]
        turns1.append(pk1+pk2+bk1+pk3+pk4+bk2+[weaters[i+1],fields[i+1],sCondictions[i+1]])
        turns2.append(pk3+pk4+bk2+pk1+pk2+bk1+[weaters[i+1],fields[i+1],sCondictions[i+1]])
    t01=[0 for i in range(91)]
    t02=[0 for i in range(91)]
    c=0
    pokemons=list(teams[0].keys())+list(teams[1].keys())
    for i in range(len(pokemons)):
        if i<6:
            pk1=teams[0][pokemons[i]] if pokemons[i] in teams[0].keys() else None
            pk2=teams[1][pokemons[i-6]] if pokemons[i-6] in teams[1].keys() else None
        else:
            pk1=teams[1][pokemons[i]] if pokemons[i] in teams[1].keys() else None
            pk2=teams[0][pokemons[i-6]] if pokemons[i-6] in teams[0].keys() else None
        if pk1 is not None:
            t01[c]=pk1["n"]
            t01[c+1]=pk1["t1"]
            t01[c+2]=pk1["t2"]
        if pk2 is not None:
            t02[c]=pk2["n"]
            t02[c+1]=pk2["t1"]
            t02[c+2]=pk2["t2"]
        c+=7
    turns1[0]=t01
    turns2[0]=t02
    with open('turn_a.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(turns1)
    with open('turn_b.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(turns2)
    with open('moves.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(tMoves)
    with open("log/"+match+".txt", 'w', encoding='UTF8', newline='') as f:
        f.write(matchLog)
        

matchs=[]
def downloadMatch():
    for i in range(1,51):
        response = requests.get("https://replay.pokemonshowdown.com/api/replays/search?username=&format=gen9vgc2025regg&page="+str(i),headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
        ids=response.text.split("\"id\":\"")
        ids=[id.split("\"")[0] for id in ids]
        ids.pop(0)
        ids=list(set(ids))
        for id in ids:
            if id not in matchs and id:
                matchs.append(id)
        print(i)
        time.sleep(0.05)
        
    with open('match.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        # write the data
        writer.writerow(matchs)

tops=os.listdir("toplist")
matchs=[]
for top in tops:
    lists=pd.read_csv("toplist/"+top)
    for l in lists["replay_url"]:
        if "regg" in l:
            matchs.append(l.split("/")[-1].strip("pw"))

with open("match.csv", mode="r")as file:
    mc=csv.reader(file)
    for m in mc:
        matchs=matchs+m

files=os.listdir("log")
files=[f[:-4] for f in files]

for match in matchs:
    print(matchs.index(match)/len(matchs))
    if match not in files:
        response = requests.get("https://replay.pokemonshowdown.com/"+match,headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
        response.raise_for_status()
        file=response.text
        matchParcer(file, match)
