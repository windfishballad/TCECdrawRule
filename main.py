import chess.pgn
import numpy as np

import drawRuleTester

#pgn=open("/home/david/events/myData.pgn")
pgn=open("/home/david/Matches/testDrawRule.pgn")
isTCECEval=False

drawRules=[]
'''

'''

drawRules.append(drawRuleTester.drawRule(eval=0.25,maxNonPawnMaterial=8,maxPawnMaterial=8,nPlies=10)) #Current default draw rule
drawRules.append(drawRuleTester.drawRule(eval=0.25,maxWeightedMaterial=30,nPlies=6))





visitor=drawRuleTester.Visitor(drawRules,isTCECEval)

plies=[]
falseAlerts=[]
correctlyTriggered=[]
games=0
draws=0
wins=0
drawsPliesSaved=[]
badData=0
crash=0
falseAlertsByEvent={}

while True:
    game = chess.pgn.read_game(pgn)

    if game is not None:
        game.accept(visitor)
        games+=1
        if(games%100==0):
            print(games)

        #if not (game.headers.get("TerminationDetails")=="White disconnects" or game.headers.get("TerminationDetails")=="Black disconnects" or game.headers.get("TerminationDetails")=="Manual adjudication"):
        if not False:

            result=game.headers.get("Result")
            if (result=="1-0") or (result=='0-1'):
                wins+=1
                falseAlerts.append(visitor.triggered)
                if visitor.triggered[0]:
                    pass
                    #print(game.headers.get("Event"))
                    #print(game.headers.get("Round"))
                    #print(game.headers.get("TerminationDetails"))
                    #print(visitor.plyNumber)
                    #print(visitor.ply)
                if visitor.triggered[1]:
                    event=game.headers.get("Event")
                    if event in falseAlertsByEvent:
                        falseAlertsByEvent[event]+=1
                    else:
                        falseAlertsByEvent[event]=1

                    #print(game.headers.get("Event"))
                    #print(game.headers.get("Round"))
                    #print(visitor.plyNumber)

                correctlyTriggered.append(np.zeros(len(drawRules)))
                drawsPliesSaved.append(np.zeros(len(drawRules)))
            else:
               # if visitor.triggered[0] and (visitor.ply-visitor.plyNumber[0]>0):
                if False:
                    badData+=1
                else:
                    falseAlerts.append(np.zeros(len(drawRules)))
                    draws+=1
                    drawsPliesSaved.append(visitor.triggered*(visitor.ply-visitor.plyNumber))
                    correctlyTriggered.append(visitor.triggered)

        else:
            crash+=1



    else:
        break

falseAlerts=np.array(falseAlerts)
drawsPliesSaved=np.array(drawsPliesSaved)
correctlyTriggered=np.array(correctlyTriggered)
refRuleTriggered=correctlyTriggered[:,0].reshape((correctlyTriggered.shape[0],1))
triggeredBeforeDrawRule=refRuleTriggered*correctlyTriggered
triggeredAlone=(1-refRuleTriggered)*correctlyTriggered
#drawsByDrawRule=np.sum(refRuleTriggered)
#otherDraws=draws-drawsByDrawRule

print(games)
#print(badData+crash+wins+draws)
print(badData)
#print(crash)
print(wins)
print(draws)
print(drawsByDrawRule)
print(otherDraws)

print(np.sum(falseAlerts,axis=0))
print(np.sum(falseAlerts,axis=0)/wins)
print(np.sum(drawsPliesSaved,axis=0)/draws)
print(np.max(drawsPliesSaved,axis=0))
print(np.percentile(drawsPliesSaved,(100*wins+95*draws)/(draws+wins),axis=0))
print(np.sum(correctlyTriggered,axis=0)/draws)
#print(np.sum(triggeredBeforeDrawRule,axis=0)/drawsByDrawRule)
#print(np.sum(drawsPliesSaved*triggeredBeforeDrawRule,axis=0)/drawsByDrawRule)
#print(np.sum(triggeredAlone,axis=0)/otherDraws)
#print(np.sum(triggeredAlone*drawsPliesSaved,axis=0)/otherDraws)

#for event in falseAlertsByEvent:
    #print(event)
    #print(falseAlertsByEvent[event])
