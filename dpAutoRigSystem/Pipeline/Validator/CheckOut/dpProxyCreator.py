# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ProxyCreator"
TITLE = "m230_proxyCreator"
DESCRIPTION = "m231_proxyCreatorDesc"
ICON = "/Icons/dp_proxyCreator.png"

PROXIED = "dpProxied"
NO_PROXY = "dpDoNotProxyIt"

DP_PROXYCREATOR_VERSION = 1.6


class ProxyCreator(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PROXYCREATOR_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.repeatedNameList = []
    

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
            self.skinClusterList = []
            proxyGrp = None
            if objList:
                proxyGrp = objList[0]
            else:
                proxyGrp = self.utils.getNodeByMessage("proxyGrp")
                if not proxyGrp:
                    if cmds.objExists("Proxy_Grp"):
                        proxyGrp = "Proxy_Grp"
            if proxyGrp:
                if not PROXIED in cmds.listAttr(proxyGrp):
                    meshList = cmds.listRelatives(proxyGrp, children=True, allDescendents=True, type="mesh")
                    if not meshList:
                        renderGrp = self.utils.getNodeByMessage("renderGrp")
                        if not renderGrp:
                            if cmds.objExists("Render_Grp"):
                                renderGrp = "Render_Grp"
                        if renderGrp:
                            meshList = cmds.listRelatives(renderGrp, children=True, allDescendents=True, fullPath=True, type="mesh")
                    if meshList:
                        # find meshes to generate proxy
                        toProxyList = []
                        for mesh in meshList:
                            if len(cmds.ls(mesh)) == 1:
                                meshTransform = cmds.listRelatives(mesh, parent=True, fullPath=True, type="transform")
                                if meshTransform:
                                    if not meshTransform[0] in toProxyList:
                                        if not NO_PROXY in cmds.listAttr(meshTransform):
                                            if not PROXIED in cmds.listAttr(meshTransform):
                                                toProxyList.append(meshTransform[0])
                        if toProxyList:
                            self.utils.setProgress(max=len(toProxyList), addOne=False, addNumber=False)
                            self.checkedObjList.append(proxyGrp)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    for sourceTransform in toProxyList:
                                        sourceShortName = self.utils.getShortName(sourceTransform)
                                        self.utils.setProgress(self.dpUIinst.lang[self.title]+": "+sourceShortName)
                                        self.createProxy(sourceTransform, sourceShortName, proxyGrp)
                                    self.proxyIntegration(proxyGrp)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+proxyGrp)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+proxyGrp)
                        else:
                            self.foundIssueList.append(False)
                            self.resultOkList.append(True)
                    else:
                        self.notFoundNodes(proxyGrp)
                else:
                    self.notFoundNodes(proxyGrp)
            else:
                self.notFoundNodes(proxyGrp)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---
        
        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def createProxy(self, source, shortName, grp, *args):
        """ Creates a proxy setup from the given source transform and put it into the given grp group.
        """
        try:
            inputDeformerList = cmds.findDeformers(source)
        except:
            return
        skinClusterNode = None
        if inputDeformerList:
            for deformerNode in inputDeformerList:
                if cmds.objectType(deformerNode) == "skinCluster":
                    skinClusterNode = deformerNode
                    break
        if skinClusterNode:
            self.skinClusterList.append(skinClusterNode)
            weightedInfluenceList = cmds.skinCluster(skinClusterNode, query=True, weightedInfluence=True)
            if weightedInfluenceList:
                # get data and store it into a dic
                indexJointDic = {}
                sourceFaceList = cmds.ls(source+".f[*]", flatten=True, long=True)
                for i, idx in enumerate(sourceFaceList):
                    percList = cmds.skinPercent(skinClusterNode, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=None, query=True)
                    if percList:
                        indexJointDic[i] = percList[0]
                        if not len(percList) == 1:
                            jointValueList = []
                            for item in percList:
                                jointValueList.append(cmds.skinPercent(skinClusterNode, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=item, query=True))
                            indexJointDic[i] = percList[jointValueList.index(max(jointValueList))]
                for jnt in weightedInfluenceList:
                    nodeFaceList = []
                    skinnedFaceList = []
                    # data analisis
                    for j in list(indexJointDic.keys()):
                        if indexJointDic[j] == jnt:
                            skinnedFaceList.append(j)
                    if skinnedFaceList:
                        # filter lists
                        faceList = [w.replace(source+".f[", "") for w in sourceFaceList]
                        faceList = [int(w.replace("]", "")) for w in faceList]
                        if faceList:
                            for v in reversed(skinnedFaceList):
                                faceList.pop(v)
                        if faceList:
                            for n in faceList:
                                nodeFaceList.append(source+".f["+str(n)+"]")
                        # create proxy geometry
                        dup = cmds.duplicate(source, name=shortName+"_"+str(self.repeatedNameList.count(shortName)).zfill(2)+"_"+jnt+"_Pxy")[0]
                        self.repeatedNameList.append(shortName)
                        self.utils.removeUserDefinedAttr(dup)
                        self.utils.deleteOrigShape(dup)
                        self.utils.removeFromSets(dup)
                        if nodeFaceList:
                            faceDupList = [w.replace(source, dup) for w in nodeFaceList]
                            cmds.delete(faceDupList)
                        self.dpUIinst.ctrls.setLockHide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], l=False)
                        cmds.xform(dup, pivots=cmds.xform(jnt, worldSpace=True, rotatePivot=True, query=True))
                        cmds.parent(dup, jnt)
                        cmds.scriptEditorInfo(suppressWarnings=True)
                        cmds.makeIdentity(dup, apply=True, translate=True, rotate=True, scale=True)
                        cmds.scriptEditorInfo(suppressWarnings=False)
                        self.checkReverseNormal(dup, jnt)
                        cmds.connectAttr(jnt+".worldMatrix", dup+".offsetParentMatrix", force=True)
                        cmds.parent(dup, grp)
                        self.utils.setAttrValues([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], [0, 0, 0, 0, 0, 0, 1, 1, 1])
                        self.dpUIinst.ctrls.setLockHide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        drawOverrideList = cmds.listConnections(dup+".drawOverride", source=True, destination=False, plugs=True)
                        if drawOverrideList:
                            # remove from display layer
                            cmds.disconnectAttr(drawOverrideList[0], dup+".drawOverride")
                        cmds.setAttr(dup+".overrideEnabled", 1)
                        cmds.setAttr(dup+".overrideDisplayType", 2) #reference
                        self.reconnectVisibility(source, dup)
            cmds.addAttr(source, longName=PROXIED, attributeType="bool", defaultValue=1)
        sourceParent = cmds.listRelatives(source, parent=True, fullPath=True, type="transform")
        if sourceParent:
            if sourceParent[0] == grp:
                cmds.delete(source)


    def proxyIntegration(self, grp, *args):
        """ Add attributes, connect to deformer nodeState if possible to disable them in order to get performance.
        """
        if not PROXIED in cmds.listAttr(grp):
            cmds.addAttr(grp, longName=PROXIED, attributeType="bool", defaultValue=1)
        optionCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optionCtrl:
            # prepare optionCtrl to deformers connections
            cmds.setAttr(optionCtrl+".proxy", channelBox=True)
            cmds.addAttr(optionCtrl, longName="proxyRevOutput", attributeType="bool")
            proxyRev = cmds.createNode("reverse", name="Proxy_Rev")
            cmds.connectAttr(optionCtrl+".proxy", proxyRev+".inputX", force=True)
            cmds.connectAttr(proxyRev+".outputX", optionCtrl+".proxyRevOutput", force=True)
            deformerList = self.skinClusterList
            defList = ["blendShape", "wrap", "ffd", "wire", "shrinkWrap", "sculpt", "morph"]
            for deform in defList:
                deformerList.extend(cmds.ls(type=deform) or [])
            if deformerList:
                for deformNode in deformerList:
                    try:
                        cmds.connectAttr(optionCtrl+".proxy", deformNode+".nodeState") #don't force it please
                    except:
                        pass #maybe it already has a connection from another node
            # hide controllers and meshes
            self.connectProxyVis(optionCtrl, "mesh")
            self.connectProxyVis(optionCtrl, "tweaks")
            self.connectProxyVis(optionCtrl, "Tweaks") #fixed camelCase for earlier rig versions v4.03.32
            self.connectProxyVis(optionCtrl, suffixName="Facial_Ctrls_Grp")
            self.connectProxyVis(optionCtrl, suffixName="Deformer_Ctrl_Grp")
        self.dpUIinst.ctrls.colorShape([grp], [1, 0.5, 0.5], outliner=True) #red


    def connectProxyVis(self, ctrl, attr=None, suffixName=None, *args):
        """ Create a reverseNode to plug it to the inverse visibility proxy option to the matching nodes.
        """
        if attr or suffixName:
            if attr:
                if attr in cmds.listAttr(ctrl):
                    connectList = cmds.listConnections(ctrl+"."+attr, source=False, destination=True, plugs=True) #list before connect on it
                    visMD = cmds.createNode("multiplyDivide", name="Proxy_"+(attr[0].upper()+attr[1:])+"_Vis_MD")
                    cmds.connectAttr(ctrl+".proxyRevOutput", visMD+".input1X", force=True)
                    cmds.connectAttr(ctrl+"."+attr, visMD+".input2X", force=True)
                    if connectList:
                        for plugDest in connectList:
                            cmds.connectAttr(visMD+".outputX", plugDest, force=True)
            else:
                allNodesList = cmds.ls("*"+suffixName, selection=False)
                if allNodesList:
                    for item in allNodesList:
                        cmds.connectAttr(ctrl+".proxyRevOutput", item+".visibility", force=True)


    def reconnectVisibility(self, sourceMesh, proxyMesh, *args):
        """ Check if there's sourceMesh visibility connection then connect the new proxyMesh visibility too, if so.
        """
        visList = cmds.listConnections(sourceMesh+".visibility", source=True, destination=False, plugs=True)
        if visList:
            cmds.connectAttr(visList[0], proxyMesh+".visibility", force=True)


    def checkReverseNormal(self, dup, jnt, *args):
        """ Verify if there're negative scale joint attributes and reverse the normal mesh if true.
        """
        for axis in ['sx', 'sy', 'sz']:
            if cmds.getAttr(jnt+'.'+axis) < 0:
                cmds.polyNormal(dup, normalMode=0, userNormalMode=0, constructionHistory=False)
                break
