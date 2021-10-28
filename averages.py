# Finding the average score for each batting position group

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
import numpy as np

'''
This will be a function to find the average score a batting makes in each position group
Top Order = 1, 2, 3
Middle Order = 4, 5, 6, 7
Tail = 8, 9, 10, 11
'''

# Middle Order
#https://stats.espncricinfo.com/ci/engine/stats/index.html?batting_positionmax2=7;batting_positionmin2=4;batting_positionval2=batting_position;class=1;filter=advanced;groupby=team;orderby=batting_average;spanmax2=28+Oct+2021;spanmin2=28+Oct+2016;spanval2=span;template=results;type=batting

# Upper Order
#https://stats.espncricinfo.com/ci/engine/stats/index.html?batting_positionmax3=3;batting_positionmin3=1;batting_positionval3=batting_position;class=1;filter=advanced;groupby=team;orderby=batting_average;spanmax2=28+Oct+2021;spanmin2=28+Oct+2016;spanval2=span;template=results;type=batting

# Lower Order
#https://stats.espncricinfo.com/ci/engine/stats/index.html?batting_positionmax2=11;batting_positionmin2=8;batting_positionval2=batting_position;class=1;filter=advanced;groupby=team;orderby=batting_average;spanmax1=28+Oct+2021;spanmin1=28+Oct+2016;spanval1=span;template=results;type=batting


match_response = requests.get(site_link)
matchsoup = Soup(match_response.text, 'html.parser')
