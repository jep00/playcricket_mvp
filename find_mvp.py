import running_fns as rf

match_information, full_batting_scorecard, full_bowling_scorecard = rf.generate_dataframes('https://www.play-cricket.com/website/results/4598125')
rf.batting_mvp(match_information, full_batting_scorecard)
