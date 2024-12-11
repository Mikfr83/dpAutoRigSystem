# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
import os

# global variables to this module:
CLASS_NAME = "VaccineCleaner"
TITLE = "v052_vaccineCleaner"
DESCRIPTION = "v053_vaccineCleanerDesc"
ICON = "/Icons/dp_vaccineCleaner.png"

DP_VACCINECLEANER_VERSION = 1.2


class VaccineCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_VACCINECLEANER_VERSION
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
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, type='script')
        if toCheckList:
            self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
            for item in toCheckList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                # conditional to check here
                scriptdata = cmds.scriptNode(item, beforeScript=True, query=True)
                #if "fuck_All_U" in scriptdata:
                if "_gene" in scriptdata:
                    self.checkedObjList.append(item)
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            cmds.delete(item)
                            path = cmds.internalVar(userAppDir=True)+"/scripts/"
                            vaccineList = ["vaccine.py", "vaccine.pyc"]
                            for vaccine in vaccineList:
                                if os.path.exists(path+vaccine):
                                    os.remove(path+vaccine)
                            if os.path.exists(path+"userSetup.py"):
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item+"\n    - "+path+"userSetup.py")
                            else:
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            cmds.select(clear=True)
                            self.resultOkList.append(True)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
