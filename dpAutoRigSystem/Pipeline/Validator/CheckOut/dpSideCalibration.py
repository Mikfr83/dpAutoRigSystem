# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass

# global variables to this module:
CLASS_NAME = "SideCalibration"
TITLE = "v044_sideCalibration"
DESCRIPTION = "v045_sideCalibrationDesc"
ICON = "/Icons/dp_sideCalibration.png"

DP_SIDECALIBRATION_VERSION = 1.2


class SideCalibration(dpBaseValidatorClass.ValidatorStartClass):
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
            toCheckList = self.dpUIinst.ctrls.getControlList()
        if toCheckList:
            pairDic = {}
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                # conditional to check here
                if cmds.objExists(item+".calibrationList"):
                    if item[1] == "_": #side: because L_CtrlName or R_CtrlName have "_" as second letter.
                        foundOtherSide = False
                        for node in toCheckList:
                            if node[2:] == item[2:]: #other side found
                                pairDic[item] = node
                                foundOtherSide = True
                                break
                        if foundOtherSide:
                            calibrationAttr = cmds.getAttr(item+".calibrationList")
                            if calibrationAttr:
                                calibrationList = calibrationAttr.split(";")
                                if calibrationList:
                                    for attr in calibrationList:
                                        if cmds.objExists(item+"."+attr) and cmds.objExists(pairDic[item]+"."+attr):
                                            # current values
                                            itemCurrentValue = float(format(cmds.getAttr(item+"."+attr),".3f"))
                                            pairCurrentValue = float(format(cmds.getAttr(pairDic[item]+"."+attr),".3f"))
                                            if not itemCurrentValue == pairCurrentValue:
                                                # found issue here
                                                self.checkedObjList.append(item+"."+attr)
                                                self.foundIssueList.append(True)
                                                if self.verifyMode:
                                                    self.resultOkList.append(False)
                                                else: #fix
                                                    try:
                                                        # default values (supposed to be the same for the two sides)
                                                        itemDefaultValue = float(format(cmds.addAttr(item+"."+attr, query=True, defaultValue=True),".3f"))
                                                        if pairCurrentValue == itemDefaultValue:
                                                            # pair current value is equal to its default value, so we set the pair value as item current value
                                                            cmds.setAttr(pairDic[item]+"."+attr, itemCurrentValue)
                                                        else:
                                                            # check for left, top or front side to use it as priority node:
                                                            if item[0] == self.dpUIinst.lang['p002_left'] or item[0] == self.dpUIinst.lang['p004_top'] or item[0] == self.dpUIinst.lang['p006_front']:
                                                                cmds.setAttr(pairDic[item]+"."+attr, itemCurrentValue)
                                                            else:
                                                                cmds.setAttr(item+"."+attr, pairCurrentValue)
                                                        self.resultOkList.append(True)
                                                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+"."+attr)
                                                    except:
                                                        self.resultOkList.append(False)
                                                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item+"."+attr)
                                        else:
                                            self.resultOkList.append(True)
                                            self.messageList.append(item+"."+attr+" "+self.dpUIinst.lang['i061_notExists'])
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
