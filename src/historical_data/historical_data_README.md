# Historical Data Retrieval

A large variety of data can be retrieved with scripts in this repo, though only a
small percentage of data I wrote scripts for is actually in use at any point.

####Data in use:
- Play-by-play scoring data by team and player
- Tipoff W/L records by player

####Data not in use:
- Basically any possible stat, i.e.
- FG%
- Plus Minus By Quarter
- Rebound rate
- W/L record
- Individual player usage rate (how often they shoot vs. others on the team)

###How to retrieve data

Basically any data can be retrieved from the excellent [nba_api](https://github.com/swar/nba_api), a wrapper around nba.com's unauthenticated api with great documentation.
However, when I wrote this initially I was lazy and instead set up a scraper for [basketball-reference.com](https://www.basketball-reference.com/) and their historical data, which wasn't worth replacing.

The script [run_data_update.py](../../run_data_update.py) updates the data use for live betting. See script for more detail.

If you are looking for data outside the play-by-play and tipoff results (see sample
[pbp](../../Data/) and [tipoff data](../../Data/CSV/season_data/tipoff_and_first_score_details_2014_season.csv)) then use the nba_api.
Some data is already being retrieved from there (i.e. [playbyplay data](nba_play_by_play_methods.py)).

The data used in a brief attempt at implementing the XGBoost algorithm are in this [sample csv](../../Data/CSV/ml_columns/all_ml_cols.csv).

######List of data endpoints offered in nba api (just look at their repo)

- alltimeleadersgrids.md
 
- assistleaders.md
 
- assisttracker.md
 
- boxscoreadvancedv2.md
 
- boxscoredefensive.md
 
- boxscorefourfactorsv2.md
 
- boxscorematchups.md
 
- boxscoremiscv2.md
 
- boxscoreplayertrackv2.md
 
- boxscorescoringv2.md
 
- boxscoresimilarityscore.
 
- boxscoresummaryv2.md
 
- boxscoretraditionalv2.md
 
- boxscoreusagev2.md
 
- commonallplayers.md
 
- commonplayerinfo.md
 
- commonplayoffseries.md
 
- commonteamroster.md
 
- commonteamyears.md
 
- cumestatsplayer.md
 
- cumestatsplayergames.md
 
- cumestatsteam.md
 
- cumestatsteamgames.md
 
- defensehub.md
 
- draftboard.md
 
- draftcombinenonstationar
 
- draftcombineplayeranthro
 
- draftcombinespotshooting
 
- draftcombinestats.md
 
- drafthistory.md
 
- fantasywidget.md
 
- franchisehistory.md
 
- franchiseleaders.md
 
- franchiseplayers.md
 
- gamerotation.md
 
- glalumboxscoresimilarity
 
- homepageleaders.md
 
- homepagev2.md
 
- hustlestatsboxscore.md
 
- infographicfanduelplayer
 
- leaderstiles.md
 
- leaguedashlineups.md
 
- leaguedashoppptshot.md
 
- leaguedashplayerbiostats
 
- leaguedashplayerclutch.m
 
- leaguedashplayerptshot.m
 
- leaguedashplayershotloca
 
- leaguedashplayerstats.md
 
- leaguedashptdefend.md
 
- leaguedashptstats.md
 
- leaguedashptteamdefend.m
 
- leaguedashteamclutch.md
 
- leaguedashteamptshot.md
 
- leaguedashteamshotlocati
 
- leaguedashteamstats.md
 
- leaguegamefinder.md
 
- leaguegamelog.md
 
- leaguehustlestatsplayer.
 
- leaguehustlestatsplayerl
 
- leaguehustlestatsteam.md
 
- leaguehustlestatsteamlea
 
- leagueleaders.md
 
- leaguelineupviz.md
 
- leagueplayerondetails.md
 
- leagueseasonmatchups.md
 
- leaguestandings.md
 
- leaguestandingsv3.md
 
- matchupsrollup.md
 
- playbyplay.md
 
- playbyplayv2.md
 
- playerawards.md
 
- playercareerbycollege.md
 
- playercareerbycollegerol
 
- playercareerstats.md
 
- playercompare.md
 
- playerdashboardbyclutch.
 
- playerdashboardbygamespl
 
- playerdashboardbygeneral
 
- playerdashboardbylastnga
 
- playerdashboardbyopponen
 
- playerdashboardbyshootin
 
- playerdashboardbyteamper
 
- playerdashboardbyyearove
 
- playerdashptpass.md
 
- playerdashptreb.md
 
- playerdashptshotdefend.m
 
- playerdashptshots.md
 
- playerestimatedmetrics.m
 
- playerfantasyprofile.md
 
- playerfantasyprofilebarg
 
- playergamelog.md
 
- playergamelogs.md
 
- playergamestreakfinder.m
 
- playernextngames.md
 
- playerprofilev2.md
 
- playervsplayer.md
 
- playoffpicture.md
 
- scoreboard.md
 
- scoreboardv2.md
 
- shotchartdetail.md
 
- shotchartleaguewide.md
 
- shotchartlineupdetail.md
 
- synergyplaytypes.md
 
- teamandplayersvsplayers.
 
- teamdashboardbyclutch.md
 
- teamdashboardbygamesplit
 
- teamdashboardbygeneralsp
 
- teamdashboardbylastngame
 
- teamdashboardbyopponent.
 
- teamdashboardbyshootings
 
- teamdashboardbyteamperfo
 
- teamdashboardbyyearovery
 
- teamdashlineups.md
 
- teamdashptpass.md
 
- teamdashptreb.md
 
- teamdashptshots.md
 
- teamdetails.md
 
- teamestimatedmetrics.md
 
- teamgamelog.md
 
- teamgamelogs.md
 
- teamgamestreakfinder.md
 
- teamhistoricalleaders.md
 
- teaminfocommon.md
 
- teamplayerdashboard.md
 
- teamplayeronoffdetails.m
 
- teamplayeronoffsummary.m
 
- teamvsplayer.md
 
- teamyearbyyearstats.md
 
- videodetails.md
 
- videoevents.md
 
- videostatus.md
 
- winprobabilitypbp.md
 