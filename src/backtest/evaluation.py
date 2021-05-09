from sklearn.metrics import log_loss


def customEvaluationMetrics(predictions, yTest):
    lenPred = len(predictions)
    totalMiss = 0
    expectedTotal = 0
    actualTotal = 0
    for i in range(0, lenPred-1):
        if yTest.iloc[i] == 1:
            totalMiss += 1 - predictions[i][1]
        elif yTest.iloc[i] == 0:
            totalMiss += predictions[i][0]
        else:
            raise ValueError("DDD")
        actualTotal += yTest.iloc[i]
        expectedTotal += predictions[i][1]

    logLoss = log_loss(yTest, predictions)

    print("Difference", totalMiss/lenPred)
    print('Expected', expectedTotal)
    print('Actual', actualTotal)
    print('bias?', expectedTotal/actualTotal)
    print("logLoss is", logLoss)