###
#
#   THANKS to:
#       David Johnson, who created the great djRivet.mel that I used a lot!
#       david@djx.com.au
#       www.djx.com.au
#
#    CREDITS by David Johnson:
#        Michael Bazhutkin, I used your excellent rivet.mel for years - thanks for sharing!
#        Mike Rhone, who said "Better than rivet:Use a follicle."
#        Brecht Debaene, for showing me how to hook up a follicle
#        robthebloke.org, for sharing the knowlege.
#
#   Also thanks to Caio Hidaka for the FaceToRivet implementation.
#
###


# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from ..Modules.Library import dpUtils
from ..Modules.Library import dpControls

# global variables to this module:
CLASS_NAME = "Rivet"
TITLE = "m083_rivet"
DESCRIPTION = "m084_rivetDesc"
ICON = "/Icons/dp_rivet.png"

MASTER_GRP = "masterGrp"
RIVET_GRP = "Rivet_Grp"
MORPH = "Morph"
WRAP = "Wrap"

DP_RIVET_VERSION = 1.8


class Rivet(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # declaring variables
        self.dpUIinst = dpUIinst
        self.ctrls = dpControls.ControlClass(self.dpUIinst)
        self.geoToAttach = None
        self.itemType = None
        self.meshNode = None
        self.selectedUVSet = None
        self.morphDeformer = MORPH
        self.wrapDeformer = WRAP
        self.mayaMinimalVersion = 2022.3
        self.mayaVersionRequired = self.checkMayaVersion()
        # call main function
        if ui:
            self.dpRivetUI()
            # try to fill UI items from selection
            self.dpFillUI()
            
            
    def dpCloseRivetUi(self, *args):
        if cmds.window('dpRivetWindow', query=True, exists=True):
            cmds.deleteUI('dpRivetWindow', window=True)
    
    
    def dpRivetUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating dpRivetUI Window:
        self.dpCloseRivetUi()
        rivet_winWidth  = 305
        rivet_winHeight = 470
        dpRivetWin = cmds.window('dpRivetWindow', title=self.dpUIinst.lang["m083_rivet"]+" "+str(DP_RIVET_VERSION), widthHeight=(rivet_winWidth, rivet_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        rivetLayout = cmds.columnLayout('rivetLayout', columnOffset=("left", 10))
        cmds.text(label=self.dpUIinst.lang["m145_loadGeo"], height=30, font='boldLabelFont', parent=rivetLayout)
        doubleLayout = cmds.rowColumnLayout('doubleLayout', numberOfColumns=2, columnWidth=[(1, 100), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=rivetLayout)
        cmds.button(label=self.dpUIinst.lang["m146_geo"]+" >", annotation="Load the Geometry here in order to be used to attach.", backgroundColor=(1.0, 0.7, 1.0), width=100, command=self.dpLoadGeoToAttach, parent=doubleLayout)
        self.geoToAttachTF = cmds.textField('geoToAttachTF', width=180, text="", changeCommand=partial(self.dpLoadGeoToAttach, None, True), parent=doubleLayout)
        uvSetLayout = cmds.rowColumnLayout('uvSetLayout', numberOfColumns=2, columnWidth=[(1, 110), (2, 210)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 1), (2, 'left', 10)], parent=rivetLayout)
        cmds.text(label="UV Set:", font='obliqueLabelFont', parent=uvSetLayout)
        self.uvSetTF = cmds.textField('uvSetTF', width=180, text="", editable=False, parent=uvSetLayout)
        cmds.separator(style='in', height=15, width=300, parent=rivetLayout)
        cmds.text(label=self.dpUIinst.lang["m147_itemsFollowGeo"], height=30, font='boldLabelFont', parent=rivetLayout)
        itemsLayout = cmds.columnLayout('itemsLayout', columnOffset=('left', 10), width=310, parent=rivetLayout)
        self.itemScrollList = cmds.textScrollList('itemScrollList', width=290, height=100, allowMultiSelection=True, parent=itemsLayout)
        cmds.separator(style='none', height=5, parent=itemsLayout)
        middleLayout = cmds.rowColumnLayout('middleLayout', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 0)], parent=itemsLayout)
        cmds.button(label=self.dpUIinst.lang["i045_add"], annotation=self.dpUIinst.lang["i045_add"], width=140, command=self.dpAddSelect, parent=middleLayout)
        cmds.button(label=self.dpUIinst.lang["i046_remove"], annotation=self.dpUIinst.lang["i046_remove"], width=140, command=self.dpRemoveSelect, parent=middleLayout)
        cmds.separator(style='in', height=15, width=300, parent=rivetLayout)
        cmds.text(label=self.dpUIinst.lang["i002_options"]+":", height=30, font='boldLabelFont', parent=rivetLayout)
        fatherLayout = cmds.columnLayout('fatherLayout', columnOffset=("left", 10), parent=rivetLayout)
        self.attachTCB = cmds.checkBox('attachTCB', label=self.dpUIinst.lang["m148_attach"]+" Translate", value=True, parent=fatherLayout)
        self.attachRCB = cmds.checkBox('attachRCB', label=self.dpUIinst.lang["m148_attach"]+" Rotate", value=False, parent=fatherLayout)
        self.fatherGrpCB = cmds.checkBox('fahterGrpCB', label=self.dpUIinst.lang["m149_createGroupConst"], value=True, parent=fatherLayout)
        invertLayout = cmds.columnLayout('invertLayout', columnOffset=("left", 10), parent=rivetLayout)
        self.addInvertCB = cmds.checkBox('addInvertCB', label=self.dpUIinst.lang["m150_avoidDoubleTransf"], height=20, value=True, changeCommand=self.dpChangeInvert, parent=invertLayout)
        translateLayout = cmds.rowColumnLayout('translateLayout', numberOfColumns=2, columnWidth=[(1, 30), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 5)], height=20, parent=rivetLayout)
        cmds.separator(style='none', parent=translateLayout)
        self.invertTCB = cmds.checkBox('invertTCB', label=self.dpUIinst.lang["m151_invert"]+" Translate", value=True, parent=translateLayout)
        rotateLayout = cmds.rowColumnLayout('rotateLayout', numberOfColumns=2, columnWidth=[(1, 30), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 5)], height=20, parent=rivetLayout)
        cmds.separator(style='none', parent=rotateLayout)
        self.invertRCB = cmds.checkBox('invertRCB', label=self.dpUIinst.lang["m151_invert"]+" Rotate", value=False, parent=rotateLayout)
        faceToRivetLayout = cmds.columnLayout('faceToRivetLayout', columnOffset=("left", 10), parent=rivetLayout)
        self.faceToRivetCB = cmds.checkBox('faceToRivetCB', label=self.dpUIinst.lang["m226_createFaceToRivet"], height=20, value=True, changeCommand=self.dpChangeDeformer, parent=faceToRivetLayout)
        deformerLayout = cmds.columnLayout('deformerLayout', columnOffset=("left", 20), parent=faceToRivetLayout)
        self.deformerCollection = cmds.radioCollection('deformerCollection', parent=deformerLayout)
        self.morphDeformerRB = cmds.radioButton(label=self.dpUIinst.lang["m232_morphDeformer"], annotation=self.morphDeformer, enable=self.mayaVersionRequired, collection=self.deformerCollection)
        self.wrapDeformerRB = cmds.radioButton(label=self.dpUIinst.lang["m233_wrapDeformer"], annotation=self.wrapDeformer, enable=self.mayaVersionRequired, collection=self.deformerCollection)
        cmds.radioCollection(self.deformerCollection, edit=True, select=self.morphDeformerRB)
        if not self.mayaVersionRequired:
            cmds.radioCollection(self.deformerCollection, edit=True, select=self.wrapDeformerRB)
        cmds.separator(style='none', height=15, parent=rivetLayout)
        createLayout = cmds.columnLayout('createLayout', columnOffset=("left", 10), parent=rivetLayout)
        cmds.button(label=self.dpUIinst.lang["i158_create"]+" "+self.dpUIinst.lang["m083_rivet"], annotation=self.dpUIinst.lang["i158_create"]+" "+self.dpUIinst.lang["m083_rivet"], width=290, backgroundColor=(0.20, 0.7, 1.0), command=self.dpCreateRivetFromUI, parent=createLayout)
        
        # call dpRivetUI Window:
        cmds.showWindow(dpRivetWin)
    
    
    def dpFillUI(self, *args):
        """ Try to auto fill UI elements from selection.
        """
        selList = cmds.ls(selection=True)
        if selList:
            if len(selList) > 1:
                itemList = selList[:-1]
                geo = selList[-1]
                self.dpLoadGeoToAttach(geo)
                self.dpAddSelect(itemList)
    
    
    def dpCreateRivetFromUI(self, *args):
        """ Just collect all information from UI and call the main function to create Rivet setup.
        """
        # getting UI values
        geoToAttach = cmds.textField(self.geoToAttachTF, query=True, text=True)
        uvSet = cmds.textField(self.uvSetTF, query=True, text=True)
        itemList = cmds.textScrollList(self.itemScrollList, query=True, allItems=True)
        attachTranslate = cmds.checkBox(self.attachTCB, query=True, value=True)
        attachRotate = cmds.checkBox(self.attachRCB, query=True, value=True)
        addFatherGrp = cmds.checkBox(self.fatherGrpCB, query=True, value=True)
        addInvert = cmds.checkBox(self.addInvertCB, query=True, value=True)
        invT = cmds.checkBox(self.invertTCB, query=True, value=True)
        invR = cmds.checkBox(self.invertRCB, query=True, value=True)
        faceToRivet = cmds.checkBox(self.faceToRivetCB, query=True, value=True)

        # call run function to create Rivet setup using UI values
        self.dpCreateRivet(geoToAttach, uvSet, itemList, attachTranslate, attachRotate, addFatherGrp, addInvert, invT, invR, faceToRivet, RIVET_GRP, True)
        self.dpCloseRivetUi()
    
    
    def dpSelectUVSetWin(self, uvSetList, *args):
        """ Ask user the UV Set to use.
        """
        self.selectedUVSet = cmds.confirmDialog(title="Multiple UV Sets", message="Which UV Set do you want to use?", button=uvSetList)
    
    
    def dpLoadUVSet(self, item, *args):
        """ Verify the UV sets for polygon mesh and show a dialog box in order to choose if there are more than one UVSet map.
        """
        if self.itemType == "mesh":
            uvSetList = cmds.polyUVSet(self.geoToAttach, query=True, allUVSets=True)
            self.selectedUVSet = uvSetList[0]
            if len(uvSetList) > 1:
                self.dpSelectUVSetWin(uvSetList)
            cmds.textField(self.uvSetTF, edit=True, text=self.selectedUVSet)
        elif self.itemType == "nurbsSurface":
            cmds.textField(self.uvSetTF, edit=True, text="nurbsSurface")
    
    
    def dpLoadGeoToAttach(self, geoName=None, geoFromUI=None, *args):
        """ Load selected object a geometry to attach rivet.
        """
        if geoName:
            selectedList = [geoName]
        elif geoFromUI:
            selectedList = [cmds.textField(self.geoToAttachTF, query=True, text=True)]
        else:
            selectedList = cmds.ls(selection=True)
        if selectedList:
            if self.dpCheckGeometry(selectedList[0]):
                self.geoToAttach = selectedList[0]
                cmds.textField(self.geoToAttachTF, edit=True, text=self.geoToAttach)
                self.dpLoadUVSet(self.geoToAttach)
        else:
            mel.eval("warning \"Select a geometry in order use it to attach rivets, please.\";")
    
    
    def dpAddSelect(self, sList=None, *args):
        """ Add selected items to target textscroll list
        """
        # declare variables
        selItemList = []
        # get selection
        if sList:
            selList=sList
        else:
            selList = cmds.ls(selection=True)
        # check if there is any selected object in order to continue
        if selList:
            # find transforms
            for item in selList:
                if not item in selItemList:
                    if cmds.objectType(item) == "transform":
                        if not item == self.geoToAttach:
                            selItemList.append(item)
                    elif ".vtx" in item or ".cv" in item or ".pt" in item:
                        selItemList.append(item)
            if selItemList:
                # get current list
                currentList = cmds.textScrollList(self.itemScrollList, query=True, allItems=True)
                if currentList:
                    # clear current list
                    cmds.textScrollList(self.itemScrollList, edit=True, removeAll=True)
                    # avoid repeated items
                    for item in selItemList:
                        if not item in currentList:
                            currentList.append(item)
                    # refresh textScrollList
                    cmds.textScrollList(self.itemScrollList, edit=True, append=currentList)
                else:
                    # add selected items in the empyt target scroll list
                    cmds.textScrollList(self.itemScrollList, edit=True, append=selItemList)
            else:
                mel.eval("warning \"Please, select a tranform node, vertices or lattice points in order to add it in the item list.\";")
        else:
            mel.eval("warning \"Please, select a tranform node, vertices or lattice points in order to add it in the item list.\";")
    
    
    def dpRemoveSelect(self, *args):
        """ Remove selected items from target scroll list.
        """
        selItemList = cmds.textScrollList(self.itemScrollList, query=True, selectItem=True)
        if selItemList:
            for item in selItemList:
                cmds.textScrollList(self.itemScrollList, edit=True, removeItem=item)
    
    
    def dpCheckGeometry(self, item, *args):
        isGeometry = False
        if item:
            if cmds.objExists(item):
                childList = cmds.listRelatives(item, children=True)
                if childList:
                    self.itemType = cmds.objectType(childList[0])
                    if self.itemType == "mesh" or self.itemType == "nurbsSurface":
                        if self.itemType == "mesh":
                            self.meshNode = childList[0]
                        isGeometry = True
                    else:
                        mel.eval("warning \""+item+" is not a geometry.\";")
                else:
                    mel.eval("warning \"Select the transform node instead of "+item+" shape, please.\";")
            else:
                mel.eval("warning \""+item+" does not exists, maybe it was deleted, sorry.\";")
        else:
            mel.eval("warning \"Not found "+item+"\";")
        return isGeometry
    
    
    def dpChangeInvert(self, value, *args):
        cmds.checkBox(self.invertTCB, edit=True, enable=value)
        cmds.checkBox(self.invertRCB, edit=True, enable=value)


    def dpChangeDeformer(self, value, *args):
        if not self.mayaVersionRequired:
            value = False
        cmds.radioButton(self.morphDeformerRB, edit=True, enable=value)
        cmds.radioButton(self.wrapDeformerRB, edit=True, enable=value)


    def dpInvertAttrTranformation(self, nodeName, invT=True, invR=False, *args):
        """ Creates a setup to invert attribute transformations in order to avoid doubleTransformation.
        """
        axisList = ['X', 'Y', 'Z']
        if cmds.objExists(nodeName):
            nodePivot = cmds.xform(nodeName, query=True, worldSpace=True, rotatePivot=True)
            if invR:
                invRGrp = cmds.group(nodeName, name=nodeName+"_InvR_Grp")
                cmds.xform(invRGrp, worldSpace=True, rotatePivot=(nodePivot[0], nodePivot[1], nodePivot[2]), rotateOrder="zyx")
                rMD = cmds.createNode('multiplyDivide', name=nodeName+"_InvR_MD", skipSelect=True)
                cmds.setAttr(rMD+'.input2X', -1)
                cmds.setAttr(rMD+'.input2Y', -1)
                cmds.setAttr(rMD+'.input2Z', -1)
                for axis in axisList:
                    cmds.connectAttr(nodeName+'.rotate'+axis, rMD+'.input1'+axis, force=True)
                    cmds.connectAttr(rMD+'.output'+axis, invRGrp+'.rotate'+axis, force=True)
            if invT:
                invTGrp = cmds.group(nodeName, name=nodeName+"_InvT_Grp")
                cmds.xform(invTGrp, worldSpace=True, rotatePivot=(nodePivot[0], nodePivot[1], nodePivot[2]))
                tMD = cmds.createNode('multiplyDivide', name=nodeName+"_InvT_MD", skipSelect=True)
                cmds.setAttr(tMD+'.input2X', -1)
                cmds.setAttr(tMD+'.input2Y', -1)
                cmds.setAttr(tMD+'.input2Z', -1)
                for axis in axisList:
                    cmds.connectAttr(nodeName+'.translate'+axis, tMD+'.input1'+axis, force=True)
                    cmds.connectAttr(tMD+'.output'+axis, invTGrp+'.translate'+axis, force=True)
    
    
    def dpCreateRivet(self, geoToAttach, uvSetName, itemList, attachTranslate, attachRotate, addFatherGrp, addInvert, invT, invR, faceToRivet, rivetGrpName='Rivet_Grp', askComponent=False, useOffset=True, *args):
        """ Create the Rivet setup.
            Returns follicle node.
        """
        # declaring variables
        self.shapeToAttachList = None
        self.shapeToAttach = None
        self.cpNode = None
        self.tempNoce = None
        attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        self.rivetList, togetherList = [], []
        isComponent = None
        
        # integrate to dpAutoRigSystem:
        self.masterGrp = None
        self.masterCtrl = None
        self.scalableGrp = None
        allList = cmds.ls(selection=False, type="transform")
        if allList:
            for node in allList:
                if cmds.objExists(node+"."+MASTER_GRP) and cmds.getAttr(node+"."+MASTER_GRP) == 1:
                    self.masterGrp = node
        if self.masterGrp:
            masterCtrlList = cmds.listConnections(self.masterGrp+".masterCtrl")
            scalableGrpList = cmds.listConnections(self.masterGrp+".scalableGrp")
            if masterCtrlList:
                self.masterCtrl = masterCtrlList[0]
            if scalableGrpList:
                self.scalableGrp = scalableGrpList[0]
        
        # create Rivet_Grp in order to organize hierarchy:
        createdRivetGrp = False
        self.rivetGrp = rivetGrpName
        if not cmds.objExists(rivetGrpName):
            createdRivetGrp = True
            self.rivetGrp = cmds.group(name=rivetGrpName, empty=True)
            for attr in attrList:
                cmds.setAttr(self.rivetGrp+"."+attr, lock=True, keyable=False, channelBox=False)
            cmds.addAttr(self.rivetGrp, longName="dpRivetGrp", attributeType='bool')
            cmds.setAttr(self.rivetGrp+".dpRivetGrp", 1)
            if self.scalableGrp:
                cmds.parent(self.rivetGrp, self.scalableGrp)
            
        # if Create FaceToRivet is activated, it will create a new geometry with cut faces, wrap in the original and parent in the Model_Grp
        if faceToRivet:
            geoToAttach = self.createFaceToRivet(itemList, self.extractGeoToRivet(geoToAttach), 4, geoToAttach)
            modelGrp = dpUtils.getNodeByMessage("modelsGrp")
            if modelGrp:
                self.ctrls.colorShape([modelGrp], [0.51, 1, 0.667], outliner=True) #green

        # get shape to attach:
        if cmds.objExists(geoToAttach):
            self.shapeToAttachList = cmds.ls(geoToAttach, dag=True, shapes=True)
        if self.shapeToAttachList:
            self.shapeToAttach = self.shapeToAttachList[0]
            # get shape type:
            self.shapeType = cmds.objectType(self.shapeToAttach)
            # verify if there are vertices, cv's or lattice points in our itemList:
            if itemList:
                asked = False
                for i, item in enumerate(itemList):
                    if ".vtx" in item or ".cv" in item or ".pt" in item:
                        if askComponent:
                            if not asked:
                                isComponent = cmds.confirmDialog(title="dpRivet on Components", message="How do you want attach vertices, cv's or lattice points?", button=("Individually", "Together", "Ignore"), defaultButton="Individually", dismissString="Ignore", cancelButton="Ignore")
                                asked = True
                                if isComponent == "Individually":
                                    cls = cmds.cluster(item, name=item[:item.rfind(".")]+"_"+str(i)+"_Cls")[0]+"Handle"
                                    clsToRivet = cmds.parent(cls, self.rivetGrp)[0]
                                    self.rivetList.append(clsToRivet)
                                elif isComponent == "Together":
                                    togetherList.append(item)
                                elif isComponent == "Ignore":
                                    itemList.remove(item)
                            elif isComponent == "Ignore":
                                itemList.remove(item)
                            elif isComponent == "Together":
                                togetherList.append(item)
                            else: #Individually
                                cls = cmds.cluster(item, name=item[:item.rfind(".")]+"_"+str(i)+"_Cls")[0]+"Handle"
                                clsToRivet = cmds.parent(cls, self.rivetGrp)[0]
                                self.rivetList.append(clsToRivet)
                        else: #Individually
                            cls = cmds.cluster(item, name=item[:item.rfind(".")]+"_"+str(i)+"_Cls")[0]+"Handle"
                            clsToRivet = cmds.parent(cls, self.rivetGrp)[0]
                            self.rivetList.append(clsToRivet)
                    elif cmds.objExists(item):
                        self.rivetList.append(item)
            else:
                mel.eval("error \"Select and add at least one item to be attached as a Rivet, please.\";")
            if isComponent == "Together":
                cls = cmds.cluster(togetherList, name="dpRivet_Cls")[0]+"Handle"
                clsToRivet = cmds.parent(cls, self.rivetGrp)[0]
                self.rivetList.append(clsToRivet)
            
            # check about locked or animated attributes on items:
            if not addFatherGrp:
                cancelProcess = False
                for rivet in self.rivetList:
                    # locked:
                    if cmds.listAttr(rivet, locked=True):
                        cancelProcess = True
                        break
                    # animated:
                    for attr in attrList:
                        if cmds.listConnections(rivet+"."+attr, source=True, destination=False):
                            cancelProcess = True
                            break
                if cancelProcess:
                    if createdRivetGrp:
                        cmds.delete(self.rivetGrp)
                    else:
                        for rivet in self.rivetList:
                            if not rivet in itemList:
                                # clear created clusters:
                                cmds.delete(rivet)
                    mel.eval("error \"Canceled process: items to be Rivet can't be animated or have locked attributes, sorry.\";")
                    return
            
            # workaround to avoid closestPoint node ignores transformations.
            # then we need to duplicate, unlock attributes and freezeTransformation:
            dupGeo = cmds.duplicate(geoToAttach, name=geoToAttach+"_dpRivet_TEMP_Geo")[0]
            # unlock attr:
            for attr in attrList:
                cmds.setAttr(dupGeo+"."+attr, lock=False)
            # parent to world:
            if cmds.listRelatives(dupGeo, allParents=True):
                cmds.parent(dupGeo, world=True)
            # freezeTransformation:
            cmds.makeIdentity(dupGeo, apply=True)
            dupShape = cmds.ls(dupGeo, dag=True, shapes=True)[0]
            
            # temporary transform node to store object's location:
            self.tempNode = cmds.createNode("transform", name=geoToAttach+"_dpRivet_TEMP_Transf", skipSelect=True)
                
            # working with mesh:
            if self.shapeType == "mesh":
                # working with uvSet:
                uvSetList = cmds.polyUVSet(dupShape, query=True, allUVSets=True)
                if len(uvSetList) > 1:
                    if not uvSetList[0] == uvSetName:
                        try:
                            # change uvSet order because closestPointOnMesh uses the default uv set
                            cmds.polyUVSet(dupShape, copy=True, uvSet=uvSetName, newUVSet=uvSetList[0])
                        except:
                            uvSetName = uvSetList[0]
                        
                # closest point on mesh node:
                self.cpNode = cmds.createNode("closestPointOnMesh", name=geoToAttach+"_dpRivet_TEMP_CP", skipSelect=True)
                cmds.connectAttr(dupShape+".outMesh", self.cpNode+".inMesh", force=True)
                
                # move tempNode to cpNode position:
                cmds.connectAttr(self.tempNode+".translate", self.cpNode+".inPosition", force=True)
            
            else: #nurbsSurface
                uRange = cmds.getAttr(dupShape+".minMaxRangeU")[0]
                vRange = cmds.getAttr(dupShape+".minMaxRangeV")[0]
                
                # closest point on mesh node:
                self.cpNode = cmds.createNode("closestPointOnSurface", name=geoToAttach+"_dpRivet_TEMP_CP", skipSelect=True)
                cmds.connectAttr(dupShape+".local", self.cpNode+".inputSurface", force=True)
                
            # working with follicles and attaches
            for rivet in self.rivetList:
                rivetPos = cmds.xform(rivet, query=True, worldSpace=True, rotatePivot=True)
                if addFatherGrp:
                    rivet = cmds.group(rivet, name=rivet+"_Rivet_Grp")
                    cmds.xform(rivet, worldSpace=True, rotatePivot=(rivetPos[0], rivetPos[1], rivetPos[2]))
                
                # move temp tranform to rivet location:
                cmds.xform(self.tempNode, worldSpace=True, translation=(rivetPos[0], rivetPos[1], rivetPos[2]))
                
                # get uv coords from closestPoint node
                fu = cmds.getAttr(self.cpNode+".u")
                fv = cmds.getAttr(self.cpNode+".v")
                
                if self.shapeType == "nurbsSurface":
                    # normalize UVs:
                    fu = abs((fu - uRange[0])/(uRange[1] - uRange[0]))
                    fv = abs((fv - vRange[0])/(vRange[1] - vRange[0]))
                    
                # create follicle:
                folTransf = cmds.createNode("transform", name=rivet+"_Fol", parent=self.rivetGrp, skipSelect=True)
                folShape = cmds.createNode("follicle", name=rivet+"_FolShape", parent=folTransf, skipSelect=True)
                
                # connect geometry shape and follicle:
                if self.shapeType == "mesh":
                    cmds.connectAttr(self.shapeToAttach+".worldMesh[0]", folShape+".inputMesh", force=True)
                    cmds.setAttr(folShape+".mapSetName", uvSetName, type="string")
                else: #nurbsSurface:
                    cmds.connectAttr(self.shapeToAttach+".local", folShape+".inputSurface", force=True)
                cmds.connectAttr(self.shapeToAttach+".worldMatrix[0]", folShape+".inputWorldMatrix", force=True)
                cmds.connectAttr(folShape+".outRotate", folTransf+".rotate", force=True)
                cmds.connectAttr(folShape+".outTranslate", folTransf+".translate", force=True)
                # put follicle in the correct place:
                cmds.setAttr(folShape+".parameterU", fu)
                cmds.setAttr(folShape+".parameterV", fv)
                
                # attach follicle and rivet using constraint:
                if attachTranslate and attachRotate:
                    cmds.parentConstraint(folTransf, rivet, maintainOffset=useOffset, name=rivet+"_PaC")
                elif attachTranslate:
                    cmds.parentConstraint(folTransf, rivet, maintainOffset=useOffset, name=rivet+"_PaC" , skipRotate=("x", "y", "z"))
                elif attachRotate:
                    cmds.parentConstraint(folTransf, rivet, maintainOffset=useOffset, name=rivet+"_PaC" , skipTranslate=("x", "y", "z"))
                
                # try to integrate to dpAutoRigSystem in order to keep the Rig as scalable:
                if self.masterCtrl:
                    cmds.scaleConstraint(self.masterCtrl, folTransf, maintainOffset=True, name=folTransf+"_ScC")
            
            # check invert group (back) in order to avoide double transformations:
            if addInvert:
                for rivet in self.rivetList:
                    self.dpInvertAttrTranformation(rivet, invT, invR)
                    
            # clean-up temporary nodes:
            cmds.delete(dupGeo, self.cpNode, self.tempNode)
            
        else:
            mel.eval("error \"Load one geometry to attach Rivets on it, please.\";")
        
        cmds.select(clear=True)
        return folTransf
    

    def extractGeoToRivet(self, geo, *args):
        """ Turn off skinCluster and blendShape envelope if exists, duplicate the selected geometry
            apply initial shading and remove it from any display layer
        """ 
        # Get the history to turn off envelopes if exists
        histList = cmds.listHistory(geo)
        shapeList = cmds.listRelatives(geo, shapes=True)
        if shapeList:
            # check if there's a skinCluster node connected to the first selected item
            checkSkin = self.dpCheckNodeExists(shapeList, "skinCluster")
            checkBS = self.dpCheckNodeExists(shapeList, "blendShape")
            if checkSkin == 1:
                skinClusterNode = cmds.ls(histList, type="skinCluster")[0]
                cmds.setAttr(skinClusterNode+".envelope", 0)
            if checkBS == 2:
                blendShapeNode = cmds.ls(histList, type="blendShape")[0]
                cmds.setAttr(blendShapeNode+".envelope", 0)
            # Duplicate geometry after turn off skinCluster and blendShape. 
            toRivetGeo = cmds.duplicate(geo)[0]
            dpUtils.removeUserDefinedAttr(toRivetGeo)
            # Unparenting
            if cmds.listRelatives(toRivetGeo, allParents=True):
                cmds.parent(toRivetGeo, world=True)
            # Unlock attributes and apply initialShading
            self.dpUIinst.ctrls.setLockHide([toRivetGeo], ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility"], False, True, True)
            cmds.sets(toRivetGeo, edit=True, forceElement="initialShadingGroup")
            cmds.editDisplayLayerMembers("defaultLayer", toRivetGeo, noRecurse=False)
            self.dpUIinst.ctrls.setLockHide([toRivetGeo], ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"], True, False, True)
            # Renaming
            toRivetGeo = cmds.rename(toRivetGeo, self.getFaceToRivetGeoName(geo))
            # Turning on nodes
            if checkSkin == 1:
                cmds.setAttr(skinClusterNode+".envelope", 1)
            if checkBS == 2:
                cmds.setAttr(blendShapeNode+".envelope", 1)
            return toRivetGeo
    

    def getFaceToRivetGeoName(self, geo, *args):
        """ Get the unused FaceToRivet geo to avoid multiples connections to the same original geometry.
            Returns the suggested name.
        """
        toRivetName = dpUtils.extractSuffix(geo)
        if "|" in toRivetName:
            toRivetName = toRivetName[toRivetName.rfind("|")+1:]
        i = 0
        done = False
        while done == False:
            if not cmds.objExists(toRivetName+"_FaceToRivet_"+str(i).zfill(2)+"_Geo"):
                done = True
            else:
                i += 1
        return toRivetName+"_FaceToRivet_"+str(i).zfill(2)+"_Geo"

    
    def createFaceToRivet(self, controlList, geometry, growMultiplier, origGeo, *args):
        """ Get the pivot coordinates from each control to get the nearest face from control to the geometry.
            After the initial selection it will grow 4 times by default.
            It uses delta to delete the extra faces, than glue it to the original model with Morph or Wrap deformer.
        """
        # Get the pivot's coordinates from each control.
        pivotList = {}
        for control in controlList:
            pivot = cmds.xform(control, query=True, translation=True, worldSpace=True)
            pivotList[control] = pivot
        # Get the coordinates from geometry faces.
        faceList = cmds.ls(geometry+".f[:]", flatten=True)
        faceCoordinateList = []
        for face in faceList:
            vertexCoordList = cmds.xform(face, query=True, translation=True, worldSpace=True)
            avgCoordinates = [
                sum(vertexCoordList[i::3]) / len(vertexCoordList[i::3])
                for i in range(3)
            ]
            faceCoordinateList.append(avgCoordinates)
        # Select the neareest face from each pivot.
        for control, pivot in pivotList.items():
            nearestFace = None
            minimalDistance = None
            for i, coord in enumerate(faceCoordinateList):
                distance = sum((coord[j] - pivot[j])**2 for j in range(3)) ** 0.5
                if minimalDistance is None or distance < minimalDistance:
                    minimalDistance = distance
                    nearestFace = faceList[i]
            if nearestFace:
                cmds.select(nearestFace, add=True)
        # Select the faces and growUp selection.
        cmds.scriptEditorInfo(edit=True, suppressWarnings=True, suppressInfo=True, suppressErrors=True, suppressResults=True)
        cmds.selectMode(component=True)
        cmds.selectType(facet=True)
        growMultiplier = growMultiplier - 1
        if growMultiplier > 0:
            for i in range(0, growMultiplier):
                cmds.GrowPolygonSelectionRegion()
        # Delta to delete unnecessary faces.
        selectedFaceList = cmds.ls(selection=True, flatten=True)
        allFaceList = cmds.ls(geometry+".f[*]", flatten=True)
        nonSelectedFaceList = list(set(allFaceList) - set(selectedFaceList))
        if nonSelectedFaceList:
            cmds.delete(nonSelectedFaceList)
        # AutoProjection for new UV and order selection to use dpRivet.
        cmds.polyAutoProjection(geometry, constructionHistory=False)
        cmds.selectMode(object=True)
        cmds.scriptEditorInfo(edit=True, suppressWarnings=False, suppressInfo=True, suppressErrors=False, suppressResults=False)
        # Create deformer by user selection
        deformerSelectedRadioButton = cmds.radioCollection(self.deformerCollection, query=True, select=True)
        deformerSelected = cmds.radioButton(deformerSelectedRadioButton, query=True, annotation=True)
        if deformerSelected == self.morphDeformer:
            self.applyMorphDeformer(geometry, origGeo)
        elif deformerSelected == self.wrapDeformer:
            self.applyWrapDeformer(geometry, origGeo)
        return geometry


    def dpCheckNodeExists(self, shapeList, type, *args):
        """ Verify if there's a skinCluster or blendShape node in the list of history of the shape.
            Return 1 if there's skinCluster.
            Return 2 if there's blendShape node
            Return -1 if there's another node with the same name.
        """
        for shapeNode in shapeList:
            if not shapeNode.endswith("Orig"):
                try:
                    histList = cmds.listHistory(shapeNode)
                    if histList:
                        for histItem in histList:
                            if type == "skinCluster":
                                if cmds.objectType(histItem) == "skinCluster":
                                    return 1
                            if type == "blendShape":
                                if cmds.objectType(histItem) == "blendShape":
                                    return 2
                except:
                    return -1
        return False
    
                    
    def applyMorphDeformer(self, morphGeo, targetGeo, *args):
        """ Apply morphDeform from morphGeo(FaceToRivet) to targetGeo(Source)
            Rename and Parent to Models_Grp
        """
        targetList = cmds.ls(targetGeo, dag=True, shapes=True)
        targetShape = targetList[0]
        targetOrig = self.findOrig(targetList)
        if not targetOrig:
            cmds.delete(cmds.cluster(targetGeo, name="ToOrig_ClsTemp"))
            targetList = cmds.ls(targetGeo, dag=True, shapes=True)
            targetOrig = self.findOrig(targetList)
        morphDeformer = cmds.deformer(morphGeo, type="morph")[0]
        cmds.setAttr(morphDeformer+".morphMode", 1)
        cmds.setAttr(morphDeformer+".useComponentLookup", 1)
        cmds.setAttr(morphDeformer+".morphSpace", 0)
        cmds.connectAttr(targetShape+".worldMesh[0]", morphDeformer+".morphTarget[0]")
        componentMatchNode = cmds.createNode("componentMatch")
        cmds.connectAttr(componentMatchNode+".componentLookup", morphDeformer+".componentLookupList[0].componentLookup")
        morphOrigOutMesh = cmds.listConnections(morphDeformer+".originalGeometry[0]", source=True, destination=False, plugs=True)[0]
        cmds.connectAttr(morphOrigOutMesh, componentMatchNode+".inputGeometry")
        cmds.connectAttr(targetOrig+".outMesh", componentMatchNode+".targetGeometry")
        #Renaming
        hist = cmds.listHistory(morphGeo)
        morphList = cmds.ls(hist, type="morph")[0]
        toRivetName = dpUtils.extractSuffix(morphGeo)
        if "|" in toRivetName:
            toRivetName = toRivetName[toRivetName.rfind("|")+1:]
        morphNode = cmds.rename(morphList, toRivetName+"_Mrp")
        componentMatchNode = cmds.listConnections(morphNode+".componentLookupList[0].componentLookup")[0]
        cmds.rename(componentMatchNode, toRivetName+"_CpM")
        # Parent in modelsGrp
        modelGrp = dpUtils.getNodeByMessage("modelsGrp")
        if modelGrp:
            cmds.parent(morphGeo, modelGrp)


    def applyWrapDeformer(self, wrapGeo, targetGeo, *args):
        """ Apply wrapDeformer from wrapGeo(FaceToRivet) to targetGeo(Source)
            Rename and Parent to Models_Grp
        """
        cmds.select([wrapGeo, targetGeo])
        mel.eval("CreateWrap;")
        hist = cmds.listHistory(wrapGeo)
        wrapList = cmds.ls(hist, type="wrap")[0]
        # Renaming
        toRivetName = dpUtils.extractSuffix(wrapGeo)
        if "|" in toRivetName:
            toRivetName = toRivetName[toRivetName.rfind("|")+1:]
        wrapNode = cmds.rename(wrapList, toRivetName+"_Wrp")
        baseShape = cmds.listConnections(wrapNode+".basePoints")[0]
        baseShape = cmds.rename(baseShape, toRivetName+"_Base")
        self.dpUIinst.ctrls.setLockHide([baseShape], ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"], True, False, True)
        # Remove from displayLayers
        cmds.editDisplayLayerMembers("defaultLayer", baseShape, noRecurse=False)
        # Parent in modelsGrp
        modelGrp = dpUtils.getNodeByMessage("modelsGrp")
        if modelGrp:
            cmds.parent(wrapGeo, baseShape, modelGrp)
        return wrapGeo


    def findOrig(self, geoList, *args):
        """ Return the orig of the shapeList
        """
        if geoList:
            for item in geoList:
                if item.endswith("Orig"):
                    return item
                

    def checkMayaVersion(self, *args):
        """ Get Maya's version installed to compare with the minimalVersionRequired (2022.3)
            If the installed version is above the minimal it returns True, otherwise False
        """ 
        mayaVersion = cmds.about(installedVersion=True)
        installedVersion = float(mayaVersion.split(" ")[-1])
        minimalVersion = float(self.mayaMinimalVersion)
        if installedVersion > minimalVersion:
            return True
        else:
            return False
