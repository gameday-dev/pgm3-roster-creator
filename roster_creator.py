import requests
from bs4 import BeautifulSoup
import random
import csv
import json
from tqdm import tqdm

class Player:
    def __init__(self, firstName="", lastName="", default_rating=-1) -> None:
        
        # player attributes
        self.forename = firstName
        self.surname = lastName
        self.age = default_rating 
        self.iden = "5A251D07-3C9D-4BD1-B511-FD20CA81227C" #str(random.randint(1, 1000000))
        self.position = default_rating 
        self.appearance	= generateRandomAppearance() # PGM specific
        self.draftNum = random.randint(1, 224) # TODO: PGM specific
        self.teamID = "" 
        # self.teamNum = 10 # TEST
        self.draftSeason = random.randint(2012, 2020) # random generated as backup if we can't find the real year

        # overall ratings
        self.rating	= default_rating 
        self.potential = random.randint(1,15) # TODO: PGM specific
        self.growthType	= 1 # PGM specific - development trait

        # contract 
        self.salary	= 0 # game will set automatically
        self.length	= random.randint(1,4) # TODO: get contract info
        self.guarantee = 1

        # contract extension settings
        self.eGuarantee	= 1
        self.eLength = 1
        self.eSalary = 1
        
        # passing attributes
        self.throwOnRun	 = default_rating
        # pass accuracy
        self.sPassAcc = default_rating
        self.mPassAcc = default_rating
        self.dPassAcc = default_rating

        # physical attributes
        self.power = default_rating 
        self.agility = default_rating
        self.jumping = default_rating
        self.injuryProne = default_rating
        self.stamina = default_rating
        self.intelligence = random.randint(20, 100) # TODO: not present in maddenratings.com

        # personality attributes
        self.discipline	= random.randint(10, 100) # TODO: not present in maddenratings.com
        self.loyalty = random.randint(20, 100)	# TODO: PGM specific
        self.ambition = random.randint(30, 100) # TODO: PGM specific 
        self.greed = random.randint(1, 100) # TODO: PGM specific
        self.decisions	= default_rating
        
        # blocking attributes
        self.passBlock	= default_rating
        self.rushBlock	= default_rating
        
        # skill position attributes
        self.releaseLine = default_rating
        self.routeRun = default_rating 
        self.ballSecurity = default_rating
        self.trucking = default_rating
        self.elusiveness = default_rating
        self.skillMove	= default_rating 
        self.vision	= default_rating
        self.speed = default_rating
        self.catching = default_rating

        # defensive + kicking attributes
        self.zoneCover = default_rating
        self.blockShedding	= default_rating
        self.tackle	= default_rating
        self.kickAccuracy = default_rating
        self.ballStrip	= default_rating
        self.manCover = default_rating	
        self.burst	= default_rating

    def __hash__(self):
        return int(self.iden)

    def __eq__(self, other):
        return (self.forename, self.surname, self.iden) ==  (other.forename, other.surname, other.iden)

    def __ne__(self, other):
        return not(self == other)
    
    def __repr__(self) -> str:
        return str(vars(self))
    
# dict that maps Madden attributes to PGM attributes
maddenToPGM = {
    "Catching" : "catching",
    "Throw Accuracy Short": "sPassAcc",
    "Throw Accuracy Medium": "mPassAcc",
    "Throw Accuracy Deep": "dPassAcc",
    "Agility": "agility",
    "Throw on the Run": "throwOnRun",
    "Pass Block": "passBlock",
    "Run Block": "rushBlock",
    "Release": "releaseLine",
    "Injury": "injuryProne",
    "Stamina": "stamina",
    "Jumping": "jumping",
    "Short Route Running": "routeRun",
    "Medium Route Running": "routeRun",
    "Deep Route Running": "routeRun",
    "Strength": "power",
    "Throw Power": "power",
    "Kick Power": "power",
    "Zone Coverage": "zoneCover",
    "Carrying": "ballSecurity",
    "Block Shedding": "blockShedding",
    "Trucking": "trucking",
    "Tackle": "tackle",
    "Awareness": "decisions",
    "Kick Accuracy": "kickAccuracy",
    "Hit Power": "ballStrip",
    "Change of Direction": "elusiveness",
    "Juke Move": "skillMove",
    "Spin Move": "skillMove",
    "Man Coverage": "manCover",
    "Acceleration": "burst",
    "BC Vision": "vision",
    "Speed": "speed",
}

