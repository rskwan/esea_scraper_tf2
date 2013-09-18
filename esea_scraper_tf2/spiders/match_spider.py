import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

from esea_scraper_tf2.items import MatchItem, TeamItem, PlayerItem

class MatchSpider(CrawlSpider):
    """Crawls play.esea.net schedule starting from June 26, 2011 and ending on September
       6, 2013 to scrape match data."""

    name = 'play.esea.net'
    allowed_domains = ['play.esea.net']
    schedule_url = ('http://play.esea.net/index.php?s=league&d=schedule&date=2011-06-26'
                    '&game_id=43&division_level=all')  
    start_urls = [schedule_url]

    # regexes for links
    schedule_2011 = r'date\=2011\-(0[6-9]|1[0-2])\-[0-3][0-9]'
    schedule_2012 = r'date\=2012\-[0-1][0-9]\-[0-3][0-9]'
    schedule_2013 = r'date\=2013\-(0[1-8]\-[0-3][0-9]|09\-0[1-6])'
    match1 = r'index.php\?s\=stats\&d\=match\&id\=\d+'
    match2 = r'index.php\?d\=match\&id\=\d+\&s\=stats'

    rules = (
        Rule(SgmlLinkExtractor(allow=(schedule_2011, ))),
        Rule(SgmlLinkExtractor(allow=(schedule_2012, ))),
        Rule(SgmlLinkExtractor(allow=(schedule_2013, ))),
        Rule(SgmlLinkExtractor(allow=(match1, match2)), callback='parse_match'),
    )

    def get_player_row(self, row):
        """Return PlayerItem using player information in the given row."""
        player = PlayerItem()
        entries = row.select('td')

        player_url = entries[0].select('a[2]/@href').extract()[0]
        m = re.search(r'\d+', player_url)
        if m:
            player['player_id'] = int(m.group(0))
        else:
            player['player_id'] = None

        player['points'] = int(entries[1].select('text()').extract()[0])
        player['damage'] = int(entries[3].select('text()').extract()[0])
        player['frags'] = int(entries[5].select('text()').extract()[0])
        player['assists'] = int(entries[7].select('text()').extract()[0])
        player['deaths'] = int(entries[9].select('text()').extract()[0])
        player['captures'] = int(entries[11].select('text()').extract()[0])
        player['blocks'] = int(entries[12].select('text()').extract()[0])
        player['dominations'] = int(entries[13].select('text()').extract()[0])
        player['revenges'] = int(entries[14].select('text()').extract()[0])
        player['ubers'] = int(entries[15].select('text()').extract()[0])
        player['uber_drops'] = int(entries[16].select('text()').extract()[0])

        return player

    def get_players(self, tbody):
        """Return list of PlayerItems with info from the given table body."""
        players = []
        player_rows = tbody.select('tr')
        for row in player_rows:
            players.append(self.get_player_row(row))
        return players

    def get_team_row(self, row):
        """Return tuple of team id and score from the given row (of the page's top box)."""
        team_url = row.select('th/a/@href').extract()[0]
        m = re.search(r'\d+', team_url)
        if m:
            team_id = int(m.group(0))
        else:
            team_id = None
        # golden cap rule
        score_elem = row.select('td[4]/text()').extract()
        if len(score_elem) == 0:
            score_elem = row.select('td[5]/text()').extract()
        team_score = int(score_elem[0])
        return (team_id, team_score)
        
    def get_teams(self, selector, forfeit):
        """Return a list of TeamItems with information from the page of the given selector,
           omitting players if match was forfeited."""
        team1 = TeamItem()
        team2 = TeamItem()

        box = selector.select('//div[@id="body-match-stats"]/table[@class="box"][1]')
        row1 = box.select('tr[2]')
        row2 = box.select('tr[3]')
        team1_row_info = self.get_team_row(row1)
        team2_row_info = self.get_team_row(row2)

        team1['team_id'] = team1_row_info[0]
        team1['total_score'] = team1_row_info[1]
        team2['team_id'] = team2_row_info[0]
        team2['total_score'] = team2_row_info[1]

        if not forfeit:
            tbody1 = selector.select('//tbody[@id="body-match-total1"]')
            tbody2 = selector.select('//tbody[@id="body-match-total2"]')
            team1['players'] = self.get_players(tbody1)
            team2['players'] = self.get_players(tbody2)

        return [team1, team2]

    def get_match_id(self, url):
        """Gets the match ID from a match URL."""
        m = re.search(r'id\=(\d+)', url)
        if m:
            return int(m.group(1))
        else:
            return None

    def parse_match(self, response):
        """Parses a match page."""
        self.log('Found match page: {0}'.format(response.url))

        selector = HtmlXPathSelector(response)
        match = MatchItem()
        match['match_id'] = self.get_match_id(response.url)

        # get match info
        info = selector.select('//div[@class="match-header"]/text()').extract()[-1]
        print "*****info: " + str(info)
        info = info.strip()
        info = info.split(' / ')
        match['match_time'] = info[0]
        match['length'] = info[1]
        match['map_name'] = info[2]

        # check for forfeit
        forfeit = False
        module_headers = selector.select('//div[@class="module-header"]/text()').extract()
        if 'Forfeit Note' in module_headers:
            forfeit = True
        match['forfeit'] = forfeit

        # get teams
        teams = self.get_teams(selector, forfeit)
        match['team1'] = teams[0]
        match['team2'] = teams[1]

        return match
