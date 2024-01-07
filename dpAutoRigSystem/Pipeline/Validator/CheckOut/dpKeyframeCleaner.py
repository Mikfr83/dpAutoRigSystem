# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass

# global variables to this module:
CLASS_NAME = "KeyframeCleaner"
TITLE = "v040_keyframeCleaner"
DESCRIPTION = "v041_keyframeCleanerDesc"
ICON = "/Icons/dp_keyframeCleaner.png"

DP_KEYFRAMECLEANER_VERSION = 1.1


class KeyframeCleaner(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False)
        if toCheckList:
            # get animation node list
            animCurveList = cmds.ls(type="animCurve")
            if animCurveList:
                animatedList = []
                for animCrv in animCurveList:
                    connectionList = cmds.ls(cmds.listConnections(animCrv), type=["transform", "blendShape", "nonLinear"])
                    if connectionList and not connectionList[0] in animatedList:
                        animatedList.append(connectionList[0])
                if animatedList:
                    progressAmount = 0
                    maxProcess = len(animatedList)
                    for item in animatedList:
                        if self.verbose:
                            # Update progress window
                            progressAmount += 1
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                        if item in toCheckList:
                            if cmds.objExists(item):
                                crvList = cmds.listConnections(item, source=True, destination=False, type="animCurve") #blendWeighted/pairBlend
                                if crvList:
                                    foundKey = False
                                    for crv in crvList:
                                        # conditional to check here
                                        if len(cmds.listConnections(crv, source=True)) >= 2:
                                            pass #drivenKey
                                        else: #normal key
                                            foundKey = True
                                            break
                                    if foundKey:
                                        self.checkedObjList.append(item)
                                        self.foundIssueList.append(True)
                                        if self.verifyMode:
                                            self.resultOkList.append(False)
                                        else: #fix
                                            reported = False
                                            for crv in crvList:
                                                if len(cmds.listConnections(crv, source=True)) < 2:
                                                    try:
                                                        # delete animation curve (keyframe)
                                                        cmds.delete(crv)
                                                        if not reported:
                                                            self.resultOkList.append(True)
                                                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                                                            reported = True
                                                    except:
                                                        if not reported:
                                                            self.resultOkList.append(False)
                                                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                                                            reported = True
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
