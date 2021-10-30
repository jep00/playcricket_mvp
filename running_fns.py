# Play Cricket MVP

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
import numpy as np
from averages import batting_averages

pd.options.mode.chained_assignment = None

#############################
######## Main Set Up ########
#############################

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

def generate_batting_scorecard(scorecard, match_information, x):
    '''
    Inputs: scorecard - Part of soup that contains scorecard information
            match_information - Full match info dataframe
            x - int, 1 or 2 - the number of the innings

    Outputs dataframe of the batting scorecard
    '''
    teamname = match_information.loc[match_information.innings == x, 'teams'].values[0]
    
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


def generate_bowling_scorecard(scorecard, match_information, x):
    '''
    Inputs: scorecard - Part of soup that contains scorecard information
            match_information - Full match info dataframe
            x - int, 1 or 2 - the number of the innings

    Outputs dataframe of the bowling scorecard
    '''
    teamname = match_information.loc[match_information.innings != x, 'teams'].values[0]
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


def order_of_innings(match_information):
    '''Finds the order in which the innings took place'''
    match_information['innings'] = None
    
    if (match_information['toss'][0] == 'Won the toss and elected to bat') or (match_information['toss'][1] == 'Won the toss and elected to bowl'):
        match_information['innings'][0] = 1
        match_information['innings'][1] = 2

    elif (match_information['toss'][1] == 'Won the toss and elected to bat') or (match_information['toss'][0] == 'Won the toss and elected to bowl'):
        match_information['innings'][0] = 2
        match_information['innings'][1] = 1

    return match_information


def find_toss_information(matchsoup):
    team_boxes = matchsoup.find_all('td', {'class':'col-md-4 text-center v-top'})

    toss = []
    for i in team_boxes:
        toss_info = i.find('p', {'class':'team-info-3 adma'}).get_text()
        toss.append(toss_info)
    return toss

def find_result_information(matchsoup, clubs):
    '''
    Finds who won and how they won (X by Y runs or Z by W wickets)
    Returned in the form of a dataframe that will be merged with match information. Loser has None
    '''
    winner = matchsoup.find('p', {'class':'match-ttl'}).get_text().title().replace('Cc', 'CC')
    how_won = matchsoup.find('div', {'class':'info mdont'}).get_text().lstrip().capitalize()

    match_information = matchsoup.find_all('p', {'class': 'team-info-2'})

    # len match_information = 6: the result is displayed 3 times
    home_runs = match_information[0].get_text().split('/')[0][-7:].lstrip().rstrip()
    home_wkts = match_information[0].get_text().split('/')[1][0:3].lstrip().rstrip()
    home_ovrs = match_information[0].get_text().split('(')[1].split(')')[0].lstrip().rstrip()

    away_runs = match_information[1].get_text().split('/')[0][-7:].lstrip().rstrip()
    away_wkts = match_information[1].get_text().split('/')[1][0:3].lstrip().rstrip()
    away_ovrs = match_information[1].get_text().split('(')[1].split(')')[0].lstrip().rstrip()

    #Dealing with all outs
    if home_wkts[0] == 'A':
        home_wkts = 10
    if away_wkts[0] == 'A':
        away_wkts = 10

    scores_df = pd.DataFrame(data = {'teams':clubs,
                                     'runs':[home_runs, away_runs],
                                     'wkts':[home_wkts, away_wkts],
                                     'ovrs':[home_ovrs, away_ovrs]})
    
    win_df = pd.DataFrame(data = {'teams':[winner], 'win':[how_won]})
    return win_df, scores_df


def generate_dataframes(site_link):
    match_response = requests.get(site_link)
    matchsoup = Soup(match_response.text, 'html.parser')
    
    print('===== MATCH INFORMATION =====')
    home_team, away_team, teams, clubs = generate_match_information(matchsoup)
    win_df, score_df = find_result_information(matchsoup, clubs)
    toss = find_toss_information(matchsoup)
    match_information = pd.DataFrame(data = {'teams':clubs, 'toss': toss})
    match_information = match_information.merge(win_df, how = 'left', on = 'teams')
    match_information = match_information.merge(score_df, how = 'left', on = 'teams')
    order_of_innings(match_information)
    print(match_information)

    #Finding batting data
    batting_tables = matchsoup.find_all('table', {'class':'table standm table-hover'})
    batting_scorecard_one_ungen = batting_tables[0]
    batting_scorecard_two_ungen = batting_tables[1]

    #Generating batting data frame
    batting_scorecard_one = generate_batting_scorecard(batting_scorecard_one_ungen, match_information, 1)
    batting_scorecard_two = generate_batting_scorecard(batting_scorecard_two_ungen, match_information, 2)
    full_batting_scorecard = pd.concat([batting_scorecard_one, batting_scorecard_two])
    
    #Finding bowling data
    bowling_tables = matchsoup.find_all('table', {'class':'table bowler-detail table-hover'})
    bowling_scorecard_one_ungen = bowling_tables[0]
    bowling_scorecard_two_ungen = bowling_tables[1]

    #Generating bowling data frame
    bowling_scorecard_one = generate_bowling_scorecard(bowling_scorecard_one_ungen, match_information, 1)
    bowling_scorecard_two = generate_bowling_scorecard(bowling_scorecard_two_ungen, match_information, 2)
    full_bowling_scorecard = pd.concat([bowling_scorecard_one, bowling_scorecard_two])

    print('- batting + bowling dataframes generated -')

    return match_information, full_batting_scorecard, full_bowling_scorecard


