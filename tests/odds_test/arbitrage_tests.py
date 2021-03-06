from src.odds.odds_calculator import sysEMainDiagonalVarsNeg1Fill, getArbitrageRatiosTwoLines, \
    checkForArbitrageAnyNumberOfLines, americanToDecimal, americanToRatio
from src.utils import floatInexactZeroCheck, floatInexactZeroTwoNumberDiff


def sysEMainDiagonalVarsNeg1Fill_test():
    ratios = sysEMainDiagonalVarsNeg1Fill([2.0, 2.0])
    assert ratios[0] == ratios[1]

    ratios = sysEMainDiagonalVarsNeg1Fill([5, 10, 2, 1])
    assert ratios[0] > -11/5 and ratios[0] < -11/7
    assert ratios[1] < -0.9 and ratios[1] > -1.03
    assert ratios[2] < -11/3.1 and ratios[2] > -11/2.9

    ratios = sysEMainDiagonalVarsNeg1Fill([4.0, 5.0])
    assert ratios[0] > ratios[1]
    assert ratios[1] > 0

def getArbitrageRatiosTwoLines_test():
    ratios = getArbitrageRatiosTwoLines('-120', '+138')
    assert ratios[0] > ratios[1]
    assert ratios[0] > ratios[1] > 0
    assert ratios[1] == 100.
    assert ratios[0] > 120 and ratios[0] < 138
    assert floatInexactZeroCheck(( (ratios[0] % 120)/1.2 ) - ( 138 - ratios[0] ))#float math makes this inexact, testing near zero diff depending on winner

def checkForArbitrageAnyNumberOfLines_test():
    spread = checkForArbitrageAnyNumberOfLines('+650', '+850', '+1000', '+1500', '+2000')
    for item in spread:
        assert item > 0
    testCalc = floatInexactZeroTwoNumberDiff(6.5 * spread[0] - spread[-1],  20 * spread[-1] - spread[0])
    assert testCalc
    spread = checkForArbitrageAnyNumberOfLines('-110', '-110')
    assert not spread

def americanToDecimal_test():
    testPositiveOdds = '+500'
    testNegativeOdds = '-200'
    decimalPo = americanToDecimal(testPositiveOdds)
    decimalNe = americanToDecimal(testNegativeOdds)
    assert floatInexactZeroCheck(decimalPo - 6)
    assert floatInexactZeroCheck(decimalNe - 1.5)

    ratioPo = americanToRatio(testPositiveOdds)
    ratioNe = americanToRatio(testNegativeOdds)
    assert floatInexactZeroCheck(ratioPo - 5)
    assert floatInexactZeroCheck(ratioNe - 0.5)
