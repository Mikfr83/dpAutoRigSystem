# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "UnlockNormals"
TITLE = "v078_unlockNormals"
DESCRIPTION = "v079_unlockNormalsDesc"
ICON = "/Icons/dp_unlockNormals.png"

DP_UNLOCKNORMALS_VERSION = 1.2


class UnlockNormals(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_UNLOCKNORMALS_VERSION
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
                allMeshList = objList
            else:
                allMeshList = cmds.ls(selection=False, type='mesh')
            if allMeshList:
                self.utils.setProgress(max=len(allMeshList), addOne=False, addNumber=False)
                for mesh in allMeshList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    if cmds.objExists(mesh):
                        lockedList = cmds.polyNormalPerVertex(mesh+".vtx[*]", query=True, freezeNormal=True)
                        # check if there's any locked normal
                        if True in lockedList:
                            self.checkedObjList.append(mesh)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    cmds.polyNormalPerVertex(mesh+".vtx[*]", unFreezeNormal=True)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+mesh)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+mesh)
        
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