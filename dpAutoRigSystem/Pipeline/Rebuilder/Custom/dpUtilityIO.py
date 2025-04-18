# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "UtilityIO"
TITLE = "r054_utilityIO"
DESCRIPTION = "r055_utilityIODesc"
ICON = "/Icons/dp_utilityIO.png"

DP_UTILITYIO_VERSION = 1.0


class UtilityIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_UTILITYIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_utilityIO"
        self.startName = "dpUtility"
    

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
                    utilityList = None
                    if objList:
                        utilityList = objList
                    else:
                        utilityList = cmds.ls(selection=False, type=self.utils.utilityTypeList)
                    if self.firstMode: #export
                        if utilityList:
                            self.exportDicToJsonFile(self.getUtilityDataDic(utilityList))
                        else:
                            self.maybeDoneIO("Utility nodes.")
                    else: #import
                        utilityDic = self.importLatestJsonFile(self.getExportedList())
                        if utilityDic:
                            self.importUtilityData(utilityDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
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


    def getUtilityDataDic(self, utilityList, *args):
        """ Processes the given utility list to collect and mount the info data.
            Returns the dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(utilityList), addOne=False, addNumber=False)
        for item in utilityList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if not cmds.attributeQuery(self.dpID, node=item, exists=True) or not self.utils.validateID(item):
                # getting attributes values
                nodeType = cmds.objectType(item)
                dic[item] = {"attributes" : {},
                                "type"       : nodeType,
                                "name"       : item
                            }
                for attr in self.utils.typeAttrDic[nodeType]:
                    if cmds.attributeQuery(attr, node=item, exists=True):
                        dic[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                # compound attributes
                if nodeType in self.utils.typeMultiAttrDic.keys():
                    for multiAttr in self.utils.typeMultiAttrDic[nodeType].keys():
                        indexList = cmds.getAttr(item+"."+multiAttr, multiIndices=True)
                        if indexList:
                            dot = ""
                            attrList = [""]
                            if self.utils.typeMultiAttrDic[nodeType][multiAttr]:
                                dot = "."
                                attrList = self.utils.typeMultiAttrDic[nodeType][multiAttr]
                            for i in indexList:
                                for attr in attrList:
                                    attrName = multiAttr+"["+str(i)+"]"+dot+attr
                                    attrValue = cmds.getAttr(item+"."+attrName)
                                    dic[item]["attributes"][attrName] = attrValue
                                    if isinstance(attrValue, list):
                                        dic[item]["attributes"][attrName] = attrValue[0]
        return dic


    def importUtilityData(self, utilityDic, *args):
        """ Import utility nodes from exported dictionary.
            Create missing utility nodes and set them values if they don't exists.
        """
        self.utils.setProgress(max=len(utilityDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in utilityDic.keys():
            existingNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # create utility node if it needs
            if not cmds.objExists(item):
                cmds.createNode(utilityDic[item]["type"], name=utilityDic[item]["name"])
                # set attribute values
                if utilityDic[item]["attributes"]:
                    for attr in utilityDic[item]["attributes"].keys():
                        #if isinstance(attr, list): 
                        if str(utilityDic[item]["attributes"][attr]).count(",") > 1: #support vector attributes like color_Color
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr][0], utilityDic[item]["attributes"][attr][1], utilityDic[item]["attributes"][attr][2], type="double3")
                        else:
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr])
                wellImportedList.append(item)
            else:
                existingNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(self.latestDataFile)
        else:
            if existingNodesList:
                self.wellDoneIO(self.dpUIinst.lang['r032_notImportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))
