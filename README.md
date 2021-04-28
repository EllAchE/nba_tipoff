# nba-tipoff-scraper

Bets are based on 2 variables, odds of winning tipoff and over/under performance of expected tipoff win percentage

Player tipoff skill ranking is done using Microsoft's [trueskill]( https://trueskill.org/) algorithm.
[Elo](https://github.com/sublee/elo) and glicko/[glicko2](https://github.com/sublee/glicko2) were also considered; all three algorithms are actually implemented in the code base but trueskill is used for predictions.
Elo performs best overall based on log-loss results when backtesting tipoff predictions, however the improvement was marginal and
due to time constraints the trueskill algorithm was chosen. Trueskill also converges to an accurate value more quickly than
Elo and so is better for players with less data.

I had expected glicko2 to outperform the other algorithms, and it's possible that it may with proper parameter tuning, but again a time issue.

Outperformance is just done using historical data.


## Code/Process

###Prep:

1. Fetch NBA historical data since 1997 ([see docs]())
2. Loop through data and calculate player "skill" at tipoff based on trueskill algorithm ([see docs]())
3. Use skill ranking and a known proportion of tipoff winning teams scoring first basket to predict odds of each team scoring first ([see docs]())
4. Save player skill and prediction results for each game. ([see docs]())

###Live Bet:

1. Retrieve best odds line across betting sites ([see docs]())
2. Calculate odds of team scoring first using prep data above ([see docs]())
3. Determine if a bet is EV positive ([see docs]())
4. If a bet is EV positive return the kelly bet size adjusted by a factor of 0.7 ([see docs]())
5. Rank all possible bets, kelly bet sizes and times to determine optimal strategy ([see docs]())

# How to setup your environment

1. Download the repo to your local folder
2. Set up a virtual environment at the project root (python 3.8 or later preferred)
3. Ask Logan if scraped data is not loaded into the repo already, or if you have any other questions

# Development Process

- Never commit directly to the main branch
- Create a branch with your name and a feature title (i.e. logan/additional-stats-fetching)
- Maintain a clear commit history (err on the side of being verbose)
- Use #todos and todos.txt as a sort of backlog
- At the start variable naming conventions etc. were a bit of a free for all, cleaned that up now but you may find legacy names sometimes. Try to:
  - lower snakecase file names, except those holding only constants which are caps (i.e. ENVIRONMENT)
  - Camelcase variable names
  \*You may also see 

# Useful Links

- The data source for tipoff results: https://www.basketball-reference.com/
- Similar analysis on reddit: https://www.reddit.com/r/nba/comments/dhandf/oc_elo_system_to_determine_who_are_the_best_at/ (they didn't do it well)
- **Existing API (with great docs) to fetch NBA data:**  https://github.com/swar/nba_api/
- Source for live lineups: https://www.rotowire.com/basketball/nba-lineups.php
- Source for injury updates (still choosing best): https://www.rotowire.com/basketball/nba-lineups.php
- Bball ref scraper I found (don't think it does what we want): https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/API.md
- Tableau created with tipoff of some current players https://fansided.com/stats/jump-ball-statistics-1998-present/

## Early Results/Key Figures

Preliminary results when setting tipoff win probability threshold at 0.7 (don't recall which) give me a 55.64% prediction rate for who scores first.

# Repo Contents

The repo currently has methods and data for:
  - Scraping historical tipoff and first score/possession data from basketball reference.com 
  - Fetchin pbp data from nba api and filtering to first scoring possession.
  - Fetching live odds from some (not all) bookies offering props bets. I.e. - Fanduel, Draftkings, Betmgm
  - Calculating trueskill based on historical data
  - Calculating bet size for a team bet
  - Calculating bet size for a player spread (currently naive floor math)
 
The "Epics" that are missing
  - Database for player, team etc. conversions
  - Additional stats comparison (i.e. team efficiency, proportion of 3s vs. 2s)
  - Day-of betting confirmation (i.e. alerts if there is an injury or change to starters just before game starts, which affect projected odds)
  - Machine learning predictions refined enough to improve on the naive predictions

# Picking up from Backlog
Just search for a todo, they will be in the appropriate file and ideally verbose enough to follow, but ask Logan if not. Most immediate prioirities are live odds fetching and day-of confirmation

# NCAA
Given my recent discovery that NCAA data could be used for betmgm, I found a great repo with data here: https://github.com/lbenz730/ncaahoopR_data. The dataset is too large for it to be worth adding to githug so save it locally and move it to this path - Data/ncaahoopR_data-master/* if you are going to run analysis on the raw data.