#############################
## Finding the batting MVP ##
#############################

# Helper functions
def player_batting_average_comparison(df, average_batter_score):
    df['average'] = average_batter_score
    df['v_average'] = df['runs']/df['average']
    df['score'] *= df['v_average']
    df = df.drop(['average'], axis = 1)
    return df

def is_not_out(row):
    ''' the multiplier for a batter being not out = 20% '''
    if row['dismissal'] == 'not out':
        return 1.2
    else:
        return 1

def batting_milestone_marker(row):
    if row['runs'] > 99:
        row['score'] *= 1.2 # 20% Hundred multiplier
    elif row['runs'] > 49:
        row['score'] *= 1.1 # 10% Fifty multiplier
    elif row['runs'] > 24:
        row['score'] *= 1.05 # 5% 25-run multiplier
    return row['score']

def penalise_ducks(row):
    if (row['runs'] == 0) and (row['dismissal'] not in ['not out','did not bat']):
        row['score'] -= 1
    return row['score']


# Main processing function
def batting_mvp(match_information, full_batting_scorecard, average_team_score, average_batter_score):
    print('- finding batting mvps for each side -')

    k = sum(match_information.runs.astype(int))/2 # Average Runs per Innings (match)

    # In order to see if a player performed better than average for their position
    # we find what an average score is for their position, based on the number of
    # runs scored in the match
    average_score_ratio = k / average_team_score 
    average_batter_score = [(i * average_score_ratio) for i in average_batter_score]

    overall_df = pd.DataFrame()
    for i in match_information.index:
        j = match_information.teams[i]
        
        # Multiplier is 20% for winning the match
        if match_information.win[i] is not np.nan:
            beta_win = 1.20
        else:
            beta_win = 1
        
        team_df = full_batting_scorecard[full_batting_scorecard.team == j].drop('team', axis = 1)
        team_df = team_df.fillna(0)
        for i in team_df.index:
            if team_df.runs[i] == '':
                team_df.runs[i] = 0
        team_df.runs = team_df.runs.astype(int)
        team_df['proportion'] = team_df['runs'] / k
        team_df['score'] = (team_df.apply(lambda row: is_not_out(row), axis = 1)) * beta_win * team_df['proportion']
        team_df['score'] = team_df.apply(lambda row: batting_milestone_marker(row), axis = 1)
        team_df = player_batting_average_comparison(team_df, average_batter_score)
        team_df['score'] = team_df.apply(lambda row: penalise_ducks(row), axis = 1)

        team_df.index += 1
        overall_df = pd.concat([overall_df, team_df])

    overall_df.sort_values(by='score', ascending=False, inplace = True)
    return overall_df

#############################
## Finding the bowling MVP ##
#############################

# Helper functions

def convert_overs_for_calculations(row):
    '''
    Input note: Overs should be a float.

    This converts overs - written as 'Full overs'.'balls' into 'Full overs'.'proportion of over left'
    which is required for any calculations involving overs.
    '''
    if '.' in str(row['overs']):
        balls_remainder = (str(row['overs'])).split('.')[1]

        percent_remained = round(int(balls_remainder)/6, 3)
        overs_int = int(float(row['overs']))

        return overs_int + percent_remained
    else:
        return row['overs']

def player_bowling_average_comparison(df, match_average):
    df['average'] = match_average
    df['v_average'] = None
    for i in df.index:
        if df['wickets'][i] != 0:
            df['v_average'][i] = ( df['runs'][i] / df['wickets'][i] ) / df['average'][i]
        else:
            df['v_average'][i] = df['runs'][i] / df['average'][i]
        
    df['score'] *= df['v_average']
    df = df.drop(['average'], axis = 1)
    return df

def player_economy_comparison(df, match_economy):
    df['av_econ'] = match_economy
    df['v_av_econ'] = (df['runs']/df['overs']) / df['av_econ']
    df = df.drop(['av_econ'], axis = 1)
    return df

