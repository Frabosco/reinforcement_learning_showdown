from poke_env.player.player import Player, ServerConfiguration
from poke_env.player.env_player import Gen4EnvSinglePlayer
from poke_env.teambuilder import Teambuilder
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.effect import Effect
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.double_battle import DoubleBattle
from poke_env.environment.target import Target
from poke_env.player.battle_order import DoubleBattleOrder, BattleOrder
from costant import ITEM, MOVES, POKEDEX, STS, NC,NF,NI,NMV,NPKM,NS,NT,NW, ACTION, TYPE
import time
import torch
from A2C import Actor, Critic
import numpy as np

class RLPlayer(Player):
    
    def __init__(self, account_configuration = None, *, avatar = None, battle_format = "gen9randombattle", log_level = None, max_concurrent_battles = 1, accept_open_team_sheet = False, save_replays = False, server_configuration = None, start_timer_on_battle_start = False, start_listening = True, ping_interval = 20, ping_timeout = 20, team = None, actor=None):
        super().__init__(account_configuration, avatar=avatar, battle_format=battle_format, log_level=log_level, max_concurrent_battles=max_concurrent_battles, accept_open_team_sheet=accept_open_team_sheet, save_replays=save_replays, server_configuration=server_configuration, start_timer_on_battle_start=start_timer_on_battle_start, start_listening=start_listening, ping_interval=ping_interval, ping_timeout=ping_timeout, team=team)
        self.actor=actor
        self.states=[[]]
        self.moves=[[]]
        self.values=[0]
        self.probs=[[]]
        self.team={}
        self.turn=0
        self.n_switch=0
    
    def reset(self):
        self.states=[[]]
        self.moves=[[]]
        self.values=[0]
        self.probs=[[]]
        self.team={}
        self.turn=0
        self.n_switch=0
    
    def teampreview(self, battle: DoubleBattle)->str:
        state= [0 for i in range(91)]
        c=0
        self.team={p:{m:m.current_pp for m in p.moves.values()} for p in battle.team.values()}
        for pokemon in battle.team:
            pk=POKEDEX[pokemon.lower().split(": ")[1].replace(" ","").replace("-","").strip("*")]
            state[c]=pk["num"]/NPKM
            state[c+1]=getattr(TYPE, pk["types"][0].upper()).value/NT
            state[c+2]=getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1
            c+=7
        for pokemon in battle.opponent_team:
            pk==POKEDEX[pokemon.lower().replace(" ","").replace("-","").strip("*")]
            state[c]=pk["num"]/NPKM
            state[c+1]=getattr(TYPE, pk["types"][0].upper()).value/NT
            state[c+2]=getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1
            c+=7
        
        self.states[battle.turn]=state
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_probs = self.actor(state_tensor)
        self.probs[battle.turn]=action_probs
        action_probs=action_probs.detach().numpy()[0].tolist()
        actions=ACTION
        action_probs=action_probs[64:]
        sorted_probs=sorted(action_probs, reverse=True)
        actions=actions[64:]
        order=[0 for i in range(2)]
        for p in sorted_probs:
            ind=action_probs.index(p)
            action=actions[ind]
            pos=int(action[0])-1
            slot=int(action[2])
            if order[pos]==0 and slot not in order:
                order[pos]=slot
                self.moves[battle.turn].append(ACTION.index(action))
            elif slot not in order:
                order.append(slot)
                self.moves[battle.turn].append(ACTION.index(action))
            if len(order)==4 and 0 not in order:
                break
            elif len(order)>4:
                order.pop()
            action_probs.pop(ind)
            actions.pop(ind)
        s=""
        for m in order:
            s+=str(m)
        return "/team "+s
    
    def action_to_move(self, action, battle):
        return super().action_to_move(action, battle)

    def embed_battle(self, battle):
        state = []
        
        for pokemon in battle.active_pokemon:
            if pokemon:
                pk=POKEDEX[pokemon.base_species]
                state.append(pk["num"]/NPKM)
                state.append(getattr(TYPE, pk["types"][0].upper()).value/NT)
                state.append(getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1)
                state.append(pokemon.current_hp_fraction)
                for i in range(4-len(pokemon.moves)):
                    state.append(-1)
                for move in pokemon.moves:
                    state.append(MOVES[move]["num"]/NMV)
                if pokemon.item!="unknown_item" and pokemon.item!=None:
                    state.append(ITEM[pokemon.item]/NI)
                else:
                    state.append(-1)
                if pokemon.effects:
                    state.append(list(pokemon.effects.keys())[0].value/NS)
                else:
                    state.append(-1)
                if pokemon.tera_type!=None:
                    state.append(pokemon.tera_type.value/NT)
                else:
                    state.append(-1)
                for stat in pokemon.boosts.keys():
                    state.append(pokemon.boosts[stat]/6)
            else:
                for i in range(18):
                    state.append(-1)

        k1=0
        for i1 in range(len(battle.available_switches[0])):
            pokemon=battle.available_switches[0][i1]
            pk=POKEDEX[pokemon.base_species]
            state.append(pk["num"]/NPKM)
            state.append(pokemon.current_hp_fraction)
            state.append(getattr(TYPE, pk["types"][0].upper()).value/NT)
            state.append(getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1)
            k1+=1
        for j in range(k1,2):
            state.append(-1)
            state.append(-1)
            state.append(-1)
            state.append(-1)

        for pokemon in battle.opponent_active_pokemon:
            if pokemon:
                pk=POKEDEX[pokemon.base_species]
                state.append(pk["num"]/NPKM)
                state.append(getattr(TYPE, pk["types"][0].upper()).value/NT)
                state.append(getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1)
                state.append(pokemon.current_hp_fraction)
                for i in range(4-len(pokemon.moves)):
                    state.append(-1)
                for move in pokemon.moves:
                    state.append(MOVES[move]["num"]/NMV)
                if pokemon.item!="unknown_item" and pokemon.item!=None:
                    state.append(ITEM[pokemon.item]/NI)
                else:
                    state.append(-1)
                if pokemon.effects:
                    state.append(list(pokemon.effects.keys())[0].value/NS)
                else:
                    state.append(-1)
                if pokemon.tera_type!=None:
                    state.append(pokemon.tera_type.value/NT)
                else:
                    state.append(-1)
                for stat in pokemon.boosts.keys():
                    state.append(pokemon.boosts[stat]/6)
            else:
                for i in range(18):
                    state.append(-1)

        k2=0
        for i2 in range(len(battle.available_switches[1])):
            pokemon=battle.available_switches[1][i2]
            pk=POKEDEX[pokemon.base_species]
            state.append(pk["num"]/NPKM)
            state.append(pokemon.current_hp_fraction)
            state.append(getattr(TYPE, pk["types"][0].upper()).value/NT)
            state.append(getattr(TYPE, pk["types"][1].upper()).value/NT if len(pk["types"])>1 else -1)
            k2+=1
        for j in range(k2,2):
            state.append(-1)
            state.append(-1)
            state.append(-1)
            state.append(-1)
        
        if battle.weather:
            state.append(list(battle.weather.keys())[0].value/NW)
        else:
            state.append(-1)
            
        if battle.fields:
            state.append(list(battle.fields.keys())[0].value/NF)
        else:
            state.append(-1)

        if battle.side_conditions:
            state.append(list(battle.side_conditions.keys())[0].value/NC)
        else:
            state.append(-1)
        
        return state

    def move(self, pokemon, battle, probs, actions, ind, tera):
        t=-1
        if pokemon:
            if len(battle.available_moves[ind])==1:
                o=battle.available_moves[ind][0]
                moves=list(pokemon.moves.values())
                for m in range(4):
                    if moves[m]==0:
                        break
                if battle.can_tera[ind]:
                    probs=probs[m*4:4+m*4]+probs[16+m*4:20+m*4]
                    actions=actions[m*4:4+m*4]+actions[16+m*4:20+m*4]
                else:
                    probs=probs[m*4:4+m*4]
                    actions=actions[m*4:4+m*4]
                action=actions[probs.index(max(probs))]
                self.moves[battle.turn].append(ACTION.index(action))
                t=int(action[1])
                if t>2:
                    t-=2
                    if t!=ind+1:
                        t=-t
                if o.deduced_target==Target.SELF or o.deduced_target==Target.ALLIES or o.deduced_target==Target.ALLY_SIDE or o.deduced_target==Target.ALLY_TEAM or o.deduced_target==Target.FOE_SIDE or o.deduced_target==Target.ALL or o.deduced_target==Target.RANDOM_NORMAL or o.deduced_target==Target.ALL_ADJACENT or o.deduced_target==Target.ALL_ADJACENT_FOES:
                    t=0
                return o, t, tera
            elif pokemon.must_recharge or pokemon.preparing in pokemon.effects:
                order1=self.choose_random_move(battle).message.split(" ")
                o=MOVES[order1[2]]
                t=int(order1[3])
                return o, t, tera
            elif True in battle.trapped or len(battle.available_switches[0])==0:
                probs=probs[:32]
                actions=actions[:32]
            elif len(battle.available_switches[0])==1:
                probs=probs[:32]
                actions=actions[:32]
            if not battle.can_tera[ind]:
                probs=probs[:16]+probs[32:]
                actions=actions[:16]+actions[32:]
            sorted_probs=sorted(probs, reverse=True)
            p=max(probs)
            action=actions[probs.index(p)]
            m=int(action[0])-1
            o=list(pokemon.moves.values())[m]
            if o not in battle.available_moves[ind]:
                for p in sorted_probs:
                    action=actions[probs.index(p)]
                    o=list(pokemon.moves.values())[int(action[0])-1]
                    if "s" in action or o in battle.available_moves[ind]:
                        break
            if self.team[pokemon][o]==0:
                for p in sorted_probs:
                    action=actions[probs.index(p)]
                    o=list(pokemon.moves.values())[int(action[0])-1]
                    if "s" in action or (int(action[0])-1!=m and self.team[pokemon][o]!=0):
                        break
                    else:
                        probs.pop(actions.index(action))
                        actions.pop(actions.index(action))
            if Effect.TAUNT in pokemon.effects.keys() and o.category==MoveCategory.STATUS:
                for p in sorted_probs:
                    action=actions[probs.index(p)]
                    o=list(pokemon.moves.values())[int(action[0])-1]
                    if "s" in action or o.category!=MoveCategory.STATUS:
                        break
                    else:
                        probs.pop(actions.index(action))
                        actions.pop(actions.index(action))
            self.moves[battle.turn].append(ACTION.index(action))
            if "s" in action:
                if int(action[2])-1<=len(battle.available_switches[0]):
                    o=battle.available_switches[0][int(action[2])-1]
                    t=0
                    self.n_switch+=1
                    return o,t, tera
            else:   
                if "t" in action:
                    tera=True
                o=list(pokemon.moves.values())[int(action[0])-1]
                t=int(action[1])
                if t>2:
                    t-=2
                    if t!=ind+1:
                        t=-t
                if o.deduced_target==Target.SELF or o.deduced_target==Target.ALLIES or o.deduced_target==Target.ALLY_SIDE or o.deduced_target==Target.ALLY_TEAM or o.deduced_target==Target.FOE_SIDE or o.deduced_target==Target.ALL or o.deduced_target==Target.RANDOM_NORMAL or o.deduced_target==Target.ALL_ADJACENT or o.deduced_target==Target.ALL_ADJACENT_FOES:
                    t=0
                return o,t, tera
            
    def set_actor(self, actor):
        self.actor=actor
        
    def extract_features(self, battle):
        return self.embed_battle(battle)
    
    def calcValue(self, battle: DoubleBattle):
        value=0
        for pokemon in battle.active_pokemon:
            if pokemon is not None:
                value-=(1-pokemon.current_hp_fraction)*1.5
                if pokemon.status is not None:
                    value-=0.5
                for sts in list(pokemon.boosts.keys()):
                    boost=pokemon.boosts[sts]
                    if boost>=0:
                        value+=0.15*boost
                    else:
                        value-=0.15*boost
            else:
                value-=2
        
        for pokemon in battle.available_switches[0]:
            value-=(1-pokemon.current_hp_fraction)*1.5
            if pokemon.status is not None:
                value-=0.5
                
        for i in range(2-len(battle.available_switches[0])):
            value-=2
        
        for pokemon in battle.opponent_active_pokemon:
            if pokemon is not None:
                value+=(1-pokemon.current_hp_fraction)*1.75
                if pokemon.status is not None:
                    value+=0.75
                for sts in list(pokemon.boosts.keys()):
                    boost=pokemon.boosts[sts]
                    if boost>=0:
                        value-=0.20*boost
                    else:
                        value+=0.20*boost
            else:
                value+=2

        for pokemon in battle.available_switches[1]:
            value+=(1-pokemon.current_hp_fraction)*1.75
            if pokemon.status is not None:
                value+=0.75
                
        for i in range(2-len(battle.available_switches[1])):
            value+=2
        
        value-=0.001*battle.turn
        return value

    def choose_move(self, battle: DoubleBattle):
        time.sleep(0.1)
        
        self.moves.append([])
        self.states.append([])
        self.probs.append([])
        if len(self.values)<=battle.turn:
            self.values.append(0)
        self.turn=battle.turn
        state = self.extract_features(battle)
        self.states[battle.turn]=state
        self.values[battle.turn]=self.calcValue(battle)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_probs = self.actor(state_tensor)
        self.probs[battle.turn]=action_probs
        action_probs=action_probs.detach().numpy()[0].tolist()
        actions=ACTION
        action_probs_a=action_probs[:32]+action_probs[64:66]
        actions_a=actions[:32]+actions[64:66]
        action_probs_b=action_probs[32:64]+action_probs[70:72]
        actions_b=actions[32:64]+actions[70:72]
        
        pokemon_a, pokemon_b=battle.active_pokemon
        
        if True in battle.force_switch and len(battle.available_switches[0])>0:
            if battle.force_switch[0] and battle.force_switch[1]:
                if len(battle.available_switches[0])==1:
                    o=battle.available_switches[0][0]
                    order=BattleOrder(order=o, move_target=1, mega=False, dynamax=False, z_move=False)
                    return DoubleBattleOrder(order,None) 
                o1=battle.available_switches[0][0]
                order1=BattleOrder(order=o1, move_target=1, mega=False, dynamax=False, z_move=False)
                o2=battle.available_switches[0][1]
                order2=BattleOrder(order=o2, move_target=2, mega=False, dynamax=False, z_move=False)
                return DoubleBattleOrder(order1,order2)
            elif pokemon_a in battle.active_pokemon:
                act=actions_b[32:34]
                probs=action_probs_b[32:34]
            else:
                act=actions_a[32:34]
                probs=action_probs_a[32:34]
            if len(battle.available_switches[0])==1:
                o=battle.available_switches[0][0]
                return BattleOrder(order=o, mega=False, dynamax=False, z_move=False)
            else:
                action=act[probs.index(max(probs))]
                o=battle.available_switches[0][int(action[2])-1]
                return BattleOrder(order=o, mega=False, dynamax=False, z_move=False)    
        else:
            o1=None
            o2=None
            order1=None
            order2=None
            t1=0
            t2=0
            tera1=False
            tera2=False
            if pokemon_a and not Effect.COMMANDER in pokemon_a.effects.keys():
                o1, t1, tera1=self.move(pokemon_a, battle, action_probs_a, actions_a, 0, False)
            if pokemon_b and not Effect.COMMANDER in pokemon_b.effects.keys():
                if isinstance(o1, Pokemon):
                    ind=battle.available_switches[0].index(o1)+32
                    action_probs_b.pop(ind)
                    actions_b.pop(ind)
                o2, t2, tera2=self.move(pokemon_b, battle, action_probs_b, actions_b, 1, False)
                
            if tera1 and tera2:
                tera2=False
            
            if t1!=0:
                if o1.deduced_target==Target.ADJACENT_ALLY:
                    t1=-2
                order1=BattleOrder(order=o1, move_target=t1, mega=False, dynamax=False, z_move=False, terastallize=tera1)
            elif o1 is not None:
                order1=BattleOrder(order=o1, mega=False, dynamax=False, z_move=False, terastallize=tera1)
                
            if t2!=0:
                if o2.deduced_target==Target.ADJACENT_ALLY:
                    t2=-1
                order2=BattleOrder(order=o2, move_target=t2, mega=False, dynamax=False, z_move=False, terastallize=tera2)
            elif o2 is not None:
                order2=BattleOrder(order=o2, mega=False, dynamax=False, z_move=False, terastallize=tera2)
            
            if order1 is not None and isinstance(order1.order, Move) and order1.order.id!="struggle":
                    self.team[pokemon_a][order1.order]-=1
                    if order1.order.id=="terastarstorm" and pokemon_a.is_terastallized:
                        order1=BattleOrder(order=o1, mega=False, dynamax=False, z_move=False, terastallize=tera1)  
            if order2 is not None and isinstance(order2.order, Move) and order2.order.id!="struggle":
                    self.team[pokemon_b][order2.order]-=1
                    if order2.order.id=="terastarstorm" and pokemon_b.is_terastallized:
                        order2=BattleOrder(order=o2, mega=False, dynamax=False, z_move=False, terastallize=tera2)   
            return DoubleBattleOrder(order1, order2)
        
        
class RandomTeamFromPool(Teambuilder):
    def __init__(self, teams):
        self.packed_teams = []

        for team in teams:
            parsed_team = self.parse_showdown_team(team)
            packed_team = self.join_team(parsed_team)
            self.packed_teams.append(packed_team)

    def yield_team(self):
        return np.random.choice(self.packed_teams)
