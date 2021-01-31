# nba-tipoff-scraper

Player tipoff skill ranking is done using Microsoft's trueskill algorithm https://trueskill.org/.
Elo and glicko/glicko2 were also considered; elo doesn't account for uncertainty and glicko didn't have any ready-made packages.
Ultimately we'll want to either recreate or adapt a glicko2 algorithm for skill ranking.

The process is: 
Prep:
1. Fetch NBA historical data since 1997
2. Loop through data and calculate player "skill" at tipoff based on trueskill algorithm
3. Use skill ranking and a known proportion of tipoff winning teams scoring first basket to predict odds of each team scoring first
4. Save player skill and prediction results for each game. 

Live Bet:
1. Retrieve best odds line across betting sites
2. Calcuate odds of team scoring first using prep data above
3. Determine if a bet is EV positive
4. If a bet is EV positive return the kelly bet size
5. Rank all possible bets, kelly bet sizes and times to determine optimal strategy

# How to setup your environment

1. Download the repo to your local folder
2. Set up a virtual environment at the project root (python 3.8 or later preferred)
3. Ask Logan if scraped data is not loaded into the repo already

# Development Process

- Never commit directly to the main branch
- Create a branch with your name or a feature title
- Maintain a clear commit history (err on the side of being verbose)
- Use the #todos as a sort of backlog
- Currently variable naming conventions etc. are a bit of a free for all, but try to:
  - Capitalize when naming files
  - Lowercase and snakecase variables and methods

# Repo contents


Preliminary results when setting tipoff win probability threshold at 0.6 or 0.7 (don't recall which) give me a %55.64 prediction rate for who scores first. American odds for most sites cap at around -125, and you can get ~ -110, which requires just %53.00 or so for positive EV.
