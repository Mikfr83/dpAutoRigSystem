# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass

# global variables to this module:
CLASS_NAME = "DuplicatedName"
TITLE = "v024_duplicatedName"
DESCRIPTION = "v025_duplicatedNameDesc"
ICON = "/Icons/dp_duplicatedName.png"

DP_DUPLICATEDNAME_VERSION = 1.2


class DuplicatedName(dpBaseValidatorClass.ValidatorStartClass):
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
            toCheckList = cmds.ls(selection=False, long=False)
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            foundDuplicated = False
            for node in toCheckList:
                if "|" in node:
                    foundDuplicated = True
                    break
            if foundDuplicated:
                # analisys the elements in the allObjectList in order to put it with ordenation from children to grandfather (inverted hierarchy)
                sizeList = []
                orderedObjList = []
                for i, element in enumerate(toCheckList):
                    # find the number of ocorrences of "|" in the string (element)
                    number = element.count("|")
                    # add to a list another list with number and element
                    sizeList.append([number, element])
                # sort (put in alphabetic order to A-Z) and reverse (invert the order to Z-A)
                sizeList.sort()
                sizeList.reverse()
                # add the elements to the final orderedObjList
                for n, value in enumerate(sizeList):
                    orderedObjList.append(sizeList[n][1])
                # prepare a list with nodeNames to iteration
                shortNameList = []
                for longName in orderedObjList:
                    # verify if there are childrens in order to get the shortNames
                    if "|" in longName:
                        shortNameList.append(longName[longName.rfind("|")+1:])
                    else:
                        shortNameList.append(longName)
                # compare each obj in the list with the others, deleting it from the original list in order to avoid compare itself
                n = 0
                for i, obj in enumerate(shortNameList):
                    if self.verbose:
                        # Update progress window
                        progressAmount += 1
                        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                    # use another list without the first element to compare it the item repeats
                    anotherList = shortNameList[i+1:]
                    for item in anotherList:
                        if cmds.objExists(orderedObjList[i]):
                            if obj == item:
                                # found issue here
                                self.checkedObjList.append(orderedObjList[i])
                                self.foundIssueList.append(True)
                                if self.verifyMode:
                                    self.resultOkList.append(False)
                                else: #fix
                                    try:
                                        cmds.rename(orderedObjList[i], obj+str(n))
                                        n += 1
                                        self.resultOkList.append(True)
                                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+orderedObjList[i])
                                    except:
                                        self.resultOkList.append(False)
                                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+orderedObjList[i])
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
