# FittingProblemMultipleCondition.py
#
# Bryan Daniels
# 8.25.2015
#
# Setup for fitting datasets taken under multiple experimental conditions.
# The goal is to find a single model structure that best fits all conditions,
# while the parameters used to fit each condition vary.
#

from FittingProblem import *

class FittingProblemMultipleCondition(FittingProblem):
    """
    Setup for fitting datasets taken under multiple experimental conditions.
    The goal is to find a single model structure that best fits all conditions,
    while the parameters used to fit each condition vary.
    
    A FittingProblemMultipleCondition object can be used in many cases
    like a usual FittingProblem.  Exceptions to this: 
        -- Hessians and singular values are stored separately for each condition
           (within each FittingProblem in self.fittingProblemList).
        -- fittingData and indepParamsList are stored separately for each condition.
    
    fittingDataMultiple                     : List of fittingData, with length equal
                                              to the number of conditions.  Each
                                              fittingData object should be in the format
                                              used by a usual FittingProblem.
    indepParamsListMultiple (None)          : List of indepParamsLists, with length equal
                                              to the number of conditions.  Each 
                                              indepParamsList should be in the format
                                              used by a usual FittingProblem.
    
    Other kwargs are the same as a usual FittingProblem.
    """
    def __init__(self,fittingDataMultiple,fittingModelList,
                 indepParamsListMultiple=None,saveFilename=None,
                 saveKey=-1,**kwargs):

        if indepParamsListMultiple is None:
            indepParamsListMultiple = [ [[]] for fd in fittingDataMultiple ]

        # Each condition gets a separate fittingProblem.  These are stored in
        # self.fittingProblemList.
        self.fittingProblemList = [ \
            FittingProblem(fittingData,fittingModelList,
                                          indepParamsList=indepParamsList,
                                          **kwargs) \
            for fittingData,indepParamsList in \
                zip(fittingDataMultiple,indepParamsListMultiple) ]
            
        # all daughter classes should call generalSetup
        self.generalSetup(saveFilename,saveKey)

    def generalSetup(self,saveFilename=None,saveKey=-1):
        self.costDict = {}
        self.penaltyDict = {}
        self.numParametersDict = {}
        self.logLikelihoodDict = {}
        self.fitAllDone = False
        self.saveFilename = saveFilename
        self.saveKey = saveKey
        self.pid = os.getpid()

        # inherit constant attributes from first fittingProblem
        f = self.fittingProblemList[0]
        self.fittingModelNames = f.fittingModelNames
        self.indepParamNames = f.indepParamNames
        self.cutoff = f.cutoff
        self.verbose = f.verbose
        self.perfectModel = f.perfectModel
        self.perfectParams = f.perfectParams
        self.stopFittingN = f.stopFittingN

    def fitAll(self,**kwargs):
        """
        See documentation for FittingProblem.fitAll.
        """
        
        # Loop over complexity
        for i,name in enumerate(self.fittingModelNames):
            
            # For each condition, fit model of the given complexity
            costMultiple = 0.
            penaltyMultiple = 0.
            for fittingProblem in self.fittingProblemList:
                fittingProblem.fitAll(maxNumFit=i+1,**kwargs)
                costMultiple += fittingProblem.costDict[name]
                penaltyMultiple += fittingProblem.penaltyDict[name]
            
                # *******************************************************
                print "single condition cost: ",fittingProblem.costDict[name]
                # *******************************************************
            # *******************************************************
            print "total cost: ",costMultiple
            # *******************************************************
    
            # Record total cost and penalty
            self.costDict[name] = costMultiple
            self.penaltyDict[name] = penaltyMultiple
            self.logLikelihoodDict[name] = -(costMultiple + penaltyMultiple)
            self.numParametersDict = self.fittingProblemList[0].numParametersDict
    
            # Check whether we're done
            # 6.1.2012 stop after seeing stopFittingN models with worse logLikelihood
            orderedLs = []
            if not hasattr(self,'stopFittingN'):
                self.stopFittingN = 3
            for n in self.fittingModelNames:
                if self.logLikelihoodDict.has_key(n):
                    orderedLs.append(self.logLikelihoodDict[n])
            if (len(orderedLs) > self.stopFittingN):
                if max(orderedLs[-self.stopFittingN:]) < max(orderedLs):
                    self.fitAllDone = True
                    return

        self.fitAllDone = True
    
    def fitPerfectModel(self,**kwargs):
        for fittingProblem in self.fittingProblemList:
            fittingProblem.fitPerfectModel(**kwargs)

    def numStiffSingVals(self,**kwargs):
        raise Exception, "Not implemented"
    
    def _StiffSingVals(self,**kwargs):
        raise Exception, "Not implemented"
    
    def _UpdateDicts(self,name):
        raise Exception, "Not implemented"
    
    def plotResults(self,**kwargs):
        """
        See documentation for FittingProblem.plotResults.
        """
        for fittingProblem in self.fittingProblemList:
            fittingProblem.plotResults(**kwargs)

    def correlationWithPerfectModel(self,**kwargs):
        raise Exception, "Not implemented"

    def outOfSampleCorrelation(self,**kwargs):
        raise Exception, "Not implemented"

    def calculateAllOutOfSampleCorrelation(self,**kwargs):
        raise Exception, "Not implemented"

    def getBestModel(self,modelName=None,maxIndex=-4,**kwargs):
        if modelName is None:
            modelName = self.maxLogLikelihoodName(maxIndex=maxIndex)
        bestModelList = [ f.fittingModelDict[modelName] for f in self.fittingProblemList ]
        return bestModelList

    def plotBestModelResults(self,modelName=None,maxIndex=-4,**kwargs):
        if modelName is None:
            modelName = self.maxLogLikelihoodName(maxIndex=maxIndex)
        returnList = []
        for fittingProblem in self.fittingProblemList:
            Plotting.figure()
            m = fittingProblem.fittingModelDict[modelName]
            returnList.append( fittingProblem.plotModelResults(m,**kwargs) )
        return returnList

    def _fixOldVersion(self):
        raise Exception, "Not implemented"


