from src.database.data_update import smallDataUpdate, updateLongTermData

'''
The following data will be updated when calling each method:

updateLongTermData():
    1. Saves a proxy of a relational database to connect player names to codes on basketball reference, their nicknames etc.
    2. Updates database of past and current teams that all nba players since 1997 have played for
    
smallDataUpdate():
    1. Adds the results of all games played since last game
    2. Recalculates the trueskill values of all tipoff participants
    3. Gets playbyplay data for all games.
    4. Creates a dictionary with metadata on over/underperformance of each team historically based on a set probability of scoring first when winning tipoff
'''

# updateLongTermData()
smallDataUpdate()