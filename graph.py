import os
import matplotlib.pyplot as plt
""" 
episodes=os.listdir("train_all_team")
episodes=[int(x.split("_")[1].split(".")[0])for x in episodes]
episodes.sort()
turns=[]
switch=[]
reward={"win":[],"lose":[],"total":[]}
teams={}
Actor_loss={"win":[],"lose":[]}
Critic_loss={"win":[],"lose":[]}
ep=0
for e in episodes:
    
    with open ("train_all_team/episode_"+str(e)+".txt", mode="r") as f:
        stats=f.read()
    stats=stats.split("\n")
    turn, sw, r_w, r_l, r_t=[float(s.split(": ")[1]) for s in stats[:5]]
    turns.append(turn)
    switch.append(sw)
    reward["win"].append(r_w)
    reward["lose"].append(r_l)
    reward["total"].append(r_t)
    sts1=[s.split(": ") for s in stats[7:-4]]
    
    for i in range(len(sts1)):
        team=sts1[i][0]
        rate=sts1[i][1]
        if sts1[i][0] in teams.keys():
            teams[team].append(float(rate)+teams[team][-1]/2)
        else:
            teams[team]=[0 for k in range(ep)]
            teams[team].append(float(rate)/2)
    for t in teams.keys():
        if t not in [s[0] for s in sts1]:
            teams[t].append(teams[t][-1])
    ep+=1
    a_l, a_w, c_l, c_w=[s.split(": ")[1] for s in stats[-4:]]
    Actor_loss["win"].append(float(a_w))
    Actor_loss["lose"].append(float(a_l))
    Critic_loss["win"].append(float(c_w))
    Critic_loss["lose"].append(float(c_l))


epochs = range(50, 2050, 50)
plt.figure(figsize=(10, 6))
plt.plot(epochs, [reward["win"][i]/turns[i] for i in range(len(turns))], label="vittoria")
plt.plot(epochs, [reward["lose"][i]/turns[i] for i in range(len(turns))], label="sconfitta")
plt.plot(epochs, [reward["total"][i]/turns[i] for i in range(len(turns))], label="totale")
    

plt.xlabel("Epoche")
plt.ylabel("Reward")
plt.legend()
plt.grid(True)
plt.show()

epochs = range(50, 2050, 50)
plt.figure(figsize=(10, 6))
plt.plot(epochs, turns, label="n° turni")
plt.plot(epochs, switch, label="n° switch")
    

plt.xlabel("Epoche")
plt.legend()
plt.grid(True)
plt.show()

epochs = range(50, 2050, 50)
plt.figure(figsize=(10, 6))
plt.plot(epochs, Actor_loss["win"], label="actor vittoria")
plt.plot(epochs, Actor_loss["lose"], label="actor sconfitta")
plt.plot(epochs, Critic_loss["win"], label="critic vittoria")
plt.plot(epochs, Critic_loss["lose"], label="critic sconfitta")
    

plt.xlabel("Epoche")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show() """


episodes=os.listdir("train_all_team_VS_umans")
episodes=[int(x.split("_")[1].split(".")[0])for x in episodes]
episodes.sort()
turns=[]
switch=[]
reward={"win":[],"lose":[],"total":[]}
teams={}
Actor_loss={"win":[],"lose":[]}
Critic_loss={"win":[],"lose":[]}
elos=[]
wins1=[]
wins2=[]
ep=0
for e in episodes:
    
    with open ("train_all_team_VS_umans/episode_"+str(e)+".txt", mode="r") as f:
        stats=f.read()
    stats=stats.split("\n")
    turn, sw, r_w, r_l, r_t, wr1, wr2=[float(s.split(": ")[1]) for s in stats[:7]]
    turns.append(turn)
    switch.append(sw)
    reward["win"].append(r_w)
    reward["lose"].append(r_l)
    reward["total"].append(r_t)
    wins1.append(wr1)
    wins2.append(wr2)
    sts1=[s.split(": ") for s in stats[8:-5]]
    
    for i in range(len(sts1)):
        team=sts1[i][0]
        rate=sts1[i][1]
        if sts1[i][0] in teams.keys():
            teams[team].append(float(rate)+teams[team][-1]/2)
        else:
            teams[team]=[0 for k in range(ep)]
            teams[team].append(float(rate)/2)
    for t in teams.keys():
        if t not in [s[0] for s in sts1]:
            teams[t].append(teams[t][-1])
    ep+=1
    a_l, a_w, c_l, c_w, elo=[float(s.split(": ")[1]) for s in stats[-5:]]
    Actor_loss["win"].append(a_w)
    Actor_loss["lose"].append(a_l)
    Critic_loss["win"].append(c_w)
    Critic_loss["lose"].append(c_l)
    elos.append(elo)
    
    
