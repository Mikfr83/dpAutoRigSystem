# importing libraries:
from maya import cmds
from maya import mel
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "NonManifoldCleaner"
TITLE = "v101_nonManifoldCleaner"
DESCRIPTION = "v102_nonManifoldCleanerDesc"
ICON = "/Icons/dp_nonManifoldCleaner.png"

DP_NONMANIFOLDCLEANER_VERSION = 1.0


class NonManifoldCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_NONMANIFOLDCLEANER_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                geoToCleanList = objList
            else:
                geoToCleanList = cmds.ls(list(set(self.checkNonManifold(self.getMeshTransformList()))), long=False)
            if geoToCleanList:
                self.utils.setProgress(max=len(geoToCleanList), addOne=False, addNumber=False)
                for geo in geoToCleanList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    if cmds.objExists(geo):
                        self.checkedObjList.append(geo)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.select(geo)
                                # Cleanup non manifolds
                                mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+geo)
                                mel.eval('changeSelectMode -object;')
                                cmds.select(clear=True)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+geo)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def checkNonManifold(self, itemList, *args):
        """ Verify if there are non manifold meshes and return them if exists.
        """
        nonManifoldList = []
        if itemList:
            for item in itemList:
                if cmds.polyInfo(item, nonManifoldEdges=True, nonManifoldUVEdges=True, nonManifoldUVs=True, nonManifoldVertices=True):
                    nonManifoldList.append(item)
        return nonManifoldList
