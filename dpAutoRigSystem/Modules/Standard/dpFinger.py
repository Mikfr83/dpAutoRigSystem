# importing libraries:
from maya import cmds
from ..Base import dpBaseStandard
from ..Base import dpBaseLayout

# global variables to this module:
CLASS_NAME = "Finger"
TITLE = "m007_finger"
DESCRIPTION = "m008_fingerDesc"
ICON = "/Icons/dp_finger.png"

DP_FINGER_VERSION = 2.2


class Finger(dpBaseStandard.BaseStandard, dpBaseLayout.BaseLayout):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseStandard.BaseStandard.__init__(self, *args, **kwargs)
        self.correctiveCtrlGrpList = []


    def createModuleLayout(self, *args):
        dpBaseStandard.BaseStandard.createModuleLayout(self)
        dpBaseLayout.BaseLayout.basicModuleLayout(self)


    def createGuide(self, *args):
        dpBaseStandard.BaseStandard.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long', minValue=2, defaultValue=2)
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 1)
        cmds.addAttr(self.moduleGrp, longName="corrective", attributeType='bool')

        self.cvJointLoc1 = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc2", r=0.25, d=1, guide=True)
        cmds.parent(self.cvJointLoc, self.cvJointLoc1, relative=True)
        cmds.setAttr(self.cvJointLoc+".translateZ", 1)
        cmds.setAttr(self.cvJointLoc+".translateX", -0.01)
        cmds.setAttr(self.cvJointLoc+".rotateY", -1)
        self.jGuide = cmds.joint(name=self.guideName+"_JGuide2", radius=0.001)
        cmds.setAttr(self.jGuide+".template", 1)
        cmds.parent(self.jGuide, self.jGuide1)
        self.ctrls.directConnect(self.cvJointLoc, self.jGuide, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.2, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])

        cmds.parent(self.cvJointLoc1, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        self.ctrls.directConnect(self.cvJointLoc1, self.jGuide1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # include nodes into net
        self.addNodeToGuideNet([self.cvJointLoc1, self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointLoc2", "JointEnd"])

        # change the number of phalanges to 3:
        self.changeJointNumber(3)

        # create a base cvLoc to start the finger joints:
        self.cvBaseJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointLoc0", r=0.2, d=1, guide=True)
        cmds.setAttr(self.cvBaseJoint+".translateZ", -1)
        cmds.setAttr(self.cvBaseJoint+".rotateZ", lock=True)
        cmds.parent(self.cvBaseJoint, self.moduleGrp)
        self.addNodeToGuideNet([self.cvBaseJoint], ["JointLoc0"])

        # transform cvLocs in order to put as a good finger guide:
        cmds.setAttr(self.moduleGrp+".rotateX", 90)
        cmds.setAttr(self.moduleGrp+".rotateZ", 90)


    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        self.utils.useDefaultRenderLayer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            try:
                self.enteredNJoints = cmds.intField(self.nJointsIF, query=True, value=True)
            except:
                return
        else:
            self.enteredNJoints = enteredNJoints
        if self.enteredNJoints >= 2:
            # get the number of joints existing:
            self.currentNJoints = cmds.getAttr(self.moduleGrp+".nJoints")
            # start analisys the difference between values:
            if self.enteredNJoints != self.currentNJoints:
                # unparent temporarely the Ends:
                self.cvEndJoint = self.guideName+"_JointEnd"
                cmds.parent(self.cvEndJoint, world=True)
                self.jGuideEnd = (self.guideName+"_JGuideEnd")
                cmds.parent(self.jGuideEnd, world=True)
                # verify if the nJoints is greather or less than the current
                if self.enteredNJoints > self.currentNJoints:
                    for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                        # create another N cvJointLoc:
                        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc"+str(n), r=0.2, d=1, guide=True)
                        # set its nJoint value as n:
                        cmds.setAttr(self.cvJointLoc+".nJoint", n)
                        # parent it to the lastGuide:
                        cmds.parent(self.cvJointLoc, self.guideName+"_JointLoc"+str(n-1), relative=True)
                        cmds.setAttr(self.cvJointLoc+".translateZ", 1)
                        cmds.setAttr(self.cvJointLoc+".rotateY", -1)
                        # create a joint to use like an arrowLine:
                        self.jGuide = cmds.joint(name=self.guideName+"_JGuide"+str(n), radius=0.001)
                        cmds.setAttr(self.jGuide+".template", 1)
                        cmds.parent(self.jGuide, self.guideName+"_JGuide"+str(n-1))
                        self.ctrls.directConnect(self.cvJointLoc, self.jGuide, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
                        self.addNodeToGuideNet([self.cvJointLoc], ["JointLoc"+str(n)])
                elif self.enteredNJoints < self.currentNJoints:
                    # re-define cvEndJoint:
                    self.cvJointLoc = self.guideName+"_JointLoc"+str(self.enteredNJoints)
                    self.cvEndJoint = self.guideName+"_JointEnd"
                    self.jGuide = self.guideName+"_JGuide"+str(self.enteredNJoints)
                    # re-parent the children guides:
                    childrenGuideBellowList = self.utils.getGuideChildrenList(self.cvJointLoc)
                    if childrenGuideBellowList:
                        for childGuide in childrenGuideBellowList:
                            cmds.parent(childGuide, self.cvJointLoc)
                    # delete difference of nJoints:
                    cmds.delete(self.guideName+"_JointLoc"+str(self.enteredNJoints+1))
                    cmds.delete(self.guideName+"_JGuide"+str(self.enteredNJoints+1))
                    for j in range(self.enteredNJoints+1, self.currentNJoints+1):
                        self.removeAttrFromGuideNet(["JointLoc"+str(j)])
                # re-parent cvEndJoint:
                cmds.parent(self.cvEndJoint, self.cvJointLoc)
                cmds.setAttr(self.cvEndJoint+".tz", 1.3)
                cmds.parent(self.jGuideEnd, self.jGuide)
                # actualise the nJoints in the moduleGrp:
                cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
                self.currentNJoints = self.enteredNJoints
                # re-build the preview mirror:
                dpBaseLayout.BaseLayout.createPreviewMirror(self)
            cmds.select(self.moduleGrp)
        else:
            self.changeJointNumber(2)


    def getCalibratePresetList(self, s, *args):
        """ Returns the calibration preset and invert lists for finger joints.
        """
        invertList = None
        presetList = [{}, {"calibrateTX":1}]
        if s == 1:
           invertList = [[], ["invertTX"]]
        return presetList, invertList


    def rigModule(self, *args):
        dpBaseStandard.BaseStandard.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            self.addCorrective = self.getModuleAttr("corrective")
            # declaring lists to send information for integration:
            self.scalableGrpList, self.ikCtrlZeroList = [], []
            # run for all sides
            for s, side in enumerate(self.sideList):
                self.skinJointList = []
                self.base = side+self.userGuideName+'_Guide_Base'
                if self.addArticJoint:
                    if self.addCorrective:
                        # corrective controls group
                        self.correctiveCtrlsGrp = cmds.group(name=side+self.userGuideName+"_Corrective_Grp", empty=True)
                        self.correctiveCtrlGrpList.append(self.correctiveCtrlsGrp)
                        phalangeCalibratePresetList, invertList = self.getCalibratePresetList(s)
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.nJoints+1):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.userGuideName+"_Guide_JointLoc"+str(n)
                    self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                    self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.userGuideName+"_%02d_Jnt"%(n), scaleCompensate=False)
                    self.skinJointList.append(self.jnt)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.utils.setJointLabel(self.jnt, s+self.jointLabelAdd, 18, self.userGuideName+"_%02d"%(n))
                    # create a control:
                    if n == 1:
                        self.fingerCtrl = self.ctrls.cvControl("id_015_FingerMain", ctrlName=side+self.userGuideName+"_%02d_Ctrl"%(n), r=(self.ctrlRadius * 2.0), d=self.curveDegree, rot=(0, 0, -90), guideSource=self.guideName+"_JointLoc"+str(n))
                        cmds.setAttr(self.fingerCtrl+".rotateOrder", 1)
                        self.utils.originedFrom(objName=self.fingerCtrl, attrString=self.base+";"+self.guide)   
                        # edit the mirror shape to a good direction of controls:
                        if s == 1:
                            if self.mirrorAxis == 'X':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            elif self.mirrorAxis == 'Y':
                                cmds.setAttr(self.fingerCtrl+'.rotateY', 180)
                            elif self.mirrorAxis == 'Z':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            elif self.mirrorAxis == 'XY':
                                cmds.setAttr(self.fingerCtrl+'.rotateX', 180)
                            elif self.mirrorAxis == 'XYZ':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            cmds.makeIdentity(self.fingerCtrl, apply=True, translate=False, rotate=True, scale=False)
                        # scale compensate attribute:
                        if not cmds.objExists(self.fingerCtrl+'.ikFkBlend'):
                            cmds.addAttr(self.fingerCtrl, longName="ikFkBlend", attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                            self.ikFkRevNode = cmds.createNode("reverse", name=side+self.userGuideName+"_ikFk_Rev")
                            self.toIDList.append(self.ikFkRevNode)
                            cmds.connectAttr(self.fingerCtrl+".ikFkBlend", self.ikFkRevNode+".inputX", force=True)
                        if not cmds.objExists(self.fingerCtrl+'.scaleCompensate'):
                            cmds.addAttr(self.fingerCtrl, longName="scaleCompensate", attributeType='short', minValue=0, defaultValue=1, maxValue=1, keyable=False)
                            cmds.setAttr(self.fingerCtrl+".scaleCompensate", channelBox=True)
                            scaleCompensateMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_%02d_ScaleCompensate_MD"%(n))
                            self.scaleCompensateCond = cmds.createNode("condition", name=side+self.userGuideName+"_%02d_ScaleCompensate_Cnd"%(n))
                            self.toIDList.extend([scaleCompensateMD, self.scaleCompensateCond])
                            cmds.connectAttr(self.fingerCtrl+".scaleCompensate", scaleCompensateMD+".input1X", force=True)
                            cmds.connectAttr(self.ikFkRevNode+".outputX", scaleCompensateMD+".input2X", force=True)
                            cmds.connectAttr(scaleCompensateMD+".outputX", self.scaleCompensateCond+".firstTerm", force=True)
                            cmds.setAttr(self.scaleCompensateCond+".secondTerm", 1)
                            cmds.setAttr(self.scaleCompensateCond+".colorIfFalseR", 0)
                            cmds.connectAttr(self.fingerCtrl+".scaleCompensate", self.scaleCompensateCond+".colorIfTrueR", force=True)
                            cmds.connectAttr(self.scaleCompensateCond+".outColorR", self.jnt+".segmentScaleCompensate", force=True)
                            cmds.connectAttr(self.scaleCompensateCond+".outColorR", self.skinJointList[0]+".segmentScaleCompensate", force=True)
                    else:
                        self.fingerCtrl = self.ctrls.cvControl("id_016_FingerFk", ctrlName=side+self.userGuideName+"_%02d_Ctrl"%(n), r=self.ctrlRadius, d=self.curveDegree, guideSource=self.guideName+"_JointLoc"+str(n))
                        cmds.setAttr(self.fingerCtrl+".rotateOrder", 1)
                        if n == self.nJoints:
                            self.utils.originedFrom(objName=self.fingerCtrl, attrString=self.guide+";"+self.cvEndJoint+";"+self.radiusGuide)
                        else:
                            self.utils.originedFrom(objName=self.fingerCtrl, attrString=self.guide)
                        if n == 0:
                            if self.nJoints == 2:
                                # problably we are creating the first control to a thumb
                                cmds.scale(2, 2, 2, self.fingerCtrl, relative=True)
                                cmds.makeIdentity(self.fingerCtrl, apply=True)
                            else:
                                # problably we are creating other base controls
                                cmds.scale(2, 0.5, 1, self.fingerCtrl, relative=True)
                                cmds.makeIdentity(self.fingerCtrl, apply=True)

                    # scaleCompensate attribute:
                    if n > 1:
                        cmds.connectAttr(self.scaleCompensateCond+".outColorR", self.jnt+".segmentScaleCompensate", force=True)

                    # hide visibility attribute:
                    cmds.setAttr(self.fingerCtrl+'.visibility', keyable=False)
                    # put another group over the control in order to use this to connect values from mainFingerCtrl:
                    self.sdkGrp = cmds.group(self.fingerCtrl, name=side+self.userGuideName+"_%02d_SDK_Grp"%(n))
                    self.utils.addCustomAttr([self.sdkGrp], self.utils.ignoreTransformIOAttr)
                    if n == 1:
                        # change pivot of this group to control pivot:
                        pivotPos = cmds.xform(self.fingerCtrl, query=True, worldSpace=True, rotatePivot=True)
                        cmds.setAttr(self.sdkGrp+'.rotatePivotX', pivotPos[0])
                        cmds.setAttr(self.sdkGrp+'.rotatePivotY', pivotPos[1])
                        cmds.setAttr(self.sdkGrp+'.rotatePivotZ', pivotPos[2])
                    # position and orientation of joint and control:
                    tempDel = cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False)
                    cmds.delete(tempDel)
                    tempDel = cmds.parentConstraint(self.guide, self.sdkGrp, maintainOffset=False)
                    cmds.delete(tempDel)
                    # zeroOut controls:
                    self.zeroGrp = self.utils.zeroOut([self.sdkGrp])
                    
                    # grouping:
                    if n > 0:
                        if n == 1:
                            if not cmds.objExists(self.fingerCtrl+'.'+self.dpUIinst.lang['c021_showControls']):
                                cmds.addAttr(self.fingerCtrl, longName=self.dpUIinst.lang['c021_showControls'], attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                                self.ctrlShape0 = cmds.listRelatives(side+self.userGuideName+"_00_Ctrl", children=True, type='nurbsCurve')[0]
                                cmds.connectAttr(self.fingerCtrl+"."+self.dpUIinst.lang['c021_showControls'], self.ctrlShape0+".visibility", force=True)
                                cmds.setAttr(self.fingerCtrl+'.'+self.dpUIinst.lang['c021_showControls'], keyable=False, channelBox=True)
                            for j in range(1, self.nJoints+1):
                                cmds.addAttr(self.fingerCtrl, longName=self.dpUIinst.lang['c022_phalange']+str(j), attributeType='float', keyable=True)
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.userGuideName+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroGrp Group to the before ctrl:
                        self.fatherCtrl = side+self.userGuideName+"_%02d_Ctrl"%(n-1)
                        cmds.parent(self.zeroGrp, self.fatherCtrl, absolute=True)
                    # freeze joints rotation
                    cmds.makeIdentity(self.jnt, apply=True)
                    # create parent and scale constraints from ctrl to jnt:
                    cmds.delete(cmds.parentConstraint(self.fingerCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC"))
                    
                    # add articulationJoint:
                    if n > 0:
                        if self.addArticJoint:
                            if self.addCorrective:
                                correctiveNetList = [None]
                                correctiveNetList.append(self.setupCorrectiveNet(side+self.userGuideName+"_01_Ctrl", self.skinJointList[n-1], self.skinJointList[n], side+self.userGuideName+"_"+str(n)+"_PitchDown", 1, 1, -90))
                                articJntList = self.utils.articulationJoint(self.fatherJnt, self.jnt, 1, [(0.3*self.ctrlRadius, 0, 0)])
                                self.setupJcrControls(articJntList, s, self.jointLabelAdd, self.userGuideName+"_"+str(n), correctiveNetList, phalangeCalibratePresetList, invertList)
                                if s == 1:
                                    cmds.setAttr(articJntList[0]+".scaleX", -1)
                                    cmds.setAttr(articJntList[0]+".scaleY", -1)
                                    cmds.setAttr(articJntList[0]+".scaleZ", -1)
                            else:
                                articJntList = self.utils.articulationJoint(self.fatherJnt, self.jnt)
                                self.utils.setJointLabel(articJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_%02d_Jar"%(n))
                                cmds.connectAttr(self.scaleCompensateCond+".outColorR", articJntList[0]+".segmentScaleCompensate", force=True)
                    cmds.select(self.jnt)
                    
                    if n == self.nJoints:
                        # create end joint:
                        self.endJoint = cmds.joint(name=side+self.userGuideName+"_"+self.dpUIinst.jointEndAttr, radius=0.5)
                        self.utils.addJointEndAttr([self.endJoint])
                        cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                
                # make first phalange be leads from base finger control:
                cmds.parentConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.userGuideName+"_01_SDK_Zero_0_Grp"+"_PaC")
                cmds.scaleConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.userGuideName+"_01_SDK_Zero_0_Grp"+"_ScC")
                if self.nJoints != 2:
                    cmds.parentConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Jnt", maintainOffset=True, name=side+self.userGuideName+"_PaC")
                    cmds.scaleConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Jnt", maintainOffset=True, name=side+self.userGuideName+"_ScC")
                # connecting the attributes from control 1 to phalanges rotate:
                for n in range(1, self.nJoints+1):
                    self.fingerCtrl = side+self.userGuideName+"_01_Ctrl"
                    self.sdkGrp = side+self.userGuideName+"_%02d_SDK_Grp"%(n)
                    cmds.connectAttr(self.fingerCtrl+"."+self.dpUIinst.lang['c022_phalange']+str(n), self.sdkGrp+".rotateY", force=True)
                    if n > 1:
                        self.ctrlShape = cmds.listRelatives(side+self.userGuideName+"_%02d_Ctrl"%(n), children=True, type='nurbsCurve')[0]
                        cmds.connectAttr(self.fingerCtrl+"."+self.dpUIinst.lang['c021_showControls'], self.ctrlShape+".visibility", force=True)

                # ik and Fk setup
                if self.nJoints == 2:
                    dupIk = cmds.duplicate(self.skinJointList[0])[0]
                    dupFk = cmds.duplicate(self.skinJointList[0])[0]
                else:
                    dupIk = cmds.duplicate(self.skinJointList[1])[0]
                    dupFk = cmds.duplicate(self.skinJointList[1])[0]
                
                # hide ik and fk joints in order to be Rigger friendly while skinning
                cmds.setAttr(dupIk+".visibility", 0)
                cmds.setAttr(dupFk+".visibility", 0)
                
                # ik setup
                childrenIkList = cmds.listRelatives(dupIk, children=True, allDescendents=True, fullPath=True)
                if childrenIkList:
                    for child in childrenIkList:
                        if not cmds.objectType(child) == "joint":
                            cmds.delete(child)
                        if child.endswith("_Jax"):
                            cmds.delete(child)
                jointIkList = cmds.listRelatives(dupIk, children=True, allDescendents=True, fullPath=True)
                for jointNode in jointIkList:
                    if "_Jnt" in jointNode[jointNode.rfind("|"):]:
                        # set joint preferred angle
                        currentRY = cmds.getAttr(jointNode+".rotateY")
                        cmds.setAttr(jointNode+".rotateY", -90)
                        cmds.joint(jointNode, edit=True, setPreferredAngles=True)
                        cmds.setAttr(jointNode+".rotateY", currentRY)
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_Jnt", "_Ik_Jxt"))
                    elif "_"+self.dpUIinst.jointEndAttr in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_"+self.dpUIinst.jointEndAttr, "_Ik_"+self.dpUIinst.jointEndAttr))
                ikBaseJoint = cmds.rename(dupIk, dupIk.replace("_Jnt1", "_Ik_Jxt"))
                ikJointList = cmds.listRelatives(ikBaseJoint, children=True, allDescendents=True)
                ikJointList.append(ikBaseJoint)

                # Fk setup
                childrenFkList = cmds.listRelatives(dupFk, children=True, allDescendents=True, fullPath=True)
                if childrenFkList:
                    for child in childrenFkList:
                        if not cmds.objectType(child) == "joint":
                            cmds.delete(child)
                        if child.endswith("_Jax"):
                            cmds.delete(child)
                jointFkList = cmds.listRelatives(dupFk, children=True, allDescendents=True, fullPath=True)
                for jointNode in jointFkList:
                    if "_Jnt" in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_Jnt", "_Fk_Jxt"))
                    elif "_"+self.dpUIinst.jointEndAttr in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_"+self.dpUIinst.jointEndAttr, "_Fk_"+self.dpUIinst.jointEndAttr))
                fkBaseJoint = cmds.rename(dupFk, dupFk.replace("_Jnt2", "_Fk_Jxt"))
                fkJointList = cmds.listRelatives(fkBaseJoint, children=True, allDescendents=True)
                fkJointList.append(fkBaseJoint)

                # fk control drives fk joints
                for i, fkJoint in enumerate(fkJointList):
                    if not "_"+self.dpUIinst.jointEndAttr in fkJoint:
                        self.utils.clearDpArAttr([fkJoint])
                        fkCtrl = fkJoint.replace("_Fk_Jxt", "_Ctrl")
                        self.scaleCompensateCond = fkCtrl.replace("_Ctrl", "_ScaleCompensate_Cnd")
                        cmds.parentConstraint(fkCtrl, fkJoint, maintainOffset=True, name=fkJoint+"_PaC")
                        cmds.scaleConstraint(fkCtrl, fkJoint, maintainOffset=True, name=fkJoint+"_ScC")
                        cmds.setAttr(fkJoint+".segmentScaleCompensate", 0)
                        cmds.setAttr(fkCtrl+".rotateOrder", 1)

                # ik handle
                if self.nJoints >= 2:
                    if self.nJoints == 2:
                        ikHandleList = cmds.ikHandle(startJoint=side+self.userGuideName+"_00_Ik_Jxt", endEffector=side+self.userGuideName+"_%02d_Ik_Jxt"%(self.nJoints), solver="ikRPsolver", name=side+self.userGuideName+"_IKH")
                    else:
                        ikHandleList = cmds.ikHandle(startJoint=side+self.userGuideName+"_01_Ik_Jxt", endEffector=side+self.userGuideName+"_%02d_Ik_Jxt"%(self.nJoints), solver="ikRPsolver", name=side+self.userGuideName+"_IKH")
                    cmds.rename(ikHandleList[1], side+self.userGuideName+"_Eff")
                    endIkHandleList = cmds.ikHandle(startJoint=side+self.userGuideName+"_%02d_Ik_Jxt"%(self.nJoints), endEffector=side+self.userGuideName+"_Ik_"+self.dpUIinst.jointEndAttr, solver="ikSCsolver", name=side+self.userGuideName+"_EndIkHandle")
                    cmds.rename(endIkHandleList[1], side+self.userGuideName+"_End_Eff")
                    self.ikCtrl = self.ctrls.cvControl("id_017_FingerIk", ctrlName=side+self.userGuideName+"_Ik_Ctrl", r=(self.ctrlRadius * 0.3), d=self.curveDegree, guideSource=self.guideName+"_JointEnd")
                    cmds.addAttr(self.ikCtrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(self.ikCtrl+".twist", ikHandleList[0]+".twist", force=True)
                    cmds.setAttr(self.ikCtrl+".rotateOrder", 1)
                    self.ikCtrlZero = self.utils.zeroOut([self.ikCtrl])[0]
                    self.ikCtrlZeroList.append(self.ikCtrlZero)
                    cmds.delete(cmds.parentConstraint(self.skinJointList[-1], self.ikCtrlZero, maintainOffset=False))
                    cmds.delete(cmds.pointConstraint(self.cvEndJoint, self.ikCtrlZero, maintainOffset=False))
                    cmds.connectAttr(self.ikFkRevNode+".outputX", self.ikCtrlZero+".visibility", force=True)
                    for q in range(2, self.nJoints+1):
                        cmds.connectAttr(side+self.userGuideName+"_01_Ctrl.ikFkBlend", side+self.userGuideName+"_%02d_Ctrl.visibility"%(q), force=True)
                    cmds.parentConstraint(self.ikCtrl, ikHandleList[0], name=side+self.userGuideName+"_IKH_PaC", maintainOffset=True)
                    cmds.parentConstraint(self.ikCtrl, endIkHandleList[0], name=side+self.userGuideName+"_EndIkHandle_PaC", maintainOffset=True)
                    ikHandleGrp = cmds.group(ikHandleList[0], endIkHandleList[0], name=side+self.userGuideName+"_IKH_Grp")
                    cmds.setAttr(ikHandleGrp+".visibility", 0)
                    self.ctrls.setLockHide([self.ikCtrl], ['sx', 'sy', 'sz', 'v'])

                    if self.nJoints == 2:
                        cmds.parentConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Ik_Jxt", maintainOffset=True, name=side+self.userGuideName+"_00_Ik_Jxt_PaC")
                        cmds.scaleConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Ik_Jxt", maintainOffset=True, name=side+self.userGuideName+"_00_Ik_Jxt_ScC")

                # ik stretch
                cmds.addAttr(self.ikCtrl, longName='stretchable', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                stretchNormMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_StretchNormalize_MD")
                cmds.setAttr(stretchNormMD+".operation", 2)
                distBetweenList = self.utils.distanceBet(side+self.userGuideName+"_01_Ctrl", self.ikCtrl, name=side+self.userGuideName+"_DistBet", keep=True)
                cmds.connectAttr(self.ikFkRevNode+".outputX", distBetweenList[5]+"."+self.ikCtrl+"W0", force=True)
                cmds.connectAttr(self.fingerCtrl+".ikFkBlend", distBetweenList[5]+"."+distBetweenList[4]+"W1", force=True)
                cmds.connectAttr(distBetweenList[1]+".distance", stretchNormMD+".input1X", force=True)
                # TO DO? stretch compensate to ik Z axis
                ikStretchZUniformScaleMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_IkStretchZ_MD")
                cmds.setAttr(ikStretchZUniformScaleMD+".input2X", distBetweenList[0])
                cmds.connectAttr(self.skinJointList[0]+".scaleZ", ikStretchZUniformScaleMD+".input1X", force=True)
                cmds.connectAttr(ikStretchZUniformScaleMD+".outputX", stretchNormMD+".input2X", force=True)
                stretchScaleMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_StretchScale_MD")
                cmds.connectAttr(stretchNormMD+".outputX", stretchScaleMD+".input1X", force=True)
                cmds.connectAttr(self.ikCtrl+".stretchable", stretchScaleMD+".input2X", force=True)
                self.stretchCond = cmds.createNode("condition", name=side+self.userGuideName+"_Stretch_Cnd")
                cmds.connectAttr(stretchScaleMD+".outputX", self.stretchCond+".firstTerm", force=True)
                cmds.setAttr(self.stretchCond+".secondTerm", 1)
                cmds.setAttr(self.stretchCond+".operation", 2)
                cmds.connectAttr(stretchScaleMD+".outputX", self.stretchCond+".colorIfTrueR", force=True)
                self.toIDList.extend([stretchNormMD, ikStretchZUniformScaleMD, stretchScaleMD, self.stretchCond])

                # ik fk blend connnections
                for i, ikJoint in enumerate(ikJointList):
                    if not "_"+self.dpUIinst.jointEndAttr in ikJoint:
                        self.utils.clearDpArAttr([ikJoint])
                        fkJoint = ikJoint.replace("_Ik_Jxt", "_Fk_Jxt")
                        skinJoint = ikJoint.replace("_Ik_Jxt", "_Jnt")
                        self.fingerCtrl = side+self.userGuideName+"_01_Ctrl"
                        self.scaleCompensateCond = ikJoint.replace("_Ik_Jxt", "_ScaleCompensate_Cnd")
                        ikFkParentConst = cmds.parentConstraint(ikJoint, fkJoint, skinJoint, maintainOffset=True, name=skinJoint+"_PaC")[0]
                        cmds.connectAttr(self.fingerCtrl+".ikFkBlend", ikFkParentConst+"."+fkJoint+"W1", force=True)
                        cmds.connectAttr(self.ikFkRevNode+".outputX", ikFkParentConst+"."+ikJoint+"W0", force=True)
                        scaleBC = cmds.createNode("blendColors", name=skinJoint+"_BC")
                        self.toIDList.append(scaleBC)
                        cmds.connectAttr(fkJoint+".scaleX", scaleBC+".color1R", force=True)
                        cmds.connectAttr(fkJoint+".scaleY", scaleBC+".color1G", force=True)
                        cmds.connectAttr(fkJoint+".scaleZ", scaleBC+".color1B", force=True)
                        cmds.connectAttr(ikJoint+".scaleX", scaleBC+".color2R", force=True)
                        cmds.connectAttr(ikJoint+".scaleY", scaleBC+".color2G", force=True)
                        cmds.connectAttr(ikJoint+".scaleZ", scaleBC+".color2B", force=True)
                        if self.nJoints == 2:
                            if not "00_Ik_Jxt" in ikJoint: # to avoid thumb cycle error about the stretch
                                cmds.connectAttr(self.stretchCond+".outColorR", ikJoint+".scaleZ", force=True)
                        else:
                            cmds.connectAttr(self.stretchCond+".outColorR", ikJoint+".scaleZ", force=True)
                        cmds.connectAttr(self.fingerCtrl+".ikFkBlend", scaleBC+".blender", force=True)
                        cmds.connectAttr(scaleBC+".output.outputR", skinJoint+".scaleX", force=True)
                        cmds.connectAttr(scaleBC+".output.outputG", skinJoint+".scaleY", force=True)
                        cmds.connectAttr(scaleBC+".output.outputB", skinJoint+".scaleZ", force=True)
                        cmds.setAttr(ikJoint+".segmentScaleCompensate", 1)
                        if "01_Ik_Jxt" in ikJoint:
                            if not self.nJoints == 2: # to avoid thumb cycle error when parenting All_Grp transform node
                                cmds.pointConstraint(self.fingerCtrl, ikJoint, maintainOffset=True, name=ikJoint+"_PoC")
                        if self.nJoints > 2:
                            if i > 0:
                                # fix ik scale
                                cmds.connectAttr(self.skinJointList[0]+".scaleX", ikJointList[i]+".scaleX", force=True)
                                cmds.connectAttr(self.skinJointList[0]+".scaleY", ikJointList[i]+".scaleY", force=True)
                # create a masterModuleGrp to be checked if this rig exists:
                ctrlHookList = [side+self.userGuideName+"_00_SDK_Zero_0_Grp", side+self.userGuideName+"_01_SDK_Zero_0_Grp"]
                if self.nJoints >= 2:
                    if self.nJoints == 2:
                        scalableHookList = [self.skinJointList[0], ikBaseJoint, fkBaseJoint, ikHandleGrp, distBetweenList[2], distBetweenList[3], distBetweenList[4]]
                    else:
                        scalableHookList = [self.skinJointList[0], ikHandleGrp, distBetweenList[2], distBetweenList[3], distBetweenList[4]]
                else:
                    ctrlHookList.append(self.ikCtrlZero)
                    scalableHookList = [side+self.userGuideName+"_00_Jnt"]
                self.hookSetup(side, ctrlHookList, scalableHookList)
                if self.addCorrective:
                    cmds.parent(self.correctiveCtrlsGrp, self.toCtrlHookGrp)
                self.scalableGrpList.append(self.toScalableHookGrp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
                self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
        self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID


    def integratingInfo(self, *args):
        dpBaseStandard.BaseStandard.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
            "module": {
                "scalableGrpList": self.scalableGrpList,
                "ikCtrlZeroList": self.ikCtrlZeroList,
                "correctiveCtrlGrpList": self.correctiveCtrlGrpList
            }
        }
