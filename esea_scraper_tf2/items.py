from scrapy.item import Item, Field

class MatchItem(Item):
    match_id = Field()
    match_time = Field()
    length = Field()
    map_name = Field()
    team1 = Field()
    team2 = Field()
    forfeit = Field()

class TeamItem(Item):
    team_id = Field()
    total_score = Field()
    players = Field()

class PlayerItem(Item):
    player_id = Field()
    points = Field()
    damage = Field()
    frags = Field()
    assists = Field()
    deaths = Field()
    captures = Field()
    blocks = Field()
    dominations = Field()
    revenges = Field()
    ubers = Field()
    uber_drops = Field()
