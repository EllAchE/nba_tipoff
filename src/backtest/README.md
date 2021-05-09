# Backtest

Specify a season (only 2021 has odds currently) and given prior knowledge
on the game, make a prediction (with only data known before hand). Then use the data from after the
game to evaluate the effect of this prediction on a base position (will start from zero and can go postive or negative)
Store daily results (evaluate batches of games that occur on a single day).

To use for all test, create a csv with columns:
1. Gamecode
2. Quarter results
3. Odds for all exchanges
4. Tippers
5. Tipper trueskill/elo/glicko prior to tipoff
6. Single-season team over/underperformance metadata


For an individual backtest the end result should be:
1. Game by game CSV with:
   - Best odds,
   - amount bet by Kelly
   - rounded amount
    - Outcome
    - Team
    - Exchange
    - Net position effect
2. a daily frequency dataset with
3. Summary stats such as:
   - max drawdown
   - max up
   - overall correct prediction %
    - Odds segmented performance
    - exchange segmented performance
    

The backtest should be configurable by:
1. flat amount bet
2. kelly bet with static and dynamic bankroll
3. minimum evaluation period
4. Odds prediction method (i.e. tip only, )