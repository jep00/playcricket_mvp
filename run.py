# Play Cricket MVP

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd


def find_match():
    """ Finds the web link for the match """
    check = False
    while check is False:
        match_id = input("Play cricket match ID: ")
        if len(match_id) > 10:
            # Assume they used the entire link
            site_link = match_id
        else:
            # Assume they used the match identifier
            site_link = f'https://www.play-cricket.com/website/results/{match_id}'
        is_check = input(f'Check the site link: {site_link}\nIs this correct? y/n: ')
        if is_check.lower()[0] == 'y':
            check = True

    return(site_link)

def soup(site_link):
    match_response = requests.get(site_link)
    matchsoup = Soup(match_response.text, 'html.parser')

    print(matchsoup.prettify())
    
    teams = []
    i = 0
    while i < 2:
        team_club = matchsoup.find_all(class_='team-name')[i].text
        
        team_name = matchsoup.find_all(class_='team-info-2')[i].text
        team_name = team_name.lstrip().split('\n')[0]
        
        teams.append(f'{team_club}, {team_name}')
        #teams.append(f'{team_club[i]}, {team_name[i]}')
        #print(team.text)
        i+=1
    
    home_team = teams[0]
    away_team = teams[1]
    print(f'Match: {home_team} (h) vs. {away_team} (a)')

    scorecard_table = matchsoup.find('table', {'class':'table standm table-hover'})

    players_to_add = []
    for row in scorecard_table.tbody.find_all('tr'):
        columns = row.find('td')
        player = columns.find('div', {'class':'bts'})
        players_to_add.append(player.get_text())

    scorecard_df = pd.DataFrame(data = {'player':players_to_add})
    print(scorecard_df)


#site_link = find_match()
soup('https://www.play-cricket.com/website/results/4583981')
