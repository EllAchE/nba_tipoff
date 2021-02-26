# nba-tipoff-scraper

Player tipoff skill ranking is done using Microsoft's trueskill algorithm https://trueskill.org/.
Elo and glicko/glicko2 were also considered; elo doesn't account for uncertainty and glicko didn't have any ready-made packages.
Ultimately we'll want to either recreate or adapt a glicko2 algorithm for skill ranking.

# Sportsbook Regulations

- Sportsbooks have regional restrictions, they vary from country to country and region/state
- Sportsbooks can/will kick you off for violating their terms of service
- Arbitrage betting is a reason to kick you off
- Violating the "one account, one user" policy is another reason to kick you off
  **- Coordinating with a cabal/syndicate to get around bet sizing limits is against the terms of service, even if the bets are made independently**
- There are payout limits on props bets. For drafkings that is set at $20,000, but it likely varies based on exchange. With experience having placed bets, I have yet to hit limits on betmgm (betting as much as $800) and on fanduel seem to be capped at $150 payout.

# Code

The process is:
Prep:

1. Fetch NBA historical data since 1997
2. Loop through data and calculate player "skill" at tipoff based on trueskill algorithm
3. Use skill ranking and a known proportion of tipoff winning teams scoring first basket to predict odds of each team scoring first
4. Save player skill and prediction results for each game.

Live Bet:

1. Retrieve best odds line across betting sites
2. Calculate odds of team scoring first using prep data above
3. Determine if a bet is EV positive
4. If a bet is EV positive return the kelly bet size adjusted by a factor of 0.7
5. Rank all possible bets, kelly bet sizes and times to determine optimal strategy

# How to setup your environment

1. Download the repo to your local folder
2. Set up a virtual environment at the project root (python 3.8 or later preferred)
3. Ask Logan if scraped data is not loaded into the repo already, or if you have any other questions genrally

# Development Process

- Never commit directly to the main branch
- Create a branch with your name and a feature title (i.e. logan/additional-stats-fetching)
- Maintain a clear commit history (err on the side of being verbose)
- Use the #todos as a sort of backlog
- At the start variable naming conventions etc. were a bit of a free for all, we've cleaned that up now but you may find legacy names sometimes. Try to:
  - lower snakecase file names, except those holding only constants which are caps (i.e. ENVIRONMENT)
  - Camelcase variable names
  - Use argument typing

# Useful Links

- The data source for tipoff results: https://www.basketball-reference.com/
- Similar analysis on reddit: https://www.reddit.com/r/nba/comments/dhandf/oc_elo_system_to_determine_who_are_the_best_at/ (they didn't do it well)
- **Existing API (with great docs) to fetch NBA data: https://github.com/swar/nba_api/**
- Source for live lineups: https://www.lineups.com/nba/lineups
- Source for injury updates (still choosing best): https://www.espn.com/nba/injuries
- Bball ref scraper I found (don't think it does what we want): https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/API.md
- Tableau created with tipoff of some current players https://fansided.com/stats/jump-ball-statistics-1998-present/

# Early Results

Preliminary results when setting tipoff win probability threshold at 0.6 or 0.7 (don't recall which) give me a %55.64 prediction rate for who scores first. American odds for most sites cap at around -125, and you can get ~ -110, which requires just %53.00 or so for positive EV.
^Update to the above. After a 1 week forward test my accuracy on postive EV bets is approximately 64%, likely inflated due to small sample size, however I do expect to reasonably have a 60% or greater prediction rate, it's just a question of bet sizing and improving the certainty associated with probabilities

# Repo Contents

The repo currently has methods and data for:
  - Scraping historical tipoff and first score/possession data from basketball reference.com 
  - Fetchin pbp data from nba api and filtering to first scoring possession.
  - Fetching live odds from some (not all) bookies offering props bets. I.e. - Fanduel, Draftkings, Betmgm
  - Calculating trueskill based on historical data
  - Calculating bet size for a team bet
  - Calculating bet size for a player spread (currently naive floor math)
 
The "Epics" that are missing
  - Comparison of trueskill to glicko/elo
  - Database for player, team etc. conversions
  - Additional stats comparison (i.e. team efficiency, proportion of 3s vs. 2s)
  - Day-of betting confirmation (i.e. alerts if there is an injury or change to starters just before game starts, which affect projected odds)

# Picking up from Backlog
Just search for a todo, they will be in the appropriate file and ideally verbose enough to follow, but ask Logan if not. Most immediate prioirities are live odds fetching and day-of confirmation