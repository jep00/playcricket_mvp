# Finding the average score for each batting position group

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
import numpy as np

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
    middle_order_filter = 'batting_positionmax2=7;batting_positionmin2=4;batting_positionval2=batting_position'
    lower_order_filter = 'batting_positionmax2=11;batting_positionmin2=8;batting_positionval2=batting_position'

    filters = [top_order_filter, middle_order_filter, lower_order_filter]

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

    average_team_score = (3 * positional_averages[0]) + (4 * positional_averages[1]) + (4 * positional_averages[2])

    average_batter_score = [
        positional_averages[0], positional_averages[0], positional_averages[0],
        positional_averages[1], positional_averages[1], positional_averages[1], positional_averages[1],
        positional_averages[2], positional_averages[2], positional_averages[2], positional_averages[2]
    ]

    return average_team_score, average_batter_score
