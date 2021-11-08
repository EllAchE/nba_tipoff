from src.database.database_access import getUniversalPlayerName, getPlayerCurrentTeam, getTeamIDFromShortCode

def getUniversalPlayerName_test():
    assert getUniversalPlayerName("John Collins") == "johncollins"
    assert getUniversalPlayerName("jOhn'Co-llins") == "johncollins"
    assert getUniversalPlayerName("Marvin Bagley III") == "marvinbagleyiii"
    assert getUniversalPlayerName("Green,Jeff") == "jeffgreen"

def getPlayerCurrentTeam_test():
    assert getPlayerCurrentTeam("carislevert") == "IND"

def getTeamIDFromShortCode_test():
    teamDict = getTeamIDFromShortCode("ATL")
    assert teamDict == 1610612737