""" epochs = range(100, 1100, 100)
i=0
plt.figure(figsize=(18, 6))
for team, win_rates in teams.items():
    plt.plot(epochs, [w*15 for w in win_rates], label="team "+str(i))
    i+=1

plt.xlabel("Epoche")
plt.ylabel("Win Rate")
plt.legend()
plt.grid(True)
plt.show()

epochs = range(100, 1100, 100)
plt.figure(figsize=(10, 6))
plt.plot(epochs, [reward["win"][i]/turns[i] for i in range(len(turns))], label="vittoria")
plt.plot(epochs, [reward["lose"][i]/turns[i] for i in range(len(turns))], label="sconfitta")
plt.plot(epochs, [reward["total"][i]/turns[i] for i in range(len(turns))], label="totale")
    

plt.xlabel("Epoche")
plt.ylabel("Reward")
plt.legend()
plt.grid(True)
plt.show()

epochs = range(100, 1100, 100)
plt.figure(figsize=(10, 6))
plt.plot(epochs, turns, label="n° turni")
plt.plot(epochs, switch, label="n° switch")
    

plt.xlabel("Epoche")
plt.legend()
plt.grid(True)
plt.show()

epochs = range(100, 1100, 100)
plt.figure(figsize=(10, 6))
plt.plot(epochs, Actor_loss["win"], label="actor vittoria")
plt.plot(epochs, Actor_loss["lose"], label="actor sconfitta")
plt.plot(epochs, Critic_loss["win"], label="critic vittoria")
plt.plot(epochs, Critic_loss["lose"], label="critic sconfitta")
    

plt.xlabel("Epoche")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show() """

epochs = range(100, 1100, 100)
plt.figure(figsize=(10, 6))
plt.plot(epochs, [wins1[0]]+[(wins1[i]+wins1[i-1])/2 for i in range(1, len(wins1))], label="addestramento")
plt.plot(epochs, [wins2[0]]+[(wins2[i]+wins2[i-1])/2 for i in range(1, len(wins2))], label="test")

    

plt.xlabel("Epoche")
plt.ylabel("win Rate")
plt.legend()
plt.grid(True)
plt.show()

""" epochs = range(100, 1100, 100)
plt.figure(figsize=(10, 6))
plt.plot(epochs, [elos[0]]+[(elos[i]+elos[i-1])/2 for i in range(1, len(elos))])
    

plt.xlabel("Epochs")
plt.ylabel("Elo")
plt.legend()
plt.grid(True)
plt.show()
 """

episodes=os.listdir("test_VS_umans")
episodes=[int(x.split("_")[1].split(".")[0])for x in episodes]
elos=[]
wins1=[]
ep=0
for e in episodes:
    
    with open ("test_VS_umans/episode_"+str(e)+".txt", mode="r") as f:
        stats=f.read()
    stats=stats.split("\n")
    win, elo=[float(s.split(": ")[1]) for s in stats[2:4]]
    wins1.append(win)
    elos.append(elo)
    
print(sum(wins1)/10)
epochs = range(100, 1100, 100)

plt.figure(figsize=(10, 6))
plt.plot(epochs, [elos[0]*wins1[0]]+[(elos[i]*wins1[i]+elos[i-1]*wins1[i-1])/2 for i in range(1,len(elos))])

plt.xlabel("Epoche")
plt.ylabel("Elo X Win Rate")
plt.legend()
plt.grid(True)
plt.show()