class PowerLawFittingProblemMultipleCondition(FittingProblemMultipleCondition):
    """
    See documentation for FittingProblemMultipleCondition.
    
    kwargs same as PowerLawFittingProblem.
    """
    
    def __init__(self,complexityList,fittingDataMultiple,indepParamsListMultiple=None,
                 saveFilename=None,saveKey=-1,**kwargs):

        if indepParamsListMultiple is None:
            indepParamsListMultiple = [ [[]] for fd in fittingDataMultiple ]

        # Each condition gets a separate fittingProblem.  These are stored in
        # self.fittingProblemList.
        self.fittingProblemList = [ \
            PowerLawFittingProblem(complexityList,fittingData,
                                                  indepParamsList=indepParamsList,
                                                  **kwargs) \
            for fittingData,indepParamsList in \
                zip(fittingDataMultiple,indepParamsListMultiple) ]

        # all daughter classes should call generalSetup
        self.generalSetup(saveFilename,saveKey)

    def networkFigureBestModel(self,filenameMultiple,maxIndex=-4,modelName=None,
                               **kwargs):
        """
        Make one network figure for each condition.
        See documentation for FittingProblem.PowerLawFittingProblem.networkFigureBestModel.
        
        filenameMultiple        : A list of filenames, one for each condition.
        """
        if modelName is None:
            modelName = self.maxLogLikelihoodName(maxIndex=maxIndex)
        return [ fp.networkFigureBestModel(filename,modelName=modelName,**kwargs) \
                 for fp,filename in zip(self.fittingProblemList,filenameMultiple) ]

    def outOfSampleCorrelation_deriv(self,**kwargs):
        raise Exception, "Not implemented"


class CTSNFittingProblemMultipleCondition(FittingProblemMultipleCondition):
    """
    See documentation for FittingProblemMultipleCondition.
    
    kwargs same as CTSNFittingProblem.
    """
    
    def __init__(self,complexityList,fittingDataMultiple,indepParamsListMultiple=None,
                 saveFilename=None,saveKey=-1,**kwargs):
        
        if indepParamsListMultiple is None:
            indepParamsListMultiple = [ [[]] for fd in fittingDataMultiple ]
        
        # Each condition gets a separate fittingProblem.  These are stored in
        # self.fittingProblemList.
        self.fittingProblemList = [ \
           CTSNFittingProblem(complexityList,fittingData,
                                                 indepParamsList=indepParamsList,
                                                 **kwargs) \
           for fittingData,indepParamsList in \
                zip(fittingDataMultiple,indepParamsListMultiple) ]
           
        # all daughter classes should call generalSetup
        self.generalSetup(saveFilename,saveKey)

    def networkFigureBestModel(self,filenameMultiple,maxIndex=-4,modelName=None,
                               **kwargs):
        """
        Make one network figure for each condition.
        See documentation for FittingProblem.CTSNFittingProblem.networkFigureBestModel.
        
        filenameMultiple        : A list of filenames, one for each condition.
        """
        if modelName is None:
            modelName = self.maxLogLikelihoodName(maxIndex=maxIndex)
        return [ fp.networkFigureBestModel(filename,modelName=modelName,**kwargs) \
                 for fp,filename in zip(self.fittingProblemList,filenameMultiple) ]
