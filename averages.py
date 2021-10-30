# Finding the average score for each batting position group
# and for bowlers

'''
A note:
For bowling, we would ideally compare against another form of check. 'Bowling position' isn't a thing, and
play-cricket has no way of letting us know if a bowler is left- or right-armed, a spinner, seamer, medium pacer,
fast bowler, etc.
'''

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
import numpy as np

def convert_overs(row):
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


def batting_averages():
    '''
    This will be a function to find the average score a batting makes in each position group
    Top Order = 1, 2, 3
    Middle Order = 4, 5, 6, 7
    Tail = 8, 9, 10, 11
    '''
    
    print('- finding overall batting averages -')

    start_date = '28+Oct+2016'
    end_date = '28+Oct+2021'

    top_order_filter = 'batting_positionmax3=3;batting_positionmin3=1;batting_positionval3=batting_position'
    top_middle_order_filter = 'batting_positionmax2=5;batting_positionmin2=4;batting_positionval2=batting_position'
    lower_middle_order_filter = 'batting_positionmax2=7;batting_positionmin2=6;batting_positionval2=batting_position'
    lower_order_filter = 'batting_positionmax2=11;batting_positionmin2=8;batting_positionval2=batting_position'

    filters = [top_order_filter, top_middle_order_filter, lower_middle_order_filter, lower_order_filter]

    positional_averages = []

    for x in filters:

        link = f'https://stats.espncricinfo.com/ci/engine/stats/index.html?{x};class=1;filter=advanced;groupby=team;orderby=batting_average;spanmax2={end_date};spanmin2={start_date};spanval2=span;template=results;type=batting'

        response = requests.get(link)
        page_soup = Soup(response.text, 'html.parser')

        table = page_soup.find_all('table', {'class':'engineTable'})[2]

        country, inns, no, runs = [], [], [], []

        for row in table.find_all('tr', {'class':'data1'}):
            columns = row.find_all('td')
            country.append(columns[0].get_text())
            inns.append(int(columns[4].get_text()))
            no.append(int(columns[5].get_text()))
            runs.append(int(columns[6].get_text()))

        df = pd.DataFrame(data = {'country':country, 'innings':inns, 'not outs':no, 'runs':runs})

        average = round( sum(runs) / ( (sum(inns) - sum(no)) ), 4 )
        positional_averages.append(average)

    '''
    We find the average team score by taking:
            3 * Average for positions 1, 2, 3
            +
            4 * Average for positions 4, 5, 6, 7
            +
            4 * Average for positions 8, 9, 10, 11
    '''

    average_team_score = (3 * positional_averages[0]) + (2 * positional_averages[1]) + (2 * positional_averages[2]) + (4 * positional_averages[3])

    average_batter_score = [
        positional_averages[0], positional_averages[0], positional_averages[0],
        positional_averages[1], positional_averages[1],
        positional_averages[2], positional_averages[2],
        positional_averages[3], positional_averages[3], positional_averages[3], positional_averages[3]
    ]

    return average_team_score, average_batter_score



def bowling_averages():
    '''
    This will be a function to find the average number of runs a bowler concedes for each wicket they take,
    and the average economy rate (runs per over) a bowler concedes. We will consider both in our MVP calculations.

    Average = (runs conceded) / (wickets taken) if wickets != 0 else average = (runs conceded)
        We penalise bowlers who concede a certain proportion of a teams runs without taking a wicket

    Economy = (runs conceded) / (overs bowled)
        Note an over is 6 balls, so 3.3 overs is 3 and a half overs, thus 3.5 in calculations.
    '''
    
    print('- finding overall bowling averages and economies -')

    start_date = '28+Oct+2016'
    end_date = '28+Oct+2021'

    link = f'https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;groupby=team;orderby=bowling_average;spanmax2={end_date};spanmin2={start_date};spanval2=span;template=results;type=bowling'

    
    response = requests.get(link)
    page_soup = Soup(response.text, 'html.parser')

    table = page_soup.find_all('table', {'class':'engineTable'})[2]

    country, overs, runs, wickets = [], [], [], []

    for row in table.find_all('tr', {'class':'data1'}):
        columns = row.find_all('td')
        country.append(columns[0].get_text())
        overs.append(float(columns[5].get_text()))
        runs.append(int(columns[7].get_text()))
        wickets.append(int(columns[8].get_text()))

    df = pd.DataFrame(data = {'country':country, 'overs':overs, 'runs':runs, 'wickets':wickets})

    df['overs_converted'] = (df.apply(lambda row: convert_overs(row), axis = 1))

    total_overs = sum(df['overs_converted'])
    total_wickets = sum(df['wickets'])
    total_runs = sum(df['runs'])

    economy = total_runs / total_overs
    if total_wickets != 0:
        average = total_runs / total_wickets
    else:
        average = total_runs
        
    return round(economy, 3), round(average, 3)

    