def expensive_no_fer(row, team_runs_conceded):
    ''' If a bowler doesn't take a wicket, and concedes more than 25% of the team runs, they're penalised '''
    if (row['runs'] > (0.25*team_runs_conceded)) & (row['wickets'] == 0):
        return 0.8
    else:
        return 1

def bowling_milestone_marker_wickets(row):
    if row['wickets'] >= 7:
        row['score'] *= 1.2 # 20% 7-fer multiplier
    elif row['runs'] >= 5:
        row['score'] *= 1.1 # 10% 5-fer multiplier
    elif row['runs'] >= 3:
        row['score'] *= 1.05 # 5% 3-fer multiplier
    return row['score']

def bowling_milestone_marker_maidens(row):
    if (row['maidens'] / row['overs']) >= 0.75:
        row['score'] *= 1.1 # 20% 7-fer multiplier
    elif (row['maidens'] / row['overs']) >= 0.5:
        row['score'] *= 1.05 # 10% 5-fer multiplier
    return row['score']

# Main processing function
def bowling_mvp(match_information, full_bowling_scorecard):
    print('- finding bowling mvps for each side -')

    full_bowling_scorecard.runs = full_bowling_scorecard.runs.astype(int)
    full_bowling_scorecard.wickets = full_bowling_scorecard.wickets.astype(int)
    full_bowling_scorecard.maidens = full_bowling_scorecard.maidens.astype(int)

    match_runs = sum(match_information.runs.astype(int))/2 # Average Runs per Innings (match)
    match_wickets = sum(match_information.wkts.astype(int))
    if match_wickets != 0:
        match_average = match_runs / match_wickets
    else:
        match_average = match_runs

    match_overs = 0
    for i in match_information.index:
        if '.' in str(match_information['ovrs'][i]):
            balls_remainder = (str(match_information['ovrs'][i])).split('.')[1]
            percent_remained = round(int(balls_remainder)/6, 3)
            overs_int = int(float(match_information['ovrs'][i]))
            match_overs += overs_int + percent_remained
        else:
            match_overs += match_overs
            
    match_economy = match_runs / match_overs

    # In order to see if a player performed better what would be expected,
    # we use the match bowling average and economy

    overall_df = pd.DataFrame()
    for i in match_information.index:
        j = match_information.teams[i]
        
        # Multiplier is 20% for winning the match
        if match_information.win[i] is not np.nan:
            beta_win = 1.20
        else:
            beta_win = 1
        
        team_df = full_bowling_scorecard[full_bowling_scorecard.team == j].drop('team', axis = 1)
        team_df['overs_raw'] = team_df['overs']
        team_df['overs'] = team_df.apply(lambda row: convert_overs_for_calculations(row), axis = 1)
        team_df['overs'] = team_df.overs.astype(float)
        
        team_economy_rate = sum(team_df['runs'].astype(int)) / sum(team_df['overs'].astype(int))
        team_df.runs = team_df.runs.astype(int)

        team_df['proportion_runs'] = team_df['runs'] / sum(team_df['runs'].astype(int))
        team_df['proportion_wkts'] = team_df['wickets'].astype(int) / sum(team_df['wickets'].astype(int))
        
        team_df['score'] = (team_df.apply(lambda row: expensive_no_fer(row, sum(team_df['runs'].astype(int))), axis = 1)) * beta_win + team_df['proportion_wkts']
        team_df['score'] = team_df.apply(lambda row: bowling_milestone_marker_wickets(row), axis = 1)
        team_df['score'] = team_df.apply(lambda row: bowling_milestone_marker_maidens(row), axis = 1)

        player_bowling_average_comparison(team_df, match_average)
        player_economy_comparison(team_df, match_economy)
        
        team_df.index += 1
        overall_df = pd.concat([overall_df, team_df])

    overall_df.sort_values(by='score', ascending=False, inplace = True)
    return overall_df

#############################
######## End Outputs ########
#############################

def print_top_and_bottom_three_players(df, action):
    top3 = df[0:3]
    bottom3 = df[-3:]

    print(f'\nThe most valuable players {action} are:')
    print(df[df['score']!=0][0:3])
    print(f'\nThe least valuable players {action} are:')
    print(df[df['score']!=0][-3:])

def run_app():
    pass


# TO MIGRATE TO RUN DOCUMENT

#site_link = find_match()
match_information, full_batting_scorecard, full_bowling_scorecard = generate_dataframes('https://www.play-cricket.com/website/results/4598125')

average_team_score, average_batter_score = batting_averages()
batting_df = batting_mvp(match_information, full_batting_scorecard, average_team_score, average_batter_score)
print_top_and_bottom_three_players(batting_df, 'batting')

bowling_df = bowling_mvp(match_information, full_bowling_scorecard)
print_top_and_bottom_three_players(bowling_df, 'bowling')


