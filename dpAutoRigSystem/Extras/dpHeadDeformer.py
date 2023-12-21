# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils

# global variables to this module:    
CLASS_NAME = "HeadDeformer"
TITLE = "m051_headDef"
DESCRIPTION = "m052_headDefDesc"
ICON = "/Icons/dp_headDeformer.png"

DP_HEADDEFORMER_VERSION = 2.15


class HeadDeformer(object):
    def __init__(self, dpUIinst, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.ctrls = dpControls.ControlClass(self.dpUIinst)
        self.headCtrl = None
        self.wellDone = True
        # call main function
        self.dpHeadDeformer(self)
    
    
    def dpHeadDeformerUI(self, *args):
        """ dpDeformer prompt dialog to get the name of the deformer
        """
        result = cmds.promptDialog(title="dpHeadDeformer", message="Enter Name:", text=self.dpUIinst.lang["c024_head"], button=["OK", "Cancel"], defaultButton="OK", cancelButton="Cancel", dismissString="Cancel")
        if result == "OK":
            dialogName = cmds.promptDialog(query=True, text=True)
            dialogName = dialogName[0].upper() + dialogName[1:]
            return dialogName
        elif result is None:
            return None


    def addDeformerInName(self, deformerName, deformerIn, *args):
        """ When the flag deformerIn is True, it will add the word Deformer as suffix. If it's false, it will maintain the name or take off Deformer in the name.
        """
        if deformerName:
            if deformerIn == True:
                if not "Deformer" in deformerName:
                    deformerName = deformerName+"Deformer"
                return deformerName
            if deformerIn == False:
                if "Deformer" in deformerName:
                    deformerName = deformerName.replace("Deformer", "")
                return deformerName+"_"


    def dpHeadDeformer(self, *args):
        """ Create the arrow curve and deformers (squash and bends).
        """
        # defining variables
        dialogName = self.dpHeadDeformerUI()
        if dialogName == None:
            return
        deformerName = self.addDeformerInName(dialogName, True)
        symetryName = self.addDeformerInName(dialogName, False)
        subCtrlName = deformerName+"_Sub"
        centerSymmetryName = symetryName+self.dpUIinst.lang["c098_center"]+self.dpUIinst.lang["c101_symmetry"]
        topSymmetryName = symetryName+self.dpUIinst.lang["c099_top"]+self.dpUIinst.lang["c101_symmetry"]
        intensityName = symetryName+self.dpUIinst.lang["c049_intensity"]
        expandName = symetryName+self.dpUIinst.lang["c104_expand"]
        axisList = ["X", "Y", "Z"]
        
        # validating namming in order to be possible create more than one setup
        validName = dpUtils.validateName(deformerName+"_FFD", "FFD")
        numbering = validName.replace(deformerName, "")[:-4]
        if numbering:
            deformerName = deformerName+numbering
            subCtrlName = subCtrlName+numbering
            centerSymmetryName = centerSymmetryName+numbering
            topSymmetryName = topSymmetryName+numbering
        
        # get a list of selected items
        selList = cmds.ls(selection=True)       

        if selList:
            # lattice deformer
            latticeDefList = cmds.lattice(name=deformerName+"_FFD", divisions=(6, 6, 6), ldivisions=(6, 6, 6), outsideLattice=2, outsideFalloffDistance=1, objectCentered=True) #[Deformer/Set, Lattice, Base], mode=falloff
            latticePointsList = latticeDefList[1]+".pt[0:5][2:5][0:5]"
            
            # store initial scaleY in order to avoid lattice rotation bug on non frozen transformations
            bBoxMaxY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMax.boundingBoxMaxY")
            bBoxMinY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMin.boundingBoxMinY")
            initialSizeY = bBoxMaxY-bBoxMinY
            
            # force rotate zero to lattice in order to avoid selected non froozen transformations
            for axis in axisList:
                cmds.setAttr(latticeDefList[1]+".rotate"+axis, 0)
                cmds.setAttr(latticeDefList[2]+".rotate"+axis, 0)
            cmds.setAttr(latticeDefList[1]+".scaleY", initialSizeY)
            cmds.setAttr(latticeDefList[2]+".scaleY", initialSizeY)
            
            # getting size and distances from Lattice Bounding Box
            bBoxMaxY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMax.boundingBoxMaxY")
            bBoxMinY = cmds.getAttr(latticeDefList[2]+".boundingBox.boundingBoxMin.boundingBoxMinY")
            bBoxSize = bBoxMaxY - bBoxMinY
            bBoxMidY = bBoxMinY + (bBoxSize*0.5)
            
            # twist deformer
            twistDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Twist", type="twist") #[Deformer, Handle]
            cmds.setAttr(twistDefList[0]+".lowBound", 0)
            cmds.setAttr(twistDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(twistDefList[1]+".ty", bBoxMinY)
            
            # squash deformer
            squashDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Squash", type="squash") #[Deformer, Handle]
            cmds.setAttr(squashDefList[0]+".highBound", 0.5*bBoxSize)
            cmds.setAttr(squashDefList[0]+".startSmoothness", 1)
            cmds.setAttr(squashDefList[1]+".ty", bBoxMidY)
            
            # side bend deformer
            sideBendDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Side_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(sideBendDefList[0]+".lowBound", 0)
            cmds.setAttr(sideBendDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(sideBendDefList[1]+".ty", bBoxMinY)
            
            # front bend deformer
            frontBendDefList = cmds.nonLinear(latticePointsList, name=deformerName+"_Front_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(frontBendDefList[0]+".lowBound", 0)
            cmds.setAttr(frontBendDefList[0]+".highBound", bBoxSize)
            cmds.setAttr(frontBendDefList[1]+".ry", -90)
            cmds.setAttr(frontBendDefList[1]+".ty", bBoxMinY)
            
            # fix deform transforms scale to 1
            defHandleList = [twistDefList[1], squashDefList[1], sideBendDefList[1], frontBendDefList[1]]
            for defHandle in defHandleList:
                for axis in axisList:
                    cmds.setAttr(defHandle+".scale"+axis, 1)
            
            # arrow control curve
            arrowCtrl = self.ctrls.cvControl("id_053_HeadDeformer", deformerName+"_Ctrl", 0.25*bBoxSize, d=0)

            # sub control curve
            subCtrl = self.ctrls.cvControl("id_097_HeadDeformerSub", subCtrlName+"_Ctrl", 0.5*bBoxSize, d=0)
            subCtrlShape = cmds.listRelatives(subCtrl, shapes=True)[0]
            
            # add control intensite and calibrate attributes
            for axis in axisList:
                cmds.addAttr(arrowCtrl, longName=intensityName+axis, attributeType='float', defaultValue=1)
                cmds.setAttr(arrowCtrl+"."+intensityName+axis, edit=True, keyable=False, channelBox=True)
            cmds.addAttr(arrowCtrl, longName=expandName, attributeType='float', min=0, defaultValue=1, max=10, keyable=True)
            cmds.addAttr(arrowCtrl, longName="calibrateX", attributeType='float', defaultValue=100/(3*bBoxSize), keyable=False)
            cmds.addAttr(arrowCtrl, longName="calibrateY", attributeType='float', defaultValue=300/bBoxSize, keyable=False)
            cmds.addAttr(arrowCtrl, longName="calibrateZ", attributeType='float', defaultValue=100/(3*bBoxSize), keyable=False)
            cmds.addAttr(arrowCtrl, longName="calibrateReduce", attributeType='float', defaultValue=100, keyable=False)
            cmds.addAttr(arrowCtrl, longName="subControlDisplay", attributeType='long', min=0, max=1, defaultValue=0)
            cmds.setAttr(arrowCtrl+".subControlDisplay", edit=True, keyable=False, channelBox=True)
            
            # multiply divide in order to intensify influences
            calibrateMD = cmds.createNode("multiplyDivide", name=deformerName+"_Calibrate_MD")
            calibrateReduceMD = cmds.createNode("multiplyDivide", name=deformerName+"_CalibrateReduce_MD")
            intensityMD = cmds.createNode("multiplyDivide", name=deformerName+"_"+intensityName.capitalize()+"_MD")
            twistMD = cmds.createNode("multiplyDivide", name=deformerName+"_Twist_MD")
            cmds.setAttr(twistMD+".input2Y", -1)
            cmds.setAttr(calibrateReduceMD+".operation", 2)

            # create a remapValue node instead of a setDrivenKey
            remapV = cmds.createNode("remapValue", name=deformerName+"_Squash_RmV")
            cmds.setAttr(remapV+".inputMin", -0.25*bBoxSize)
            cmds.setAttr(remapV+".inputMax", 0.5*bBoxSize)
            cmds.setAttr(remapV+".outputMin", -1*bBoxSize)
            cmds.setAttr(remapV+".outputMax", -0.25*bBoxSize)            
            cmds.setAttr(remapV+".value[2].value_Position", 0.149408)
            cmds.setAttr(remapV+".value[2].value_FloatValue", 0.128889)
            cmds.setAttr(remapV+".value[3].value_Position", 0.397929)
            cmds.setAttr(remapV+".value[3].value_FloatValue", 0.742222)
            cmds.setAttr(remapV+".value[4].value_Position", 0.60355)
            cmds.setAttr(remapV+".value[4].value_FloatValue", 0.951111)
            for v in range(0, 5):
                cmds.setAttr(remapV+".value["+str(v)+"].value_Interp", 3) #spline
            
            # connections
            for axis in axisList:
                cmds.connectAttr(arrowCtrl+"."+intensityName+axis, calibrateMD+".input1"+axis, force=True)
                cmds.connectAttr(arrowCtrl+".calibrate"+axis, calibrateReduceMD+".input1"+axis, force=True)
                cmds.connectAttr(arrowCtrl+".calibrateReduce", calibrateReduceMD+".input2"+axis, force=True)
                cmds.connectAttr(calibrateReduceMD+".output"+axis, calibrateMD+".input2"+axis, force=True)
                cmds.connectAttr(arrowCtrl+".translate"+axis, intensityMD+".input1"+axis, force=True)
                cmds.connectAttr(calibrateMD+".output"+axis, intensityMD+".input2"+axis, force=True)
            cmds.connectAttr(intensityMD+".outputX", sideBendDefList[1]+".curvature", force=True)
            cmds.connectAttr(intensityMD+".outputY", squashDefList[1]+".factor", force=True)
            cmds.connectAttr(intensityMD+".outputZ", frontBendDefList[1]+".curvature", force=True)
            cmds.connectAttr(arrowCtrl+".ry", twistMD+".input1Y", force=True)
            cmds.connectAttr(twistMD+".outputY", twistDefList[1]+".endAngle", force=True)
            # change squash to be more cartoon
            cmds.connectAttr(intensityMD+".outputY", remapV+".inputValue", force=True)
            cmds.connectAttr(remapV+".outValue", squashDefList[0]+".lowBound", force=True)
            cmds.connectAttr(arrowCtrl+"."+expandName, squashDefList[0]+".expand", force=True)
            # fix side values
            for axis in axisList:
                unitConvNode = cmds.listConnections(intensityMD+".output"+axis, destination=True)[0]
                if unitConvNode:
                    if cmds.objectType(unitConvNode) == "unitConversion":
                        cmds.setAttr(unitConvNode+".conversionFactor", 1)
            cmds.connectAttr(arrowCtrl+".subControlDisplay", subCtrlShape+".visibility")
            self.ctrls.setLockHide([arrowCtrl], ['rx', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
            
            # create symmetry setup
            centerClusterList = cmds.cluster(latticeDefList[1]+".pt[0:5][2:3][0:5]", relative=True, name=centerSymmetryName+"_Cls") #[Cluster, Handle]
            topClusterList = cmds.cluster(latticeDefList[1]+".pt[0:5][2:5][0:5]", relative=True, name=topSymmetryName+"_Cls")
            clustersZeroList = dpUtils.zeroOut([centerClusterList[1], topClusterList[1]])
            cmds.delete(cmds.parentConstraint(centerClusterList[1], clustersZeroList[1]))
            clusterGrp = cmds.group(clustersZeroList, name=deformerName+"_"+self.dpUIinst.lang["c101_symmetry"]+"_Grp")
            # arrange lattice deform points percent
            cmds.percent(topClusterList[0], [latticeDefList[1]+".pt[0:5][2][0]", latticeDefList[1]+".pt[0:5][2][1]", latticeDefList[1]+".pt[0:5][2][2]", latticeDefList[1]+".pt[0:5][2][3]", latticeDefList[1]+".pt[0:5][2][4]", latticeDefList[1]+".pt[0:5][2][5]"], value=0.5)
            # symmetry controls
            centerSymmetryCtrl = self.ctrls.cvControl("id_068_Symmetry", centerSymmetryName+"_Ctrl", bBoxSize, d=0, rot=(-90, 0, 90))
            topSymmetryCtrl = self.ctrls.cvControl("id_068_Symmetry", topSymmetryName+"_Ctrl", bBoxSize, d=0, rot=(0, 90, 0))
            symmetryCtrlZeroList = dpUtils.zeroOut([centerSymmetryCtrl, topSymmetryCtrl])
            for axis in axisList:
                cmds.connectAttr(centerSymmetryCtrl+".translate"+axis, centerClusterList[1]+".translate"+axis, force=True)
                cmds.connectAttr(centerSymmetryCtrl+".rotate"+axis, centerClusterList[1]+".rotate"+axis, force=True)
                cmds.connectAttr(centerSymmetryCtrl+".scale"+axis, centerClusterList[1]+".scale"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".translate"+axis, topClusterList[1]+".translate"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".rotate"+axis, topClusterList[1]+".rotate"+axis, force=True)
                cmds.connectAttr(topSymmetryCtrl+".scale"+axis, topClusterList[1]+".scale"+axis, force=True)
            
            # create groups
            arrowCtrlGrp = cmds.group(arrowCtrl, name=arrowCtrl+"_Grp")
            dpUtils.zeroOut([arrowCtrl])
            offsetGrp = cmds.group(name=deformerName+"_Offset_Grp", empty=True)
            dataGrp = cmds.group(name=deformerName+"_Data_Grp", empty=True)
            cmds.delete(cmds.parentConstraint(latticeDefList[2], arrowCtrlGrp, maintainOffset=False))
            arrowCtrlHeight = bBoxMaxY + (bBoxSize*0.5)
            cmds.setAttr(arrowCtrlGrp+".ty", arrowCtrlHeight)
            cmds.delete(cmds.parentConstraint(latticeDefList[2], offsetGrp, maintainOffset=False))
            cmds.delete(cmds.parentConstraint(latticeDefList[2], symmetryCtrlZeroList[0], maintainOffset=False))
            cmds.delete(cmds.parentConstraint(latticeDefList[2], symmetryCtrlZeroList[1], maintainOffset=False))
            topSymmetryHeight = cmds.getAttr(symmetryCtrlZeroList[1]+".ty") - (bBoxSize*0.3)
            cmds.setAttr(symmetryCtrlZeroList[1]+".ty", topSymmetryHeight)
            cmds.parent(symmetryCtrlZeroList, arrowCtrlGrp)
            latticeGrp = cmds.group(name=latticeDefList[1]+"_Grp", empty=True)
            cmds.parent(latticeDefList[1], latticeDefList[2], latticeGrp)
            subCtrlGrp = cmds.group(subCtrl, name=subCtrl+"_Grp")
            cmds.matchTransform(subCtrlGrp, subCtrl, pivots=True)
            cmds.delete(cmds.parentConstraint(latticeDefList[1], subCtrlGrp, maintainOffset=False))
            cmds.parent(arrowCtrlGrp, subCtrl)
            cmds.parentConstraint(subCtrl, dataGrp, maintainOffset=True, name=dataGrp+"_PaC")
            cmds.scaleConstraint(subCtrl, dataGrp, maintainOffset=True, name=dataGrp+"_ScC")
            # fix topSymmetryCluster pivot
            topSymmetryCtrlPos = cmds.xform(symmetryCtrlZeroList[1], query=True, rotatePivot=True, worldSpace=True)
            cmds.xform(topClusterList[1], rotatePivot=(topSymmetryCtrlPos[0], topSymmetryCtrlPos[1], topSymmetryCtrlPos[2]), worldSpace=True)
            
            # try to integrate to Head_Head_Ctrl
            allTransformList = cmds.ls(selection=False, type="transform")
            headCtrlList = self.ctrls.getControlNodeById("id_093_HeadSub")
            if headCtrlList:
                if len(headCtrlList) > 1:
                    mel.eval("warning" + "\"" + self.dpUIinst.lang["i075_moreOne"] + " Head control.\"" + ";")
                else:
                    self.headCtrl = headCtrlList[0]
            if self.headCtrl:
                # correcting topSymetry pivot
                cmds.matchTransform(topSymmetryCtrl, self.headCtrl, pivots=True)
                cmds.matchTransform(topClusterList[1], self.headCtrl, pivots=True)
                # setup hierarchy
                headCtrlPosList = cmds.xform(self.headCtrl, query=True, rotatePivot=True, worldSpace=True)
                cmds.xform(dataGrp, translation=(headCtrlPosList[0], headCtrlPosList[1], headCtrlPosList[2]), worldSpace=True)
                # influence controls
                self.upperJawCtrl = None
                toHeadDefCtrlList = []
                for item in allTransformList:
                    if cmds.objExists(item+".controlID"):
                        if cmds.getAttr(item+".controlID") == "id_024_HeadJaw":
                            toHeadDefCtrlList.append(item)
                        elif cmds.getAttr(item+".controlID") == "id_027_HeadLipCorner":
                            toHeadDefCtrlList.append(item)
                        elif cmds.getAttr(item+".controlID") == "id_069_HeadUpperJaw":
                            self.upperJawCtrl = item
                            upperJawCtrlShapeList = cmds.listRelatives(item, children=True, shapes=True)
                            if upperJawCtrlShapeList:
                                for upperJawShape in upperJawCtrlShapeList:
                                    toHeadDefCtrlList.append(upperJawShape)
                if self.upperJawCtrl:
                    upperJawChildrenList = cmds.listRelatives(self.upperJawCtrl, children=True, allDescendents=True, type="transform")
                    if upperJawChildrenList:
                        for upperJawChild in upperJawChildrenList:
                            if cmds.objExists(upperJawChild+".controlID"):
                                if not cmds.getAttr(upperJawChild+".controlID") == "id_052_FacialFace":
                                    if not cmds.getAttr(upperJawChild+".controlID") == "id_029_SingleIndSkin":
                                        if not cmds.getAttr(upperJawChild+".controlID") == "id_054_SingleMain":
                                            toHeadDefCtrlList.append(upperJawChild)
                                        else:
                                            singleMainShapeList = cmds.listRelatives(upperJawChild, children=True, shapes=True)
                                            if singleMainShapeList:
                                                for mainShape in singleMainShapeList:
                                                    toHeadDefCtrlList.append(mainShape)
                if toHeadDefCtrlList:
                    useComponentTag = cmds.optionVar(query="deformationUseComponentTags")
                    for item in toHeadDefCtrlList:
                        if useComponentTag:
                            cmds.deformer(deformerName+"_FFD", edit=True, geometry=item)
                        else:
                            cmds.sets(item, include=deformerName+"_FFDSet")
                cmds.parent(subCtrlGrp, self.headCtrl)

            else:
                mel.eval("warning" + "\"" + self.dpUIinst.lang["e020_notFoundHeadCtrl"] + "\"" + ";")
                self.wellDone = False
            
            cmds.parent(squashDefList[1], sideBendDefList[1], frontBendDefList[1], twistDefList[1], offsetGrp)
            cmds.parent(offsetGrp, clusterGrp, latticeGrp, dataGrp)
            
            # try to integrate to Scalable_Grp
            for item in allTransformList:
                if cmds.objExists(item+".masterGrp") and cmds.getAttr(item+".masterGrp") == 1:
                    scalableGrp = cmds.listConnections(item+".scalableGrp")[0]
                    cmds.parent(dataGrp, scalableGrp)
                    break
            
            # try to change deformers to get better result
            cmds.scale(1.25, 1.25, 1.25, offsetGrp)
            
            # colorize
            self.ctrls.colorShape([arrowCtrl, subCtrl, centerSymmetryCtrl, topSymmetryCtrl], "cyan")

            # if there's Jaw in the deformerName it will configure rotate and delete symetries setup
            if "Jaw" in subCtrl:
                print(toHeadDefCtrlList)
                cmds.setAttr(subCtrlGrp+".rotateX", 145)
                cmds.delete(clusterGrp, symmetryCtrlZeroList)
            
            # finish selection the arrow control
            cmds.select(arrowCtrl)
            if self.wellDone:
                print(self.dpUIinst.lang["i179_addedHeadDef"])
        
        else:
            mel.eval("warning" + "\"" + self.dpUIinst.lang["i034_notSelHeadDef"] + "\"" + ";")