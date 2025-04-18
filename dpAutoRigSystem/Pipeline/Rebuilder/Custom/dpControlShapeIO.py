# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ControlShapeIO"
TITLE = "r014_controlShapeIO"
DESCRIPTION = "r015_controlShapeIODesc"
ICON = "/Icons/dp_controlShapeIO.png"

DP_CONTROLSHAPEIO_VERSION = 1.0


class ControlShapeIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONTROLSHAPEIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_controlShapeIO"
        self.startName = "dpControlShape"
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
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
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    ctrlList = None
                    if objList:
                        ctrlList = objList
                    else:
                        ctrlList = self.dpUIinst.ctrls.getControlList()
                    if ctrlList:
                        self.utils.setProgress(max=len(ctrlList), addOne=False, addNumber=False)
                        if self.firstMode: #export
                            try:
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                ctrlFileName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".ma"
                                self.dpUIinst.ctrls.exportShape(ctrlList, ctrlFileName, ui=False, verbose=True)
                                self.wellDoneIO(ctrlFileName)
                            except Exception as e:
                                self.notWorkedWellIO(', '.join(ctrlList)+": "+str(e))
                        else: #import
                            exportedList = self.getExportedList()
                            if exportedList:
                                try:
                                    exportedList.sort()
                                    ctrlsToImport = self.ioPath+"/"+exportedList[-1]
                                    self.dpUIinst.ctrls.importShape(ctrlList, ctrlsToImport, ui=False, verbose=True)
                                    self.wellDoneIO(exportedList[-1])
                                except Exception as e:
                                    self.notWorkedWellIO(exportedList[-1]+": "+str(e))
                            else:
                                self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                    else:
                        self.maybeDoneIO("Ctrls_Grp")
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic
