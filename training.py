import asyncio
import torch
from actor import RLPlayer, RandomTeamFromPool
from teams import teams, teams2
from poke_env import SimpleHeuristicsPlayer
from poke_env import AccountConfiguration, ShowdownServerConfiguration
from A2C import Actor, Critic
import torch.nn.functional as F


def update_weight(actor, critic, player, optimizer_critic, optimizer_actor, win, n_win=0):
    act_l=[]
    cri_l=[]
    states=[i for i in player.states if i!=[]]+[[]]
    values=[i for i in player.values if i!=[]]
    actions=[i for i in player.moves if i!=[]]
    done=False
    for i in range(len(states)-1):
        if len(states[i])==0:
            break
        elif len(states[i+1])==0:
            done=True
            
        probs=actor(torch.tensor(states[i], dtype=torch.float32))
        value = critic(torch.tensor(states[i], dtype=torch.float32))
        if not done:
            next_value = critic(torch.tensor(states[i+1], dtype=torch.float32))
        else:
            if player.n_won_battles>n_win:
                values[i]=win
            else:
                values[i]=-win
            next_value = critic(torch.tensor([-1 for i in range(91)], dtype=torch.float32))
        
        td_target = values[i] + 0.5 * next_value*(1-done)
        advantage = td_target - value
        
        critic_loss = F.mse_loss(value, td_target.detach())
        optimizer_critic.zero_grad()
        critic_loss.backward()
        optimizer_critic.step()
        actions_tensor = torch.tensor(actions[i], dtype=torch.long)
        prob=torch.gather(probs,0, actions_tensor)
        log_prob = torch.log(prob + 1e-8).squeeze()
        actor_loss=(-log_prob * advantage.detach()).sum()
        optimizer_actor.zero_grad()
        actor_loss.backward()
        optimizer_actor.step()
        act_l.append(actor_loss.item())
        cri_l.append(critic_loss.item())
    player.set_actor(actor=actor)
    return sum(act_l)/len(states)-1, sum(cri_l)/len(states)-1

async def cleanup():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
       

async def self_train():
    actor = Actor(91, 76)
    actor.load_state_dict(torch.load("team_mix\A2C_train_100.pth"))
    critic = Critic(91)
    optimizer_critic = torch.optim.Adam(critic.parameters(), lr=1e-4)
    optimizer_actor = torch.optim.Adam(actor.parameters(), lr=1e-4)
    RLplayer1 = RLPlayer(battle_format="gen9vgc2025regg", team=RandomTeamFromPool(teams), accept_open_team_sheet=True, account_configuration=AccountConfiguration("FraIA", "Password"), actor=actor)
    RLplayer2 = RLPlayer(battle_format="gen9vgc2025regg", team=RandomTeamFromPool(teams), accept_open_team_sheet=True, actor=actor)
    teams_win_rate={}
    turns=0
    n_switch=0
    value_W=0
    value_L=0
    a_loss_W=[]
    a_loss_L=[]
    c_loss_W=[]
    c_loss_L=[]
    # Loop di allenamento RL
    for episode in range(100,2000):          
        await RLplayer1.battle_against(RLplayer2)
        turns+=RLplayer1.turn
        n_switch+=RLplayer1.n_switch
        n_switch+=RLplayer2.n_switch
        win=abs(100-0.8*RLplayer1.turn)
        print("Episode: "+str(episode))
        act1, cri1=update_weight(actor, critic, RLplayer1, optimizer_critic, optimizer_actor, win)
        act2, cri2=update_weight(actor, critic, RLplayer2, optimizer_critic, optimizer_actor, win)
        
        if RLplayer1.n_won_battles==1:
            team=str([pk.name for pk in RLplayer1.team.keys()]).replace("', '",", ").strip("[]'")
            value_W+=(sum(RLplayer1.values)+win)
            value_L+=(sum(RLplayer2.values)-win)
            a_loss_W.append(act1)
            a_loss_L.append(act2)
            c_loss_W.append(cri1)
            c_loss_L.append(cri2)

        else:
            team=str([pk.name for pk in RLplayer2.team.keys()]).replace("', '",", ").strip("[]'")
            value_W+=(sum(RLplayer2.values)+win)
            value_L+=(sum(RLplayer1.values)-win)
            a_loss_W.append(act2)
            a_loss_L.append(act1)
            c_loss_W.append(cri2)
            c_loss_L.append(cri1)
        value=value_W+value_L
        
        if team in teams_win_rate.keys():
            teams_win_rate[team]+=1
        else:
            teams_win_rate[team]=1
        
        print(teams_win_rate.values())
        RLplayer1.reset()
        RLplayer1.reset_battles()
        RLplayer2.reset()
        RLplayer2.reset_battles()
        await cleanup()
        if (episode+1)%50==0:
            m_turn=turns/50
            turns=0
            m_switch=n_switch/100
            n_switch=0
            m_value=value/100
            m_value_W=value_W/100
            m_value_L=value_L/100
            value_W=0
            value_L=0
            value=0
            a_l=sum(a_loss_L)/50
            a_w=sum(a_loss_W)/50
            c_l=sum(c_loss_L)/50
            c_w=sum(c_loss_W)/50
            a_loss_L=[]
            a_loss_W=[]
            c_loss_L=[]
            c_loss_W=[]
            with open('train_all_team/episode_'+str(episode+1)+'.txt', 'w', encoding='UTF8') as f:
                f.write(f"Means n° turn per match: {m_turn}\n")
                f.write(f"Means n° switch per match: {m_switch}\n")
                f.write(f"Means n° reward per win match: {m_value_W}\n")
                f.write(f"Means n° reward per lose match: {m_value_L}\n")
                f.write(f"Means n° reward per match: {m_value}\n\n")
                f.write("Teams win rate:\n")
                for t in teams_win_rate.keys():
                    f.write(t+": "+str(teams_win_rate[t]/50)+"\n")
                    teams_win_rate[t]=0
                f.write(f"Actor loss win match: {a_w}\n")
                f.write(f"Actor loss lose match: {a_l}\n")
                f.write(f"Critic loss win match: {c_w}\n")
                f.write(f"Critic loss lose match: {c_l}")
            torch.save(actor.state_dict(), f"team_mix/A2C_train_{episode+1}.pth")
    torch.save(actor.state_dict(), "A2C_train_mix_teams.pth")
    
    
