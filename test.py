import asyncio
import torch
from actor import RLPlayer, RandomTeamFromPool
from teams import teams3
from poke_env import AccountConfiguration, ShowdownServerConfiguration
from A2C import Actor, Critic

async def test():
    actor = Actor(91, 76)
    actor.load_state_dict(torch.load("A2C_train_mix_teams_VS_umans.pth"))
    RLplayer1 = RLPlayer(battle_format="gen9vgc2025regg", team=RandomTeamFromPool(teams3), accept_open_team_sheet=True, account_configuration=AccountConfiguration("CynthIA_DL", "Password"), actor=actor, server_configuration=ShowdownServerConfiguration)
    turns=0
    n_switch=0
    for episode in range(10, 110, 10):
        await RLplayer1.ladder(10)
        turns+=RLplayer1.turn
        n_switch+=RLplayer1.n_switch
        print("Episode: "+str(episode))
        m_turn=turns/(episode)
        m_switch=n_switch/(episode)
        with open('test_VS_umans/episode_'+str(episode)+'.txt', 'w', encoding='UTF8') as f:
            f.write(f"Means n° turn per match: {m_turn}\n")
            f.write(f"Means n° switch per match: {m_switch}\n")
            f.write(f"Win rate: {RLplayer1.win_rate}\n")
            f.write(f"Agent elo: {list(RLplayer1.battles.values())[-1].rating}")
        RLplayer1.reset_battles()  
    
asyncio.run(test())