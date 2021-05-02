from src.database.database_access import getUniversalPlayerName, getPlayerCurrentTeam, getTeamIDFromShortCode

def testGetUniversalPlayerName():
    assert getUniversalPlayerName("John Collins") == "johncollins"
    assert getUniversalPlayerName("jOhn'Co-llins") == "johncollins"
    assert getUniversalPlayerName("Marvin Bagley III") == "marvinbagleyiii"
    assert getUniversalPlayerName("Green,Jeff") == "jeffgreen"

def testGetPlayerCurrentTeam():
    assert getPlayerCurrentTeam("carislevert") == "IND"

def testGetTeamIDFromShortCode():
    teamDict = getTeamIDFromShortCode("ATL")
    assert teamDict == 1610612737

def testSys