NFL_ABBREV = dict()
def populateAbbrevDict():
    with open('nflteams.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            NFL_ABBREV[row["Name"]] = row["Abbreviation"]

# roster creation functions
def generateRandomAppearance():

    return [
      "Head3",
      "Eyes3",
      "Hair3Brown",
      "Beard2Brown"
    ]
    
    hair_colors = ["Blonde", "Ginger", "Brown", "Black", "Grey", "White"]

    return ["Head" + str(random.randint(1,5)), 
            "Eyes" + str(random.randint(1,5)), 
            "Hair" + str(random.randint(1,5)) + random.choice(hair_colors),
            "Beard" + str(random.randint(1,5)) + random.choice(hair_colors),
        ]

# create player from maddenratings.com url
def generatePlayerFromURL(player_name, player_url):
    player_name_split = player_name.split(" ", 1) 
    new_player = Player(firstName=player_name_split[0], lastName=player_name_split[1])
    player_soup = BeautifulSoup(requests.get(player_url).text, "html.parser")
    
    # set player information attributes
    background_attrs = [elem for elem in player_soup.select('p[class=mb-0]')]
    for attr in background_attrs:
        attr_split = attr.text.split(" ")
        # set draft year
        # print(attr_split)
        if "Pro: " in attr_split:
            years_pro_ind = attr_split.index("Pro:")
            years_pro = int(''.join(c for c in attr_split[years_pro_ind + 1] if c.isdigit()))
            new_player.draftSeason = 2022 - years_pro
        # set team
        if "Team" in attr_split[0]:
            team_name = " ".join(attr_split[1:])
            new_player.teamID = NFL_ABBREV[team_name]
        # set position and age
        elif "Position" in attr_split[0]:
            new_player.position = attr_split[1]
            years_ind = attr_split.index("years")
            new_player.age = int(''.join(c for c in attr_split[years_ind - 1] if c.isdigit()))
    # set rating   
    rating_span = player_soup.select('span.attribute-box-player')[0]
    new_player.rating = int(rating_span.text)

    # get remaining ratings
    attributes = player_soup.select('li[class=mb-1]')
    for attribute in attributes:
        attr_text_split = attribute.text.split(" ", 1)
        attr_name = attr_text_split[1]
        attr_val = int(attr_text_split[0])
        if attr_name in maddenToPGM:
            pgm_attr_name = maddenToPGM[attr_name]
            # special cases
            if pgm_attr_name == "routeRun":
                setattr(new_player, pgm_attr_name, int(getattr(new_player, pgm_attr_name) + 0.33 * attr_val))
            elif pgm_attr_name == "power":
                if new_player.position == "QB" and attr_name == "Throw Power":
                    setattr(new_player, pgm_attr_name, attr_val)
                if new_player.position in ["K", "P"] and attr_name == "Kick Power":
                    setattr(new_player, pgm_attr_name, attr_val)
                if new_player.position not in ["QB", "K", "P"] and attr_name == "Strength":
                    setattr(new_player, pgm_attr_name, attr_val)
            elif pgm_attr_name == "skillMove":
                setattr(new_player, pgm_attr_name, int(getattr(new_player, pgm_attr_name) + 0.5 * attr_val))
            # general statement
            else:
                setattr(new_player, pgm_attr_name, attr_val)
    if new_player.draftSeason == -1:
        print([elem.text.split(" ") for elem in background_attrs])
    return new_player


# create most updated roster
def createUpdatedRoster():
    populateAbbrevDict()
    
    # open final file to write to
    jsonFile = open("roster.json", "w")

    # get all team URLs from MaddenRatings first
    MAIN_PAGE = "https://www.maddenratings.com/"
    main_page_soup = BeautifulSoup(requests.get(MAIN_PAGE).text, "html.parser")
    team_pages = [elem["href"] for elem in main_page_soup.select('a.sidebar-link.sidebar-link-open')]
    temp_count = 1
    final_roster = []
    # for each team URL, get players
    for team_page in team_pages:
        team_name = " ".join(team_page.split("/")[-1].split("-")).title()
        # DEBUG PURPOSES
        if "Arizona" not in team_name: # and "Agency" not in team_name:
            continue

        print(f"TEAM: {team_name} ({temp_count} / 33)")
        if team_name == "Free Agency":
            team_page = "https://maddenratings.com" + team_page
        team_page_soup = BeautifulSoup(requests.get(team_page).text, "html.parser")

        # iterate through each player, create Player model for player and append to final roster
        # use random ratings for free agents
        if team_name == "Free Agency":
            players = tqdm([(elem.text, elem['href']) for elem in team_page_soup.select("span.entry-font a")])
        else:
            players = tqdm([(elem['title'], elem['href']) for elem in team_page_soup.select("span.entry-font a")])

        for player_name, player_url in players:
            players.set_description(f"Processing player: {player_name}")
            if team_name == "Free Agency":
                player_name_split = player_name.split(" ", 1)
                player_model = Player(firstName=player_name_split[0], lastName=player_name_split[1], default_rating=random.randint(60, 80))
                player_model.teamID = "Free Agency"
            else:
                player_model = generatePlayerFromURL(player_name, player_url)
            final_roster.append(vars(player_model))
        temp_count += 1
        
    jsonStr = json.dumps(final_roster)
    jsonFile.write(jsonStr)
    jsonFile.close()

createUpdatedRoster()