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

def generate_batting_scorecard(scorecard, match_infomation, x):
    '''
    Inputs: scorecard - Part of soup that contains scorecard infomation
            match_infomation - Full match info dataframe
            x - int, 1 or 2 - the number of the innings

    Outputs dataframe of the batting scorecard
    '''
    teamname = match_infomation.loc[match_infomation.innings == x, 'teams'].values[0]
    
    player_names = []
    amount_of_runs = []
    how_out = []
    for row in scorecard.tbody.find_all('tr'):

        player = row.find('td').find('div', {'class':'bts'}).get_text()
        runs = row.find('td', {'class':'sTD'}).get_text()
        dismissal_info = row.find('div', {'class':'m-player'}).get_text().rstrip()
        
        player_names.append(player)
        amount_of_runs.append(runs)
        how_out.append(dismissal_info)

    df = pd.DataFrame(data = {'player':player_names, 'runs':amount_of_runs, 'dismissal':how_out})
    df['team'] = teamname
    return df


def generate_bowling_scorecard(scorecard, match_infomation, x):
    '''
    Inputs: scorecard - Part of soup that contains scorecard infomation
            match_infomation - Full match info dataframe
            x - int, 1 or 2 - the number of the innings

    Outputs dataframe of the bowling scorecard
    '''
    teamname = match_infomation.loc[match_infomation.innings != x, 'teams'].values[0]
    #We choose != x as the bowling team is the team not batting
  
    player_names = []
    overs = []
    mdns = []
    runs = []
    wickets = []
    econ = []
    for row in scorecard.tbody.find_all('tr'):
        bowling_data = row.find_all('td')
        player = bowling_data[0].get_text()
        overs_bowled = bowling_data[1].get_text()
        mdns_bowled = bowling_data[2].get_text()
        runs_conceded = bowling_data[3].get_text()
        wickets_taken = bowling_data[4].get_text()
        economy = bowling_data[7].get_text()

        player_names.append(player)
        overs.append(overs_bowled)
        mdns.append(mdns_bowled)
        runs.append(runs_conceded)
        wickets.append(wickets_taken)
        econ.append(economy)

    df = pd.DataFrame(data = {'player':player_names, 'overs':overs, 'maidens':mdns, 'runs':runs, 'wickets':wickets, 'economy':econ})
    df['team'] = teamname
    return df
        

def generate_match_information(matchsoup):
    teams = []
    clubs = []
    i = 0
    while i < 2:
        team_club = matchsoup.find_all(class_='team-name')[i].text
        
        team_name = matchsoup.find_all(class_='team-info-2')[i].text
        team_name = team_name.lstrip().split('\n')[0]

        clubs.append(team_club)
        teams.append(f'{team_club}, {team_name}')
        i+=1
    
    home_team = teams[0]
    away_team = teams[1]
    return home_team, away_team, teams, clubs


def order_of_innings(match_infomation):
    '''Finds the order in which the innings took place'''
    match_infomation['innings'] = None
    
    if (match_infomation['toss'][0] == 'Won the toss and elected to bat') or (match_infomation['toss'][1] == 'Won the toss and elected to bowl'):
        match_infomation['innings'][0] = 1
        match_infomation['innings'][1] = 2

    elif (match_infomation['toss'][1] == 'Won the toss and elected to bat') or (match_infomation['toss'][0] == 'Won the toss and elected to bowl'):
        match_infomation['innings'][0] = 2
        match_infomation['innings'][1] = 1

    return match_infomation


def find_toss_information(matchsoup):
    team_boxes = matchsoup.find_all('td', {'class':'col-md-4 text-center v-top'})

    toss = []
    for i in team_boxes:
        toss_info = i.find('p', {'class':'team-info-3 adma'}).get_text()
        toss.append(toss_info)
    return toss

def find_result_infomation(matchsoup):
    '''
    Finds who won and how they won (X by Y runs or Z by W wickets)
    Returned in the form of a dataframe that will be merged with match infomation. Loser has None
    '''
    winner = matchsoup.find('p', {'class':'match-ttl'}).get_text().title().replace('Cc', 'CC')
    how_won = matchsoup.find('div', {'class':'info mdont'}).get_text().lstrip().capitalize()

    # Next steps => scrape runs, wickets, overs
    
    df = pd.DataFrame(data = {'teams':[winner], 'win':[how_won]})
    return df
                                    

def generate_dataframes(site_link):
    match_response = requests.get(site_link)
    matchsoup = Soup(match_response.text, 'html.parser')
    #print(matchsoup.prettify())
    
    print('===== MATCH INFORMATION =====')
    home_team, away_team, teams, clubs = generate_match_information(matchsoup)
    winner = find_result_infomation(matchsoup)
    toss = find_toss_information(matchsoup)
    match_infomation = pd.DataFrame(data = {'teams':clubs, 'toss': toss})
    match_infomation = match_infomation.merge(winner, how = 'left', on = 'teams')
    order_of_innings(match_infomation)
    print(match_infomation)

    print('===== BATTING =====')
    
    #Finding batting data
    batting_tables = matchsoup.find_all('table', {'class':'table standm table-hover'})
    batting_scorecard_one_ungen = batting_tables[0]
    batting_scorecard_two_ungen = batting_tables[1]

    #Generating batting data frame
    batting_scorecard_one = generate_batting_scorecard(batting_scorecard_one_ungen, match_infomation, 1)
    batting_scorecard_two = generate_batting_scorecard(batting_scorecard_two_ungen, match_infomation, 2)
    full_batting_scorecard = pd.concat([batting_scorecard_one, batting_scorecard_two])
    print(full_batting_scorecard)

    print('===== BOWLING =====')
    
    #Finding bowling data
    bowling_tables = matchsoup.find_all('table', {'class':'table bowler-detail table-hover'})
    bowling_scorecard_one_ungen = bowling_tables[0]
    bowling_scorecard_two_ungen = bowling_tables[1]

    #Generating bowling data frame
    bowling_scorecard_one = generate_bowling_scorecard(bowling_scorecard_one_ungen, match_infomation, 1)
    bowling_scorecard_two = generate_bowling_scorecard(bowling_scorecard_two_ungen, match_infomation, 2)
    full_bowling_scorecard = pd.concat([bowling_scorecard_one, bowling_scorecard_two])
    print(full_bowling_scorecard)
    
                          
def run_app():
    pass




#site_link = find_match()
generate_dataframes('https://www.play-cricket.com/website/results/4598125')










