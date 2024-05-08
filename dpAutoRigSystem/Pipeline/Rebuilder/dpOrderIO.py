# importing libraries:
from maya import cmds
from .. import dpBaseActionClass
from ...Deforms import dpWeights # need it or we can just use dpUIinst.skin instead?




from importlib import reload
reload(dpWeights)





# global variables to this module:
CLASS_NAME = "OrderIO"
TITLE = "r035_orderIO"
DESCRIPTION = "r036_orderIODesc"
ICON = "/Icons/dp_orderIO.png"

DP_ORDERIO_VERSION = 1.0


class OrderIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_ORDERIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_orderIO"
        self.startName = "dpOrder"
        self.defWeights = dpWeights.Weights(self.dpUIinst)
    

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
                    meshList = None
                    if objList:
                        meshList = objList
                    else:
                        meshList = self.defWeights.getDeformedModelList(deformerTypeList=self.defWeights.typeAttrDic.keys(), ignoreAttr=self.dpUIinst.skin.ignoreSkinningAttr)
                    if meshList:
                        #
                        # WIP
                        #
                        print("MESH LIST HERE 00000 =", meshList)


                        orderDic = {}
                        progressAmount = 0
                        maxProcess = len(meshList)
                        for mesh in meshList:
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                            orderDic[mesh] = self.defWeights.getOrderList(mesh)
                        if orderDic:
                            try:
                                # export order list data
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                                self.pipeliner.saveJsonFile(orderDic, jsonName)
                                self.wellDoneIO(jsonName)
                            except Exception as e:
                                self.notWorkedWellIO(', '.join(meshList)+": "+str(e))
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" - deformed meshes")
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" - meshes")
                else: #import


                    # 
                    # TODO
                    #
                    #

                    self.exportedList = self.getExportedList()
                    if self.exportedList:
                        self.exportedList.sort()
                        skinWeightDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                        if skinWeightDic:
                            progressAmount = 0
                            maxProcess = len(skinWeightDic.keys())
                            wellImported = True
                            toImportList, notFoundMeshList, changedTopoMeshList, changedShapeMeshList = [], [], [], []
                            
                            # reference old wip rig version to compare meshes changes
                            #refNodeList = self.referOldWipFile()
                            refNodeList = None

                            for mesh in skinWeightDic.keys():
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                                if cmds.objExists(mesh):
                                    if refNodeList:
                                        for refNodeName in refNodeList:
                                            if refNodeName[refNodeName.rfind(":")+1:] == self.dpUIinst.skin.getIOFileName(mesh):
                                                if cmds.polyCompare(mesh, refNodeName, vertices=True) > 0 or cmds.polyCompare(mesh, refNodeName, edges=True) > 0: #check if shape changes
                                                    changedShapeMeshList.append(mesh)
                                                    wellImported = False
                                                elif not len(cmds.ls(mesh+".vtx[*]", flatten=True)) == len(cmds.ls(refNodeName+".vtx[*]", flatten=True)): #check if poly count changes
                                                    changedTopoMeshList.append(mesh)
                                                    wellImported = False
                                                else:
                                                    toImportList.append(mesh)
                                    else:
                                        toImportList.append(mesh)
                                else:
                                    notFoundMeshList.append(mesh)
                            if refNodeList:
                                cmds.file(self.refPathName, removeReference=True)
                            if toImportList:
                                try:
                                    # import skin weights
                                    self.dpUIinst.skin.importSkinWeightsFromFile(toImportList, self.ioPath, self.exportedList[-1])
                                    self.wellDoneIO(', '.join(toImportList))
                                except Exception as e:
                                    self.notWorkedWellIO(self.exportedList[-1]+": "+str(e))
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(skinWeightDic.keys())))
                            if not wellImported:
                                if changedShapeMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" shape "+str(', '.join(changedShapeMeshList)))
                                elif changedTopoMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" topology "+str(', '.join(changedTopoMeshList)))
                                elif notFoundMeshList:
                                    self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic
