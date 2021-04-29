# Sportsbooks
##Approach we could take
- Find api calls made on different sites to retrieve odds [(as done here)](src/live_data/live_odds_retrieval.py), but much more optimally
- fuzzy string matching to find candidate pairs https://pypi.org/project/fuzzywuzzy/
- retrieve across books and compare prices to see which spreads are narrowest
- Value betting/modeling esoteric things (i.e. tipoffs). If the odds are expected to move cross market arbitrage may 
allow a proxy on something not even modeled by the exchanges (i.e. tip win probability)


### List of books
These have nba score first props bets (some only for player to score first)
- [Draftkings]()
- [Fanduel]()
- [BetMGM]()
- [Bovada]()
- [Barstool Sports]()
- [PointsBet]()
- [Unibet]()
- [Betfair]() (UK only)
  
Other exchanges you can find on lists like these that talk about different sportsbook. https://pasportsbooks.com/


###Automatic arbitrage finders:
- summary list https://thearbacademy.com/best-arbitrage-betting-software/
- Just search and more should come up

### Sportsbook Regulations

- Sportsbooks have regional restrictions, they vary from country to country and region/state
- Many sportsbooks will share a common data provider, common parent company or common set of odds.
  So it's important to understand if 2 books could be paired.
- Sportsbooks can/will kick you off for violating their terms of service
- Arbitrage betting is a reason to kick you off (I believe, policies aren't explicit so I read a bunch of stuff British people said)
- Violating the "one account, one user" policy is another reason to kick you off
- **Coordinating with a cabal/syndicate to get around bet sizing limits is against the terms of service, even if the bets are made independently**
- There are payout limits on props bets. For drafkings that is set at $20,000, but it likely varies based on exchange.
  With experience having placed bets, I have yet to hit limits on betmgm or draftkings (betting as much as $1000) while on fanduel and bovada I have yet to hit any limits.
  
- I've also placed a decent number of arbitrage bets among various value-based bets and have yet to be limited or kicked off platform.


# Prediction Markets
- [Predictit](https://www.predictit.org/)
- [Polymarket](https://polymarket.com/)
- [Catnip](https://catnip.exchange/)
- [Omen](https://www.augur.net/)
- [Augur](https://www.augur.net/)
- [prediqt](https://prediqt.com/)
- [Degens](https://degens.com/) *may only be sports right now
- [Smarkets](https://smarkets.com/politics/)

Hadn't looked at these since election ended but seems like there is hardly any liquidity now, so possibly not worth any time

##Approach we could take
- Same as sportsbooks basically, but also with opportunities to be market makers and/or liquidity provider

###Other links
https://arbers.org/popular-sports-arbing/
https://www.oddsportal.com/sure-bets/
https://mollybet.com/

# Repos
- Live PI tracker https://github.com/Talophex/PITA
- Gaussian processes PI https://github.com/keyonvafa/gp-predictit-blog
- wrapper for PI API https://github.com/stephengardner/pyredictit
- PI vs. 538 https://github.com/mauricebransfield/predictit_538_odds
- Twitter sentiment analysis https://github.com/anthonyebiner/Twitter-Sentiment-Analysis
- Polymarket api wrapper https://github.com/anthonyebiner/PolyPython
- PI Discord (I forked this) https://github.com/EllAchE/PredictitDiscordNew


------------
NEW data source:
https://us.888sport.com/