async def train():
    actor = Actor(91, 76)
    actor.load_state_dict(torch.load("team_mix\A2C_train_600_VS_umans.pth"))
    critic = Critic(91)
    optimizer_critic = torch.optim.Adam(critic.parameters(), lr=1e-4)
    optimizer_actor = torch.optim.Adam(actor.parameters(), lr=1e-4)
    RLplayer1 = RLPlayer(battle_format="gen9vgc2025regg", team=RandomTeamFromPool(teams2), accept_open_team_sheet=True, account_configuration=AccountConfiguration("CynthIA_DL", "Password"), actor=actor, server_configuration=ShowdownServerConfiguration)
    teams_win_rate={}
    turns=0
    n_switch=0
    value_W=0
    value_L=0
    a_loss_W=[]
    a_loss_L=[]
    c_loss_W=[]
    c_loss_L=[]
    n_win=0
    for episode in range(1000):
        await RLplayer1.ladder(1)
        turns+=RLplayer1.turn
        n_switch+=RLplayer1.n_switch
        win=abs(100-0.8*RLplayer1.turn)
        print("Episode: "+str(episode))
        act1, cri1=update_weight(actor, critic, RLplayer1, optimizer_critic, optimizer_actor, win, n_win)
        
        if RLplayer1.n_won_battles>n_win:
            n_win=RLplayer1.n_won_battles
            team=str([pk.name for pk in RLplayer1.team.keys()]).replace("', '",", ").strip("[]'")
            value_W+=(sum(RLplayer1.values)+win)
            a_loss_W.append(act1)
            c_loss_W.append(cri1)
            if team in teams_win_rate.keys():
                teams_win_rate[team]+=1
            else:
                teams_win_rate[team]=1
            print(teams_win_rate.values())
        else:
            value_L+=(sum(RLplayer1.values)-win)
            a_loss_L.append(act1)
            c_loss_L.append(cri1)
        value=value_W+value_L
            
        RLplayer1.reset()
        await cleanup()
        if (episode+1)%100==0:
            m_turn=turns/100
            turns=0
            m_switch=n_switch/100
            n_switch=0
            m_value=value/100
            m_value_W=value_W/100
            m_value_L=value_L/100
            value_W=0
            value_L=0
            value=0
            win_rate_d=sum(teams_win_rate.values())/100
            RLplayer1.reset_battles()
            await RLplayer1.ladder(20)
            win_rate_a=RLplayer1.n_won_battles/20
            
            n_win=0
            a_l=sum(a_loss_L)/100
            a_w=sum(a_loss_W)/100
            c_l=sum(c_loss_L)/100
            c_w=sum(c_loss_W)/100
            a_loss_L=[]
            a_loss_W=[]
            c_loss_L=[]
            c_loss_W=[]
            with open('train_all_team_VS_umans/episode_'+str(episode+1)+'.txt', 'w', encoding='UTF8') as f:
                f.write(f"Means n° turn per match: {m_turn}\n")
                f.write(f"Means n° switch per match: {m_switch}\n")
                f.write(f"Means n° reward per win match: {m_value_W}\n")
                f.write(f"Means n° reward per lose match: {m_value_L}\n")
                f.write(f"Means n° reward per match: {m_value}\n")
                f.write(f"Win rate during {episode+1} episode: {win_rate_d}\n")
                f.write(f"Win rate after {episode+1} episode: {win_rate_a}\n")
                f.write("Teams win rate:\n")
                for t in teams_win_rate.keys():
                    f.write(t+": "+str(teams_win_rate[t]/100)+"\n")
                    teams_win_rate[t]=0
                f.write(f"Actor loss win match: {a_w}\n")
                f.write(f"Actor loss lose match: {a_l}\n")
                f.write(f"Critic loss win match: {c_w}\n")
                f.write(f"Critic loss lose match: {c_l}\n")
                f.write(f"Agent elo: {list(RLplayer1.battles.values())[-1].rating}")
            RLplayer1.reset_battles()
            torch.save(actor.state_dict(), f"team_mix/A2C_train_{episode+1}_VS_umans.pth")
    torch.save(actor.state_dict(), "A2C_train_mix_teams_VS_umans.pth")
    
    
#asyncio.run(self_train())

asyncio.run(train())