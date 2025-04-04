# importing libraries:
from maya import cmds
from maya import mel
from ....Modules.Base import dpBaseAction
from ....Modules.Library import dpWeights

# global variables to this module:
CLASS_NAME = "DeformationIO"
TITLE = "r033_deformationIO"
DESCRIPTION = "r034_deformationIODesc"
ICON = "/Icons/dp_deformationIO.png"

DP_DEFORMATIONIO_VERSION = 1.2


class DeformationIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DEFORMATIONIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_deformationIO"
        self.startName = "dpDeformation"
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
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    if self.firstMode: #export
                        itemList = None
                        if objList:
                            itemList = objList
                        else:
                            itemList = cmds.listRelatives(cmds.ls(selection=False, type="mesh"), parent=True) or []
                            itemList.extend(cmds.listRelatives(cmds.ls(selection=False, type="nurbsCurve"), parent=True) or [])
                        if itemList:
                            # finding deformers
                            hasDef = False
                            inputDeformerList = cmds.listHistory(itemList, pruneDagObjects=False, interestLevel=True)
                            for deformerType in self.defWeights.typeAttrDic.keys():
                                if cmds.ls(inputDeformerList, type=deformerType):
                                    hasDef = True
                                    break
                            if hasDef:
                                self.exportDicToJsonFile(self.getDeformerDataDic(inputDeformerList))
                            else:
                                self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes']+" deformers")
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes']+" mesh")
                    else: #import
                        deformerDic = self.importLatestJsonFile(self.getExportedList())
                        if deformerDic:
                            self.importDeformationData(deformerDic)
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
        cmds.select(clear=True)
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getDeformerDataDic(self, inputDeformerList, *args):
        """ Return the deformer data dictionary to export.
        """
        self.utils.setProgress(max=len(self.defWeights.typeAttrDic.keys()), addOne=False, addNumber=False)
        # Declaring the data dictionary to export it
        deformerDic = {}
        # run for all deformer types to get info
        for deformerType in self.defWeights.typeAttrDic.keys():
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            deformerList = cmds.ls(selection=False, type=deformerType)
            if deformerList:
                for deformerNode in deformerList:
                    if deformerNode in inputDeformerList:
                        # get the attributes and values for this deformer node
                        deformerDic[deformerNode] = self.defWeights.getDeformerInfo(deformerNode)
                        # Get shape indexes for the deformer so we can query the deformer weights
                        shapeList, indexList, shapeToIndexDic = self.defWeights.getShapeToIndexData(deformerNode)
                        # update dictionary
                        deformerDic[deformerNode]["shapeList"] = shapeList
                        deformerDic[deformerNode]["indexList"] = indexList
                        deformerDic[deformerNode]["shapeToIndexDic"] = shapeToIndexDic
                        deformerDic[deformerNode]["weights"] = {}
                        for shape in shapeList:
                            # Get weights
                            index = shapeToIndexDic[shape]
                            weights = self.defWeights.getDeformerWeights(deformerNode, index)
                            if deformerDic[deformerNode]["relatedNode"]: 
                                if not deformerType == "ffd":
                                    # nonLinear because other don't have weights (wrap, shrinkWrap and wire)
                                    weights = self.defWeights.getDeformerWeights(deformerDic[deformerNode]["relatedNode"], index)
                            deformerDic[deformerNode]["weights"][index] = weights
                        # componentTag
                        deformerDic[deformerNode]["componentTag"] = self.defWeights.checkUseComponentTag(deformerNode)
                        # parenting
                        deformerDic[deformerNode]["father"] = None
                        if deformerDic[deformerNode]["relatedNode"]:
                            if cmds.listRelatives(deformerDic[deformerNode]["relatedNode"], allParents=True):
                                deformerDic[deformerNode]["father"] = cmds.listRelatives(deformerDic[deformerNode]["relatedNode"], allParents=True, fullPath=True)[0]
        return deformerDic


    def importDeformation(self, deformerNode, deformerDic, wellImported, *args):
        """ Import deformer data creating a new deformer node, set values and weights.
        """
        self.existShapeList = [s for s in deformerDic[deformerNode]["shapeList"] if cmds.objExists(s)]
        newDefNode = None
        # verify if the deformer node exists to don't recreate it and import data
        if cmds.objExists(deformerNode):
            newDefNode = deformerNode
            self.defWeights.assignDeformer(deformerNode, self.existShapeList)
        else:
            # create a new deformer if it doesn't exists
            if deformerDic[deformerNode]["type"] == "cluster":
                newDefNode = cmds.cluster(self.existShapeList, name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"])[0] #[cluster, handle]
            elif deformerDic[deformerNode]["type"] == "deltaMush":
                newDefNode = cmds.deltaMush(self.existShapeList, name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"])[0] #[deltaMush]
            elif deformerDic[deformerNode]["type"] == "tension":
                newDefNode = cmds.tension(self.existShapeList, name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"])[0] #[tension]
            elif deformerDic[deformerNode]["type"] == "ffd":
                latticeList = cmds.lattice(self.existShapeList, name=deformerDic[deformerNode]["name"], divisions=deformerDic[deformerNode]["divisions"], useComponentTags=deformerDic[deformerNode]["componentTag"]) #[set, ffd, base] 
                newDefNode = latticeList[0]
                self.defWeights.setLatticePoints(latticeList[1], deformerDic[deformerNode]["relatedData"]["pointList"])
                cmds.rename(latticeList[1], deformerDic[deformerNode]["relatedNode"])
                cmds.rename(latticeList[2], deformerDic[deformerNode]["relatedData"]["baseLatticeMatrix"])
            elif deformerDic[deformerNode]["type"] == "sculpt":
                sculptList = cmds.sculpt(self.existShapeList, name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"]) #[sculpt, sculptor, orig]
                newDefNode = sculptList[0]
                cmds.rename(sculptList[1], deformerDic[deformerNode]["relatedData"]["sculptor"])
                cmds.rename(sculptList[2], deformerDic[deformerNode]["relatedData"]["originLocator"])
            elif deformerDic[deformerNode]["type"] == "wrap":
                if cmds.objExists(deformerDic[deformerNode]["relatedNode"]):
                    wrapBaseShape = False
                    if "inflType" in cmds.listAttr(deformerDic[deformerNode]["relatedNode"]):
                        pluggedList = cmds.listConnections(deformerDic[deformerNode]["relatedNode"]+".inflType", destination=True, source=False)
                        if pluggedList:
                            for plugged in pluggedList:
                                if cmds.objectType(plugged) == "wrap":
                                    wrapBaseShapeList = cmds.listConnections(plugged+".basePoints[0]", destination=False, source=True)
                                    if wrapBaseShapeList:
                                        wrapBaseShape = wrapBaseShapeList[0]
                                        break
                    cmds.select(self.existShapeList, deformerDic[deformerNode]["relatedNode"])
                    mel.eval("CreateWrap;")
                    hist = cmds.listHistory(self.existShapeList)
                    wrapList = cmds.ls(hist, type="wrap")[0]
                    newDefNode = cmds.rename(wrapList, deformerDic[deformerNode]["name"])
                    newWrapBaseNode = cmds.listConnections(newDefNode+".basePoints[0]", destination=False, source=True)[0]
                    if wrapBaseShape:
                        cmds.connectAttr(wrapBaseShape+".worldMesh[0]", newDefNode+".basePoints[0]", force=True)
                        cmds.delete(newWrapBaseNode)
                    supportGrp = self.utils.getNodeByMessage("supportGrp")
                    if supportGrp:
                        parentNodeList = []
                        if wrapBaseShape:
                            parentNodeList = cmds.listRelatives(wrapBaseShape, parent=True)
                        else:
                            parentNodeList = cmds.listRelatives(newWrapBaseNode, parent=True)
                        if parentNodeList:
                            if not parentNodeList[0] == supportGrp:
                                cmds.parent(newWrapBaseNode, supportGrp)
            elif deformerDic[deformerNode]["type"] == "shrinkWrap":
                newDefNode = cmds.deformer(self.existShapeList, type=deformerDic[deformerNode]["type"], name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"])[0] #shrinkWrap
                for cAttr in ["continuity", "smoothUVs", "keepBorder", "boundaryRule", "keepHardEdge", "propagateEdgeHardness", "keepMapBorders"]:
                    cmds.connectAttr(deformerDic[deformerNode]["relatedNode"]+"."+cAttr, newDefNode+"."+cAttr, force=True)
                cmds.connectAttr(deformerDic[deformerNode]["relatedNode"]+".worldMesh", newDefNode+".targetGeom", force=True)
            elif deformerDic[deformerNode]["type"] == "wire":
                if not cmds.objExists(deformerDic[deformerNode]["relatedNode"]):
                    isPeriodic = False
                    if deformerDic[deformerNode]["relatedData"]["form"] == 2:
                        isPeriodic = True
                    cmds.curve(name=deformerDic[deformerNode]["relatedNode"], periodic=isPeriodic, point=deformerDic[deformerNode]["relatedData"]["point"], degree=deformerDic[deformerNode]["relatedData"]["degree"], knot=deformerDic[deformerNode]["relatedData"]["knot"])
                newDefNode = cmds.wire(self.existShapeList, wire=deformerDic[deformerNode]["relatedNode"], name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"])[0] #wire
            elif deformerDic[deformerNode]["nonLinear"]:
                nonLinearList = cmds.nonLinear(self.existShapeList, type=deformerDic[deformerNode]["nonLinear"], name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"]) #[def, handle] bend, flare, sine, squash, twist, wave
                newDefNode = nonLinearList[0]
                cmds.rename(nonLinearList[1], deformerDic[deformerNode]["relatedData"])
            else: #solidify, proximityWrap, morph, textureDeformer, jiggle
                newDefNode = cmds.deformer(self.existShapeList, type=deformerDic[deformerNode]["type"], name=deformerDic[deformerNode]["name"], useComponentTags=deformerDic[deformerNode]["componentTag"])[0]
            if deformerDic[deformerNode]["type"] == "morph":
                if cmds.objExists(deformerDic[deformerNode]["relatedNode"]):
                    cmds.connectAttr(deformerDic[deformerNode]["relatedNode"]+".worldMesh[0]", newDefNode+".morphTarget[0]", force=True)
                else:
                    wellImported = False
                    self.notWorkedWellIO(self.latestDataFile+": "+deformerNode+" - "+deformerDic[deformerNode]["relatedNode"])
        # parenting
        needParentIt = False
        if deformerDic[deformerNode]["father"]:
            if cmds.objExists(deformerDic[deformerNode]["father"]):
                if cmds.listRelatives(deformerDic[deformerNode]["relatedNode"], allParents=True, fullPath=True):
                    if not deformerDic[deformerNode]["father"] in cmds.listRelatives(deformerDic[deformerNode]["relatedNode"], allParents=True, fullPath=True):
                        needParentIt = True
                else:
                    needParentIt = True
        if needParentIt:
            if deformerDic[deformerNode]["type"] == "ffd":
                cmds.parent([deformerDic[deformerNode]["relatedNode"], deformerDic[deformerNode]["relatedData"]["baseLatticeMatrix"]], deformerDic[deformerNode]["father"])
            else:
                cmds.parent(deformerDic[deformerNode]["relatedNode"], deformerDic[deformerNode]["father"])
        # import attribute values
        if newDefNode:
            for attr in deformerDic[deformerNode]["attributes"].keys():
                try:
                    cmds.setAttr(newDefNode+"."+attr, deformerDic[deformerNode]["attributes"][attr])
                except:
                    pass #just to avoid try set connected attributes like envelope or curvature.
        # import deformer weights, except for skinCluster, blendShape, sculpt, wrap
        weightsDic = deformerDic[deformerNode]["weights"]
        if weightsDic:
            for index in deformerDic[deformerNode]["indexList"]:
                currentIndex = self.defWeights.getCurrentDeformedIndex(deformerNode, deformerDic[deformerNode]["shapeToIndexDic"], index)
                if weightsDic[str(index)]:
                    # cluster, deltaMush, tension, ffd, shrinkWrap, wire, nonLinear, solidify, proximityWrap, textureDeformer, jiggle
                    self.defWeights.setDeformerWeights(deformerDic[deformerNode]["name"], weightsDic[str(index)], currentIndex)
        return wellImported


    def importDeformationData(self, deformerDic, *args):
        """ Import the deformation from exported file using the given dictionary.
        """
        wellImported = True
        toImportList, notFoundMeshList, changedShapeMeshList = [], [], []
        for deformerNode in deformerDic.keys():
            # check mesh existing
            for shapeNode in deformerDic[deformerNode]["shapeList"]:
                if cmds.objExists(shapeNode):
                    if not deformerNode in toImportList:
                        toImportList.append(deformerNode)
                else:
                    notFoundMeshList.append(deformerNode)
        if toImportList:
            self.utils.setProgress(max=len(toImportList), addOne=False, addNumber=False)
            for deformerNode in toImportList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                try:
                    wellImported = self.importDeformation(deformerNode, deformerDic, wellImported)
                except Exception as e:
                    self.notWorkedWellIO(self.latestDataFile+": "+deformerNode+" - "+str(e))
            if notFoundMeshList: #call again the same instruction to try create a deformer in a deformer, like a cluster in a lattice.
                for deformerNode in notFoundMeshList:
                    for shapeNode in deformerDic[deformerNode]["shapeList"]:
                        if cmds.objExists(shapeNode):
                            try:
                                wellImported = self.importDeformation(deformerNode, deformerDic, wellImported)
                            except Exception as e:
                                self.notWorkedWellIO(self.latestDataFile+": "+deformerNode+" - "+str(e))
            if wellImported:
                self.wellDoneIO(self.latestDataFile)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(deformerDic.keys())))
        if not wellImported:
            if changedShapeMeshList:
                self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" shape "+str(', '.join(changedShapeMeshList)))
            elif notFoundMeshList:
                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
