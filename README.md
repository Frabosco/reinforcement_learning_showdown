# Reinforcement Learning Showdown

A reinforcement learning agent that learns to play competitive Pokémon VGC (Video Game Championship) double battles on [Pokémon Showdown](https://pokemonshowdown.com/) using the **Advantage Actor-Critic (A2C)** algorithm.

## Overview

This project trains an AI agent to compete in **Gen 9 VGC 2025 Reg G** double battles. The training pipeline combines **supervised pretraining** on expert replays with **reinforcement learning** through both self-play and ladder matches against human players.

The agent connects to Pokémon Showdown via the [`poke-env`](https://github.com/hsahovic/poke-env) library and learns to make strategic decisions including move selection, target selection, Pokémon switching, and Terastallization.

## Project Structure

| File | Description |
|---|---|
| `A2C.py` | Actor-Critic neural network architecture definitions |
| `actor.py` | `RLPlayer` class — core battle agent with state encoding and action selection |
| `training.py` | Training loops for self-play and ladder training with A2C weight updates |
| `test.py` | Evaluation script — tests the trained agent on the Pokémon Showdown ladder |
| `pretrain.py` | Supervised pretraining from expert replay data using KL divergence loss |
| `pretrainMatch.py` | Data collection — downloads and parses Pokémon Showdown replays into training data |
| `costant.py` | Constants and encodings (Pokédex, moves, items, types, actions) |
| `teams.py` | Predefined competitive Pokémon team configurations |
| `graph.py` | Visualization of training metrics (rewards, losses, win rates, ELO) |

## Architecture

### Neural Networks

- **Actor Network**: Fully connected network (`91 → 512 → 256 → 128 → 76`) with ReLU activations and softmax output. Outputs action probabilities over 76 possible actions.
- **Critic Network**: Fully connected network (`91 → 256 → 64 → 1`) with ReLU activations. Outputs a scalar state value estimate.

### State Representation

The state is a **91-dimensional** vector encoding:
- Active Pokémon stats for both players (species, types, HP, moves, item, status effects, tera type, stat boosts)
- Bench Pokémon info (species, HP, types)
- Field conditions (weather, terrain, side conditions)

### Action Space

**76 actions** covering:
- 4 moves × 4 targets × 2 active Pokémon = 32 move actions per side
- Switch actions for each bench Pokémon slot
- Terastallization variants of move actions

### Reward Function

A heuristic reward based on the battle state, incorporating:
- HP fractions of all Pokémon (own and opponent's)
- Status conditions
- Stat boosts and drops
- Number of fainted Pokémon
- Turn count penalty
- Win/loss bonus scaled by battle length

## Dependencies

- [PyTorch](https://pytorch.org/) — deep learning framework
- [poke-env](https://github.com/hsahovic/poke-env) — Pokémon Showdown API wrapper
- [NumPy](https://numpy.org/) — numerical operations
- [Matplotlib](https://matplotlib.org/) — training visualization
- [Pandas](https://pandas.pydata.org/) — data processing
- [BeautifulSoup / Requests](https://docs.python-requests.org/) — replay data collection

## Usage

### 1. Data Collection

Download and parse expert replays from Pokémon Showdown to create supervised training data:

```bash
python pretrainMatch.py
```

This generates CSV files (`turn_a.csv`, `turn_b.csv`, `moves.csv`) with encoded battle states and actions.

### 2. Supervised Pretraining

Pretrain the actor network on expert replay data:

```bash
python pretrain.py
```

Trains using KL divergence loss and saves the pretrained model to `actor_pretrained2.pth`.

### 3. Self-Play Training

Train the agent through self-play battles (requires a local Pokémon Showdown server):

```python
# In training.py, uncomment:
asyncio.run(self_train())
```

```bash
python training.py
```

### 4. Ladder Training

Train against human players on the Pokémon Showdown ladder:

```python
# In training.py, use:
asyncio.run(train())
```

```bash
python training.py
```

### 5. Testing

Evaluate the trained agent on the Pokémon Showdown ladder:

```bash
python test.py
```

### 6. Visualize Results

Plot training metrics (rewards, losses, win rates, ELO):

```bash
python graph.py
```

## Training Pipeline

```
Replay Data Collection ──► Supervised Pretraining ──► Self-Play Training ──► Ladder Training ──► Evaluation
   (pretrainMatch.py)         (pretrain.py)           (training.py)        (training.py)       (test.py)
```

1. **Data Collection**: Expert replays are scraped from Pokémon Showdown and parsed into state-action pairs
2. **Supervised Pretraining**: The actor network learns from expert demonstrations using KL divergence
3. **Self-Play Training**: Two instances of the agent battle each other, with A2C updates using TD learning and advantage estimation
4. **Ladder Training**: The agent plays on the public Pokémon Showdown ladder against human players, continuing to learn via A2C
5. **Evaluation**: The trained agent is tested on the ladder, tracking win rate and ELO rating
