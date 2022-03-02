import chess.pgn
import numpy as np
import math


def nonPawnMaterial(board):
    return 2+len(board.pieces(chess.QUEEN,chess.WHITE))+len(board.pieces(chess.ROOK,chess.WHITE))+len(board.pieces(chess.BISHOP,chess.WHITE))+len(board.pieces(chess.KNIGHT,chess.WHITE))+len(board.pieces(chess.QUEEN,chess.BLACK))+len(board.pieces(chess.ROOK,chess.BLACK))+len(board.pieces(chess.BISHOP,chess.BLACK))+len(board.pieces(chess.KNIGHT,chess.BLACK))

def pawnMaterial(board):
    return len(board.pieces(chess.PAWN,chess.BLACK))+len(board.pieces(chess.PAWN,chess.BLACK))

def parseEval(comment):


    eval=comment.split('/')[0]
    try:
        f=float(eval)
        return f
    except:
        return None

def parseEvalTCEC(comment):
    eval=comment.split(',')
    if eval[0].lstrip()=='book':
        return None

    for e in eval:
        f=e.lstrip().split("=")
        if f[0]=='wv':
            try:
                return float(f[1])
            except:
                return None

    return None




class drawRule:
    def __init__(self,reset=True,minMoveNumber=35,nPlies=10,maxNonPawnMaterial=32,maxPawnMaterial=16,maxTotalMaterial=32,eval=0.15,asymetric=False):
        self.reset=reset
        self.minMoveNumber=minMoveNumber
        self.nPlies=nPlies
        self.maxNonPawnMaterial=maxNonPawnMaterial
        self.maxPawnMaterial=maxPawnMaterial
        self.maxTotalMaterial=maxTotalMaterial
        self.eval=eval
        self.asymetric=asymetric




class Visitor(chess.pgn.BaseVisitor):

    def __init__(self,drawRules,isTCECEval=False):
        self.nRules=len(drawRules)
        self.reset=np.array([d.reset for d in drawRules])
        self.minMoveNumber=np.array([d.minMoveNumber for d in drawRules])
        self.nPlies=np.array([d.nPlies for d in drawRules])
        self.maxNonPawnMaterial=np.array([d.maxNonPawnMaterial for d in drawRules])
        self.maxPawnMaterial = np.array([d.maxPawnMaterial for d in drawRules])
        self.maxTotalMaterial=np.array([d.maxTotalMaterial for d in drawRules])
        self.eval=np.array([d.eval for d in drawRules])
        self.isTCECEval=isTCECEval
        self.asymetric=np.array([d.asymetric for d in drawRules])

    def begin_game(self):
        self.reInitialize()
        self.ply=-1


    def reInitialize(self):
        self.plyNumber=np.zeros(self.nRules)
        self.plyCounter=np.zeros(self.nRules)
        self.triggered=np.zeros(self.nRules)
        self.active=np.zeros(self.nRules)
        self.materialCondition=np.zeros(self.nRules)
        self.resetsNow=0



    def visit_comment(self,comment):
        eval=None
        if (self.isTCECEval):
            eval=parseEvalTCEC(comment)
            if eval is not None:
                eval=parseEvalTCEC(comment)*(2*(self.ply % 2)-1)
        else:
            eval=parseEval(comment)
        if eval is not None:
            self.active=self.asymetric*(eval<self.eval+1e-3)*self.materialCondition+(1-self.asymetric)*(abs(eval)<self.eval+1e-3)*self.materialCondition
        else:
            self.active=np.zeros(self.nRules)

        self.plyCounter=(1-self.resetsNow)*self.active*(self.plyCounter+1)

        triggers = (self.plyCounter >= self.nPlies)*(int(self.ply/2) >= self.minMoveNumber)

        self.plyNumber = self.triggered * self.plyNumber + (1 - self.triggered) * triggers * self.ply

        self.triggered = np.logical_or(self.triggered, triggers)

    def visit_board(self, board):

        self.ply += 1

        if not(np.sum(1-self.triggered)):
            return


        self.resetsNow=self.reset*(board.halfmove_clock==0)
        self.plyCounter=(1-self.resetsNow)*self.plyCounter

        if(np.sum(self.materialCondition) < self.nRules):
            nonPawnMat=nonPawnMaterial(board)
            pawnMat=pawnMaterial(board)
            totalMat=nonPawnMat+pawnMat
            self.materialCondition=(pawnMat<=self.maxPawnMaterial)*(nonPawnMat<=self.maxNonPawnMaterial) *(totalMat<=self.maxTotalMaterial)





    def result(self):
        return [self.triggered,self.plyNumber,self.ply]

