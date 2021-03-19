from src.database.data_update import customDataUpdate

# customDataUpdate()
from src.live_data.display_bets import getAllOddsAndDisplayByEv

getAllOddsAndDisplayByEv(getFanduelTomorrow=True, getFanduelToday=True)