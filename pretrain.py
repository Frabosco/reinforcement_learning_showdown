import torch
import csv
import torch
from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
from A2C import Actor
from torch.utils.data import DataLoader, random_split
from costant import ACTION, NA


with open("moves.csv", mode="r")as file:
    moves=csv.reader(file)
    moves=[m for m in moves]

with open("turn_a.csv", mode ='r')as file:
    turn_a=csv.reader(file)
    turn_a=[a for a in turn_a]

with open("turn_b.csv", mode ='r')as file:
    turn_b=csv.reader(file)
    turn_b=[a for a in turn_b]


sts=[]
act=[]
for i in range(1,len(turn_a)):
    mv=moves[i]
    if mv!=["['', '']", "['', '']"]:
        m1=[x.strip("'[]") for x in mv[0].split(", ")]
        a1=[]
        for j in range(len(m1)):
            if m1[j]!="":
                a1.append(ACTION.index(m1[j]))
        if(len(a1)>0):
            k1=1/len(a1)
            m1=[0 for i in range(NA)]
            for a in a1:
                m1[a]=k1
            sts.append([float(v)for v in turn_a[i]])
            act.append(m1)        
        m2=[x.strip("'[]") for x in mv[1].split(", ")]
        a2=[]
        for j in range(len(m2)):
            if m2[j]!="":
                a2.append(ACTION.index(m2[j]))
        if len(a2)>0:
            k2=1/len(a2)
            m2=[0 for i in range(NA)]
            for a in a2:
                m2[a]=k2
            sts.append([float(v)for v in turn_b[i]])
            act.append(m2)

error=[]
for i in range(len(sts)):
    if len(sts[i])!=91:
        error.append(i)
error.reverse()
for e in error:
    sts.pop(e)
    act.pop(e)   

actor = Actor(91, len(ACTION))
# Dati di esempio (da sostituire con i tuoi dati reali)
states = torch.tensor(sts)
actions = torch.tensor(act)


# Creare un DataLoader
dataset = TensorDataset(states, actions)

# Dimensione del dataset
dataset_size = len(dataset)
train_size = int(0.8 * dataset_size)
test_size = dataset_size - train_size

# Divisione
train_set, test_set = random_split(dataset, [train_size, test_size])

# Ottimizzatore per l'Actor
optimizer_actor = torch.optim.Adam(actor.parameters(), lr=1e-4)
loss_fn = nn.KLDivLoss(reduction="batchmean")
train_loader = DataLoader(train_set, batch_size=256, shuffle=True)
test_loader = DataLoader(test_set, batch_size=256, shuffle=False)

# Pretraining
nEpoch=int(train_size/256)

losses=[]
print(train_size,nEpoch)
for epoch in range(nEpoch):  # Numero di epoche
    for state_batch, action_distributions in train_loader:
        logits = actor(state_batch)
        log_probs = torch.log(logits+1e-8)
        loss = loss_fn(log_probs, action_distributions)
        
        optimizer_actor.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(actor.parameters(), max_norm=2.0)
        optimizer_actor.step()
    print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")
    losses.append(loss.item())
    
correct = 0
total = 0

# Disabilita il gradiente durante il test
torch.save(actor.state_dict(), "actor_pretrained2.pth")
actor.eval()
with torch.no_grad():
    for inputs, labels in test_loader:
        outputs = actor(inputs)
        predictions = torch.argmax(outputs, dim=0) # Azione predetta
        correct += (predictions == labels).sum().item()

accuracy = correct / train_size
print(f"Accuracy: {accuracy * 100:.2f}%")

with open('pretrain.txt', 'w', encoding='UTF8') as f:
    for loss in losses:
        f.write(f"Epoch {epoch + 1}, Loss: {loss}\n")
    f.write(f"Accuracy: {accuracy * 100:.2f}%")