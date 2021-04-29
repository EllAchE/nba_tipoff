# Skill Algorithms
3 different skill algorithms for calculating player skill at tipoffs
are implemented in this project, and their performance has been
compared (without a grid search/automated hyperparameter tuning) based on log-loss.These are:

All skill algorithms allow for the possibility of ties, set this probability to zero for binary outcomes.

###Elo

Earliest skill algorithm, easy to compute and widely used/known. Downside is there is no certainty
factor and it takes much longer to converge, i.e. elo recommends the use of a "rating period". 1v1 only.

###Trueskill

The original trueskill algorithm was open sourced by Microsoft, trueskill2 is still proprietary.
Trueskill is similar to the glicko algorithm, however it extends glicko to be applicable to mulitplayer competitions.


###Glicko2
An improvement on the Elo rating system to account for increased certainty of players who have played more games,
vs. players who are new. 1v1 only.

####Resources
The math behind each of these is actually quite important to how they work but would take a very long time to explain.
See the references for each for more detail:

- https://en.wikipedia.org/wiki/Elo_rating_system

- https://trueskill.org/

- http://glicko.net/glicko/glicko2.pdf
