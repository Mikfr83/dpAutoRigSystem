# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ParentingIO"
TITLE = "r019_parentingIO"
DESCRIPTION = "r020_parentingIODesc"
ICON = "/Icons/dp_parentingIO.png"

DP_PARENTINGIO_VERSION = 1.0


class ParentingIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PARENTINGIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_parentingIO"
        self.startName = "dpParenting"
    

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
        if self.pipeliner.checkAssetContext():
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    transformList = None
                    if objList:
                        transformList = objList
                    else:
                        transformList = cmds.ls(selection=False, long=True, type="transform")
                    if transformList:
                        self.utils.setProgress(max=len(transformList), addOne=False, addNumber=False)
                        # define data to export
                        parentDic = self.getParentingDataDic(transformList)
                        parentDic.update(self.getBrokenIDDataDic())
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                            self.pipeliner.saveJsonFile(parentDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except Exception as e:
                            self.notWorkedWellIO(jsonName+": "+str(e))
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes'])
                else: #import
                    try:
                        self.exportedList = self.getExportedList()
                        if self.exportedList:
                            self.exportedList.sort()
                            parentDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                            if parentDic:
                                if self.importBrokenIDData(parentDic):
                                    self.importParentingData(parentDic) #double run to first put broken nodes in place
                                self.importParentingData(parentDic)
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    except Exception as e:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def reorderList(self, itemList, *args):
        """ Returns a list with high to low counting of '|' in the item list given. That means a descending order.
        """
        return sorted(itemList, key = lambda x: x.count("|"), reverse=True)


    def getParentingDataDic(self, transformList=None, *args):
        """ Return a filtered dictionary of parenting hierarchy of current scene nodes.
        """
        if not transformList:
            transformList = cmds.ls(selection=False, long=True, type="transform")
        filteredList = self.utils.filterTransformList(transformList, verbose=self.verbose, title=self.dpUIinst.lang[self.title])
        filteredList = self.reorderList(filteredList)
        return {"Parent" : filteredList}


    def importBrokenIDData(self, parentDic, *args):
        """ If there are broken nodes, we try to recreate them if needed.
            Return True if there are broken nodes.
        """
        if parentDic["BrokenID"]:
            self.utils.setProgress(max=len(parentDic["BrokenID"]), addOne=False, addNumber=False)
            for nodeType in parentDic["BrokenID"].keys():
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                for item in parentDic["BrokenID"][nodeType].keys():
                    if not cmds.objExists(item):
                        cmds.createNode(nodeType, name=item)
                        if parentDic["BrokenID"][nodeType][item]:
                            if cmds.objExists(parentDic["BrokenID"][nodeType][item]):
                                cmds.parent(item, parentDic["BrokenID"][nodeType][item])
                        cmds.select(clear=True)
            return True


    def importParentingData(self, parentDic, *args):
        """ Import parenting data and put the nodes as the correct hierarchy if needed.
        """
        if not self.getParentingDataDic()["Parent"] == parentDic["Parent"]:
            self.utils.setProgress(max=len(parentDic["Parent"]), addOne=False, addNumber=False)
            # define lists to check result
            wellImportedList = []
            parentIssueList = []
            notFoundNodesList = []
            # check parenting shaders
            for item in parentDic["Parent"]:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if not cmds.objExists(item):
                    parentIssueList.append(item)
                    shortItem = item[item.rfind("|")+1:]
                    if cmds.objExists(shortItem):
                        if len(cmds.ls(shortItem)) == 1:
                            # get father name
                            longFatherNode = item[:item.rfind("|")]
                            shortFatherNode = longFatherNode[longFatherNode.rfind("|")+1:]
                            currentFatherList = cmds.listRelatives(shortItem, parent=True)
                            if cmds.objExists(longFatherNode):
                                # simple parent to existing old father node in the ancient hierarchy
                                cmds.parent(shortItem, longFatherNode)
                                wellImportedList.append(shortItem)
                            elif currentFatherList:
                                if currentFatherList[0] == shortFatherNode:
                                    # already child of the father node
                                    wellImportedList.append(shortItem)
                            elif cmds.objExists(shortFatherNode):
                                if len(cmds.ls(shortFatherNode)) == 1:
                                    # found unique father node in another hierarchy to parent
                                    cmds.parent(shortItem, shortFatherNode)
                                    wellImportedList.append(shortItem)
                                else:
                                    self.notWorkedWellIO(self.dpUIinst.lang['i075_moreOne']+" "+self.dpUIinst.lang['i076_sameName']+" "+shortFatherNode)
                            #else: #root here
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['i075_moreOne']+" "+self.dpUIinst.lang['i076_sameName']+" "+shortItem)
                    else:
                        notFoundNodesList.append(shortItem)
            if parentIssueList:
                if wellImportedList:
                    self.wellDoneIO(self.exportedList[-1]+": "+', '.join(parentIssueList))
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
            else:
                self.wellDoneIO(self.exportedList[-1])
        else:
            self.wellDoneIO(self.exportedList[-1])
