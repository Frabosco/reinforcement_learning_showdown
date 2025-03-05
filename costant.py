from bs4 import BeautifulSoup
from poke_env.data.gen_data import GenData
from poke_env.environment import field, weather, side_condition, pokemon_type, status, effect

with open('ssss.html', 'r', encoding='utf-8') as file:
    html_cont2 = file.read()
    
# Parse the HTML content


soup2 = BeautifulSoup(html_cont2, 'html.parser')
nitem=0
items={}
item= soup2.find_all('span')
for i in item:
    i=i.get_text().lower().replace(" ","")
    if i not in items.keys():
        items[i]=nitem
        nitem+=1
items["nevermeltice"]=nitem
nitem+=1
data=GenData.from_format("gen9vgc2024regg")

ITEM=items
FIELD=field.Field
WEATHER=weather.Weather
CONDICTION=side_condition.SideCondition
TYPE=pokemon_type.PokemonType
#STS={"atk":1,"def":2,"spa":3,"spd":4,"spe":5,"accuracy":6,"evasion":7}
STS=["atk","def","spa","spd","spe","accuracy","evasion"]
POKEDEX=data.load_pokedex(gen=9)
MOVES=data.load_moves(gen=9)
STATUS=status.Status
EFFECT=effect.Effect

NPKM=len(POKEDEX)
NS=len(STATUS)
NMV=len(MOVES.keys())
NF=len(FIELD)
NW=len(WEATHER)
NC=len(CONDICTION)
NT=len(TYPE)
NI=nitem


ACTION=["11a","12a","13a","14a","21a","22a","23a","24a","31a","32a","33a","34a","41a","42a","43a","44a",
        "11at","12at","13at","14at","21at","22at","23at","24at","31at","32at","33at","34at","41at","42at","43at","44at",
        "11b","12b","13b","14b","21b","22b","23b","24b","31b","32b","33b","34b","41b","42b","43b","44b",
        "11bt","12bt","13bt","14bt","21bt","22bt","23bt","24bt","31bt","32bt","33bt","34bt","41bt","42bt","43bt","44bt",
        "1s1","1s2","1s3","1s4","1s5","1s6","2s1","2s2","2s3","2s4","2s5","2s6"]
NA=len(ACTION)