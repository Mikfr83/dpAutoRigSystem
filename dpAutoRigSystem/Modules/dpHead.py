# importing libraries:
from maya import cmds
from . import dpBaseClass
from . import dpLayoutClass
import os
import json

# global variables to this module:    
CLASS_NAME = "Head"
TITLE = "m017_head"
DESCRIPTION = "m018_headDesc"
ICON = "/Icons/dp_head.png"

DP_HEAD_VERSION = 3.0


class Head(dpBaseClass.StartClass, dpLayoutClass.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.facialAttrList = ["facialBrow", "facialEyelid", "facialMouth", "facialLips", "facialSneer", "facialGrimace", "facialFace"]
        dpBaseClass.StartClass.__init__(self, *args, **kwargs)
        # declare variables
        self.correctiveCtrlGrpList = []
        self.aInnerCtrls = []
        self.redeclareVariables(self.guideName)
        
        self.RmVNumber = 0
        # redefining Tweaks variables:
        self.dpInitTweaksVariables()
        self.bsNode = None
        # declaring gaming dictionary:
#        self.tweaksDic = self.dpInitTweaksDic()
    
    
    def dpInitTweaksVariables(self, *args):
        # part names:
        mainName = self.dpUIinst.lang['c058_main']
        tweaksName = self.dpUIinst.lang['m081_tweaks']
        middleName = self.dpUIinst.lang['c029_middle']
        eyebrowName = self.dpUIinst.lang['c041_eyebrow']
        cornerName = self.dpUIinst.lang['c043_corner']
        upperName = self.dpUIinst.lang['c044_upper']
        lowerName = self.dpUIinst.lang['c045_lower']
        lipName = self.dpUIinst.lang['c039_lip']
        squintName = self.dpUIinst.lang['c054_squint']
        cheekName = self.dpUIinst.lang['c055_cheek']
        self.calibrateName = self.dpUIinst.lang["c111_calibrate"].lower()
        # eyebrows names:
        self.eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
        self.eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
        self.eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
        self.eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
        # squints names:
        self.squintName1 = tweaksName+"_"+squintName+"_01"
        self.squintName2 = tweaksName+"_"+squintName+"_02"
        self.squintName3 = tweaksName+"_"+squintName+"_03"
        # cheeks names:
        self.cheekName1 = tweaksName+"_"+cheekName+"_01"
        # lip names:
        self.upperLipMiddleName = tweaksName+"_"+upperName+"_"+lipName+"_00"
        self.upperLipName1 = tweaksName+"_"+upperName+"_"+lipName+"_01"
        self.upperLipName2 = tweaksName+"_"+upperName+"_"+lipName+"_02"
        self.lowerLipMiddleName = tweaksName+"_"+lowerName+"_"+lipName+"_00"
        self.lowerLipName1 = tweaksName+"_"+lowerName+"_"+lipName+"_01"
        self.lowerLipName2 = tweaksName+"_"+lowerName+"_"+lipName+"_02"
        self.lipCornerName = tweaksName+"_"+cornerName+"_"+lipName
        # list:
        self.tweaksNameList = [self.eyebrowMiddleName, self.eyebrowName1, self.eyebrowName2, self.eyebrowName3, \
                                self.squintName1, self.squintName2, self.squintName3, \
                                self.cheekName1, \
                                self.upperLipMiddleName, self.upperLipName1, self.upperLipName2, self.lowerLipMiddleName, self.lowerLipName1, self.lowerLipName2, self.lipCornerName]
        self.tweaksNameStrList = ["eyebrowMiddleName", "eyebrowName1", "eyebrowName2", "eyebrowName3", \
                                "squintName1", "squintName2", "squintName3", \
                                "cheekName1", \
                                "upperLipMiddleName", "upperLipName1", "upperLipName2", "lowerLipMiddleName", "lowerLipName1", "lowerLipName2", "lipCornerName"]
    
    
    def createModuleLayout(self, *args):
        dpBaseClass.StartClass.createModuleLayout(self)
        dpLayoutClass.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        dpBaseClass.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 0)
        cmds.addAttr(self.moduleGrp, longName="corrective", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".corrective", 0)
        cmds.addAttr(self.moduleGrp, longName="facial", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".facial", 0)
        for attr in self.facialAttrList:
            cmds.addAttr(self.moduleGrp, longName=attr, attributeType='bool')
            cmds.setAttr(self.moduleGrp+"."+attr, 1)

        # create cvJointLoc and cvLocators:
        self.cvNeckLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Neck0", r=0.5, d=1, rot=(-90, 90, 0), guide=True)
        self.cvHeadLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Head", r=0.4, d=1, guide=True)
        self.cvJawLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_Jaw", r=0.3, d=1, guide=True)
        self.cvChinLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Chin", r=0.3, d=1, guide=True)
        self.cvChewLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Chew", r=0.3, d=1, guide=True)
        self.cvLCornerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_LCornerLip", r=0.1, d=1, guide=True)
        self.cvRCornerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RCornerLip", r=0.1, d=1, guide=True)
        self.cvUpperJawLoc  = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_UpperJaw", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.cvUpperHeadLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_UpperHead", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.cvUpperLipLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_UpperLip", r=0.15, d=1, guide=True)
        self.cvLowerLipLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_LowerLip", r=0.15, d=1, guide=True)
        self.cvBrowLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_Brow", r=0.2, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_046_FacialBrow"))
        self.cvEyelidLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_Eyelid", r=0.2, d=1, guide=True, rot=(0, 0, 90), color="cyan", cvType=self.ctrls.getControlModuleById("id_047_FacialEyelid"))
        self.cvMouthLoc   = self.ctrls.cvLocator(ctrlName=self.guideName+"_Mouth", r=0.2, d=1, guide=True, rot=(0, 0, -90), color="cyan", cvType=self.ctrls.getControlModuleById("id_048_FacialMouth"))
        self.cvLipsLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_Lips", r=0.1, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_049_FacialLips"))
        self.cvSneerLoc   = self.ctrls.cvLocator(ctrlName=self.guideName+"_Sneer", r=0.2, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_050_FacialSneer"))
        self.cvGrimaceLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Grimace", r=0.2, d=1, guide=True, rot=(0, 0, 180), color="cyan", cvType=self.ctrls.getControlModuleById("id_051_FacialGrimace"))
        self.cvFaceLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_Face", r=0.2, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_052_FacialFace"))

        # create jointGuides:
        self.jGuideNeck0 = cmds.joint(name=self.guideName+"_JGuideNeck0", radius=0.001)
        self.jGuideHead = cmds.joint(name=self.guideName+"_JGuideHead", radius=0.001)
        self.jGuideUpperJaw = cmds.joint(name=self.guideName+"_jGuideUpperJaw", radius=0.001)
        self.jGuideUpperLip = cmds.joint(name=self.guideName+"_jGuideUpperLip", radius=0.001)
        cmds.select(self.jGuideUpperJaw)
        self.jGuideUpperHead = cmds.joint(name=self.guideName+"_jGuideUpperHead", radius=0.001)
        cmds.select(self.jGuideHead)
        self.jGuideJaw  = cmds.joint(name=self.guideName+"_JGuideJaw", radius=0.001)
        self.jGuideChin = cmds.joint(name=self.guideName+"_JGuideChin", radius=0.001)
        self.jGuideChew = cmds.joint(name=self.guideName+"_JGuideChew", radius=0.001)
        cmds.select(self.jGuideChin)
        self.jGuideLowerLip = cmds.joint(name=self.guideName+"_jGuideLowerLip", radius=0.001)
        cmds.select(self.jGuideJaw)
        self.jGuideLLip = cmds.joint(name=self.guideName+"_jGuideLLip", radius=0.001)
        # set jointGuides as templates:
        jGuideList = [self.jGuideNeck0, self.jGuideHead, self.jGuideUpperJaw, self.jGuideUpperHead, self.jGuideJaw, self.jGuideChin, self.jGuideChew, self.jGuideUpperLip, self.jGuideLowerLip]
        for jGuide in jGuideList:
            cmds.setAttr(jGuide+".template", 1)
        cmds.parent(self.jGuideNeck0, self.moduleGrp, relative=True)
        # create cvEnd:
        cmds.select(self.jGuideChew)
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvChewLoc)
        cmds.setAttr(self.cvEndJoint+".tz", self.ctrls.dpCheckLinearUnit(0.6))
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideChew)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvNeckLoc, self.jGuideNeck0, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvHeadLoc, self.jGuideHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperJawLoc, self.jGuideUpperJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperHeadLoc, self.jGuideUpperHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvJawLoc, self.jGuideJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChinLoc, self.jGuideChin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChewLoc, self.jGuideChew, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperLipLoc, self.jGuideUpperLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLowerLipLoc, self.jGuideLowerLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLCornerLipLoc, self.jGuideLLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
        cmds.setAttr(self.cvNeckLoc+".rotateZ", 90)
        cmds.makeIdentity(self.cvNeckLoc, rotate=True, apply=False)
        cmds.setAttr(self.cvHeadLoc+".translateY", 2)
        cmds.setAttr(self.cvUpperJawLoc+".translateY", 3.5)
        cmds.setAttr(self.cvUpperJawLoc+".translateZ", 0.25)
        cmds.setAttr(self.cvUpperHeadLoc+".translateY", 4.2)
        cmds.setAttr(self.cvUpperHeadLoc+".translateZ", 0.5)
        cmds.setAttr(self.cvJawLoc+".translateY", 2.7)
        cmds.setAttr(self.cvJawLoc+".translateZ", 0.7)
        cmds.setAttr(self.cvChinLoc+".translateY", 2.5)
        cmds.setAttr(self.cvChinLoc+".translateZ", 1.0)
        cmds.setAttr(self.cvChewLoc+".translateY", 2.3)
        cmds.setAttr(self.cvChewLoc+".translateZ", 1.3)
        # lip cvLocs:
        cmds.setAttr(self.cvUpperLipLoc+".translateY", 2.9)
        cmds.setAttr(self.cvUpperLipLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvLowerLipLoc+".translateY", 2.3)
        cmds.setAttr(self.cvLowerLipLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvLCornerLipLoc+".translateX", 0.6)
        cmds.setAttr(self.cvLCornerLipLoc+".translateY", 2.6)
        cmds.setAttr(self.cvLCornerLipLoc+".translateZ", 3.4)
        # mirror right Lip:
        self.lipTMD = cmds.createNode("multiplyDivide", name=self.guideName+"_LipTMD")
        self.lipRMD = cmds.createNode("multiplyDivide", name=self.guideName+"_LipRMD")
        cmds.connectAttr(self.cvLCornerLipLoc+".translateX", self.lipTMD+".input1X", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".translateY", self.lipTMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".translateZ", self.lipTMD+".input1Z", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".rotateX", self.lipRMD+".input1X", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".rotateY", self.lipRMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".rotateZ", self.lipRMD+".input1Z", force=True)
        cmds.connectAttr(self.lipTMD+".outputX", self.cvRCornerLipLoc+".translateX", force=True)
        cmds.connectAttr(self.lipTMD+".outputY", self.cvRCornerLipLoc+".translateY", force=True)
        cmds.connectAttr(self.lipTMD+".outputZ", self.cvRCornerLipLoc+".translateZ", force=True)
        cmds.connectAttr(self.lipRMD+".outputX", self.cvRCornerLipLoc+".rotateX", force=True)
        cmds.connectAttr(self.lipRMD+".outputY", self.cvRCornerLipLoc+".rotateY", force=True)
        cmds.connectAttr(self.lipRMD+".outputZ", self.cvRCornerLipLoc+".rotateZ", force=True)
        cmds.setAttr(self.lipTMD+".input2X", -1)
        cmds.setAttr(self.lipRMD+".input2Y", -1)
        cmds.setAttr(self.lipRMD+".input2Z", -1)
        cmds.setAttr(self.cvRCornerLipLoc+".template", 1)
        # facial cvLocs
        cmds.setAttr(self.cvBrowLoc+".translateX", 0.9)
        cmds.setAttr(self.cvBrowLoc+".translateY", 4.7)
        cmds.setAttr(self.cvBrowLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvEyelidLoc+".translateX", 0.3)
        cmds.setAttr(self.cvEyelidLoc+".translateY", 4.15)
        cmds.setAttr(self.cvEyelidLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvMouthLoc+".translateX", 1)
        cmds.setAttr(self.cvMouthLoc+".translateY", 2.6)
        cmds.setAttr(self.cvMouthLoc+".translateZ", 3.4)
        cmds.setAttr(self.cvLipsLoc+".translateY", 2.6)
        cmds.setAttr(self.cvLipsLoc+".translateZ", 3.9)
        cmds.setAttr(self.cvSneerLoc+".translateY", 3.15)
        cmds.setAttr(self.cvSneerLoc+".translateZ", 3.9)
        cmds.setAttr(self.cvGrimaceLoc+".translateY", 2)
        cmds.setAttr(self.cvGrimaceLoc+".translateZ", 3.9)
        cmds.setAttr(self.cvFaceLoc+".translateX", 2.4)
        cmds.setAttr(self.cvFaceLoc+".translateY", 1.5)
        cmds.setAttr(self.cvFaceLoc+".translateZ", 0.7)
        # make parenting between cvLocs:
        cmds.parent(self.cvNeckLoc, self.moduleGrp)
        cmds.parent(self.cvHeadLoc, self.cvNeckLoc)
        cmds.parent(self.cvUpperJawLoc, self.cvJawLoc, self.cvHeadLoc)
        cmds.parent(self.cvChinLoc, self.cvJawLoc)
        cmds.parent(self.cvChewLoc, self.cvLowerLipLoc, self.cvChinLoc)
        cmds.parent(self.cvLCornerLipLoc, self.cvJawLoc)
        cmds.parent(self.cvRCornerLipLoc, self.cvJawLoc)
        cmds.parent(self.cvUpperLipLoc, self.cvUpperHeadLoc, self.cvLipsLoc, self.cvUpperJawLoc)
        cmds.parent(self.cvBrowLoc, self.cvEyelidLoc, self.cvUpperHeadLoc)
        cmds.parent(self.cvMouthLoc, self.cvLCornerLipLoc)
        cmds.parent(self.cvSneerLoc, self.cvUpperLipLoc)
        cmds.parent(self.cvGrimaceLoc, self.cvLowerLipLoc)
        cmds.parent(self.cvFaceLoc, self.cvHeadLoc)
        # include nodes into net
        self.addNodeToGuideNet([self.cvNeckLoc, self.cvHeadLoc, self.cvJawLoc, self.cvChinLoc, self.cvChewLoc, self.cvLCornerLipLoc, self.cvUpperJawLoc, self.cvUpperHeadLoc, self.cvUpperLipLoc, self.cvLowerLipLoc, self.cvBrowLoc, self.cvEyelidLoc, self.cvMouthLoc, self.cvLipsLoc, self.cvSneerLoc, self.cvGrimaceLoc, self.cvFaceLoc, self.cvEndJoint],\
                                ["Neck0", "Head", "Jaw", "Chin", "Chew", "LCornerLip", "UpperJaw", "UpperHead", "UpperLip", "LowerLip", "Brow", "Eyelid", "Mouth", "Lips", "Sneer", "Grimace", "Face", "JointEnd"])
    

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
        # get the number of joints existing:
        self.currentNJoints = cmds.getAttr(self.moduleGrp+".nJoints")
        # start analisys the difference between values:
        if self.enteredNJoints != self.currentNJoints:
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvNeckLoc:
                    self.cvNeckLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Neck"+str(n-1), r=0.2, d=1, rot=(-90, 90, 0), guide=True)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvNeckLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvNeckLoc, self.guideName+"_Neck"+str(n-2), relative=True)
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.guideName+"_JGuideNeck"+str(n-1), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    #Prevent a intermidiate node to be added
                    cmds.parent(self.jGuide, self.guideName+"_JGuideNeck"+str(n-2), relative=True)
                    #Do not maintain offset and ensure cv will be at the same place than the joint
                    cmds.parentConstraint(self.cvNeckLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                    cmds.scaleConstraint(self.cvNeckLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
                    self.addNodeToGuideNet([self.cvNeckLoc], ["Neck"+str(n-1)])
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvNeckLoc:
                self.cvNeckLoc = self.guideName+"_Neck"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = self.utils.getGuideChildrenList(self.cvNeckLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvNeckLoc)
                # delete difference of nJoints:
                cmds.delete(self.guideName+"_Neck"+str(self.enteredNJoints))
                cmds.delete(self.guideName+"_JGuideNeck"+str(self.enteredNJoints))
                for j in range(self.enteredNJoints, self.currentNJoints):
                    self.removeAttrFromGuideNet(["Neck"+str(j)])
            # get the length of the neck to position segments.
            dist = self.utils.distanceBet(self.guideName+"_Neck0", self.guideName+"_Head")[0]
            # translateY to input on each cvLocator
            distBt = dist/(self.enteredNJoints)
            for n in range(1, self.enteredNJoints):
                # translate the locators to the calculated position:
                cmds.setAttr(self.guideName+"_Neck"+str(n)+".translateY", distBt)
            cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            # re-build the preview mirror:
            dpLayoutClass.LayoutClass.createPreviewMirror(self)
        cmds.select(self.moduleGrp)
    

    def changeFacial(self, value, *args):
        """ Enable or disable the Facial Controls UI.
            Set the moduleGrp facial value as well.
        """
        collapsed = False
        if not value:
            collapsed = True
        cmds.frameLayout(self.facialCtrlFrameLayout, edit=True, collapse=collapsed, enable=value)
        cmds.setAttr(self.moduleGrp+".facial", value)
        for item in list(self.facialLocDic.keys()):
            cmds.setAttr(self.facialLocDic[item]+".visibility", False)
            if value:
                cmds.setAttr(self.facialLocDic[item]+".visibility", cmds.getAttr(self.moduleGrp+"."+item))


    def changeFacialElement(self, uiCB, attr, *args):
        """ Activate or disactivate the facial elements by them UI checkbox value.
        """
        cbValue = cmds.checkBox(uiCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+"."+attr, cbValue)
        cmds.setAttr(self.facialLocDic[attr]+".visibility", cbValue)


    def setupJawMove(self, attrCtrl, openCloseID, positiveRotation=True, axis="Y", intAttrID="c049_intensity", invertRot=False, createOutput=False, fixValue=0.01, *args):
        """ Create the setup for move jaw group when jaw control rotates for open or close adjustements.
            Depends on axis and rotation done.
        """
        # declaring naming:
        attrBaseName = self.utils.extractSuffix(attrCtrl)
        drivenGrp = attrBaseName+"_"+self.dpUIinst.lang[openCloseID]+self.dpUIinst.lang['c034_move']+"_Grp"
        # attribute names:
        intAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang[intAttrID].capitalize()+axis
        startRotName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c110_start'].capitalize()+"Rotation"
        unitFixAttrName = self.dpUIinst.lang[openCloseID].lower()+"UnitFix"+axis
        calibAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c111_calibrate']+axis
        calibOutputAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output']
        outputAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c112_output']
        # utility node names:
        jawCalibrateMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_"+self.dpUIinst.lang['c111_calibrate']+"_"+axis+"_MD"
        jawUnitFixMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_UnitFix_"+axis+"_MD"
        jawIntMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_MD"
        jawStartMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_Start_"+axis+"_MD"
        jawIntPMAName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_Start_"+axis+"_PMA"
        jawIntCndName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_Cnd"
        jawOutputRmVName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang['c112_output']+"_RmV"
        
        # create move group and its attributes:
        if not cmds.objExists(drivenGrp):
            drivenGrp = cmds.group(attrCtrl, name=drivenGrp)
        if not cmds.objExists(self.jawCtrl+"."+startRotName):
            if positiveRotation: #open
                cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=5, minValue=0, keyable=True)
            else: #close
                cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=0, maxValue=0, keyable=True)
            cmds.setAttr(self.jawCtrl+"."+startRotName, keyable=False, channelBox=True)
        if not cmds.objExists(attrCtrl+"."+unitFixAttrName):
            if positiveRotation: #open
                cmds.addAttr(attrCtrl, longName=unitFixAttrName, attributeType='float', defaultValue=fixValue)
            else:
                cmds.addAttr(attrCtrl, longName=unitFixAttrName, attributeType='float', defaultValue=-fixValue)
            cmds.setAttr(attrCtrl+"."+unitFixAttrName, lock=True)
        if not cmds.objExists(attrCtrl+"."+calibAttrName):
            cmds.addAttr(attrCtrl, longName=calibAttrName, attributeType='float', defaultValue=1)
        if not cmds.objExists(attrCtrl+"."+intAttrName):
            cmds.addAttr(attrCtrl, longName=intAttrName, attributeType='float', defaultValue=1, keyable=True)
            cmds.setAttr(attrCtrl+"."+intAttrName, keyable=False, channelBox=True)
        
        # create utility nodes:
        jawCalibrateMD = cmds.createNode('multiplyDivide', name=jawCalibrateMDName)
        jawUnitFixMD = cmds.createNode('multiplyDivide', name=jawUnitFixMDName)
        jawIntMD = cmds.createNode('multiplyDivide', name=jawIntMDName)
        jawStartMD = cmds.createNode('multiplyDivide', name=jawStartMDName)
        jawIntPMA = cmds.createNode('plusMinusAverage', name=jawIntPMAName)
        jawIntCnd = cmds.createNode('condition', name=jawIntCndName)
        
        # set attributes to move jaw group when open or close:
        cmds.setAttr(jawIntPMA+".operation", 2) #substract
        cmds.setAttr(jawIntCnd+".operation", 4) #less than
        if positiveRotation: #open
            cmds.setAttr(jawIntCnd+".operation", 2) #greater than
        cmds.setAttr(jawIntCnd+".colorIfFalseR", 0)
        
        # connect utility nodes:
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntMD+".input1"+axis, force=True)
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntCnd+".firstTerm", force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawStartMD+".input2"+axis, force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawIntCnd+".secondTerm", force=True)
        cmds.connectAttr(attrCtrl+"."+intAttrName, jawCalibrateMD+".input1"+axis, force=True)
        cmds.connectAttr(attrCtrl+"."+calibAttrName, jawCalibrateMD+".input2"+axis, force=True)
        cmds.connectAttr(attrCtrl+"."+unitFixAttrName, jawUnitFixMD+".input2"+axis, force=True)
        cmds.connectAttr(jawCalibrateMD+".output"+axis, jawUnitFixMD+".input1"+axis, force=True)
        cmds.connectAttr(jawUnitFixMD+".output"+axis, jawIntMD+".input2"+axis, force=True)
        cmds.connectAttr(jawUnitFixMD+".output"+axis, jawStartMD+".input1"+axis, force=True)
        cmds.connectAttr(jawIntMD+".output"+axis, jawIntPMA+".input1D[0]", force=True)
        cmds.connectAttr(jawStartMD+".output"+axis, jawIntPMA+".input1D[1]", force=True)
        cmds.connectAttr(jawIntPMA+".output1D", jawIntCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(jawIntCnd+".outColorR", drivenGrp+".translate"+axis, force=True)
        
        # invert rotation for lower lip exception:
        if invertRot:
            invetRotPMAName = attrBaseName+self.dpUIinst.lang[openCloseID]+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_InvertRot_PMA"
            invetRotMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_InvertRot_MD"
            invetRotPMA = cmds.createNode('plusMinusAverage', name=invetRotPMAName)
            invetRotMD = cmds.createNode('multiplyDivide', name=invetRotMDName)
            cmds.setAttr(invetRotPMA+".operation", 2) #substract
            cmds.setAttr(invetRotMD+".input2X", -1)
            cmds.setAttr(jawIntCnd+".colorIfFalseG", 0)
            cmds.connectAttr(self.jawCtrl+".rotateX", invetRotPMA+".input1D[0]", force=True)
            cmds.connectAttr(self.jawCtrl+"."+startRotName, invetRotPMA+".input1D[1]", force=True)
            cmds.connectAttr(invetRotPMA+".output1D", jawIntCnd+".colorIfTrueG", force=True)
            cmds.connectAttr(jawIntCnd+".outColorG", invetRotMD+".input1X", force=True)
            cmds.connectAttr(invetRotMD+".outputX", drivenGrp+".rotateX", force=True)
            
        # output to a blendShape target value setup:
        if createOutput:
            if not cmds.objExists(self.jawCtrl+"."+outputAttrName):
                cmds.addAttr(self.jawCtrl, longName=calibOutputAttrName, attributeType='float', defaultValue=1)
                cmds.addAttr(self.jawCtrl, longName=outputAttrName, attributeType='float', defaultValue=1)
            jawOutputRmV = cmds.createNode('remapValue', name=jawOutputRmVName)
            cmds.connectAttr(self.jawCtrl+".rotateX", jawOutputRmV+".inputValue", force=True)
            cmds.connectAttr(self.jawCtrl+"."+calibOutputAttrName, jawOutputRmV+".inputMax", force=True)
            cmds.connectAttr(jawOutputRmV+".outValue", self.jawCtrl+"."+outputAttrName, force=True)
            cmds.setAttr(self.jawCtrl+"."+outputAttrName, lock=True)

    
    def getCalibratePresetList(self, s, *args):
        """ Returns the calibration preset and invert lists for neck and head joints.
        """
        invertList = [[], [], ["invertTX", "invertRY", "invertRZ"], [], []]
        presetList = [{}, {"calibrateTX":1}, {"calibrateTX":1}, {"calibrateTZ":1}, {"calibrateTZ":-1}]
        if s == 1:
            if self.addFlip:
                invertList = [[], ["invertTX"], ["invertTX"], ["invertTZ"], ["invertTZ"]]
        return presetList, invertList


    def autoRotateCalc(self, n, *args):
        if self.nJoints < 7:
            return 0.15*(n+1)
        else:
            if n == 0:
                return (2**(1/self.nJoints))-1
            else:
                return (2**(n/self.nJoints))-(1-(1/self.nJoints))

    
    def redeclareVariables(self, middle, side="", guide="", *args):
        """ Just redeclare main locators and dictionary to use it again after reloading code.
        """
        self.base            = side+middle+guide+"_Base"
        self.cvHeadLoc       = side+middle+guide+"_Head"
        self.cvUpperJawLoc   = side+middle+guide+"_UpperJaw"
        self.cvUpperHeadLoc  = side+middle+guide+"_UpperHead"
        self.cvJawLoc        = side+middle+guide+"_Jaw"
        self.cvChinLoc       = side+middle+guide+"_Chin"
        self.cvChewLoc       = side+middle+guide+"_Chew"
        self.cvLCornerLipLoc = side+middle+guide+"_LCornerLip"
        self.cvRCornerLipLoc = side+middle+guide+"_RCornerLip"
        self.cvUpperLipLoc   = side+middle+guide+"_UpperLip"
        self.cvLowerLipLoc   = side+middle+guide+"_LowerLip"
        self.cvEndJoint      = side+middle+guide+"_JointEnd"
        self.radiusGuide     = side+middle+guide+"_Base_RadiusCtrl"
        self.cvBrowLoc       = side+middle+guide+"_Brow"
        self.cvEyelidLoc     = side+middle+guide+"_Eyelid"
        self.cvMouthLoc      = side+middle+guide+"_Mouth"
        self.cvLipsLoc       = side+middle+guide+"_Lips"
        self.cvSneerLoc      = side+middle+guide+"_Sneer"
        self.cvGrimaceLoc    = side+middle+guide+"_Grimace"
        self.cvFaceLoc       = side+middle+guide+"_Face"
        self.facialLocDic = {
                                self.facialAttrList[0] : self.cvBrowLoc,
                                self.facialAttrList[1] : self.cvEyelidLoc,
                                self.facialAttrList[2] : self.cvMouthLoc,
                                self.facialAttrList[3] : self.cvLipsLoc,
                                self.facialAttrList[4] : self.cvSneerLoc,
                                self.facialAttrList[5] : self.cvGrimaceLoc,
                                self.facialAttrList[6] : self.cvFaceLoc
                            }
        

    def rigModule(self, *args):
        dpBaseClass.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            self.addFlip = self.getModuleAttr("flip")
            self.addCorrective = self.getModuleAttr("corrective")
            # declare lists to store names and attributes:
            self.worldRefList, self.upperCtrlList, self.upperJawCtrlList = [], [], []
            self.aCtrls, self.aLCtrls, self.aRCtrls = [], [], []
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [ self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_' ]
                for s, side in enumerate(sideList):
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_Guide_Base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        if not self.addFlip:
                            for axis in self.mirrorAxis:
                                gotValue = cmds.getAttr(side+self.userGuideName+"_Guide_Base.translate"+axis)
                                flipedValue = gotValue*(-2)
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                        else:
                            for axis in self.mirrorAxis:
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = self.utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                self.neckLocList, self.neckCtrlList, self.neckJointList = [], [], []
                # redeclaring variables:
                self.redeclareVariables(self.userGuideName, side, "_Guide")
                
                # generating naming:
                headJntName = side+self.userGuideName+"_01_"+self.dpUIinst.lang['c024_head']+"_Jnt"
                if self.addArticJoint:
                    headJntName = side+self.userGuideName+"_02_"+self.dpUIinst.lang['c024_head']+"_Jnt"
                upperJawJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw']+"_Jnt"
                upperHeadJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_Jnt"
                upperEndJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_JEnd"
                jawJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c025_jaw']+"_Jnt"
                chinJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c026_chin']+"_Jnt"
                chewJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c048_chew']+"_Jnt"
                endJntName = side+self.userGuideName+"_JEnd"
                lCornerLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['p002_left']+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                rCornerLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['p003_right']+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                upperLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                lowerLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c045_lower']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                neckCtrlBaseName = side+self.userGuideName+"_"+self.dpUIinst.lang['c023_neck']
                headCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_Ctrl"
                headSubCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_Sub_Ctrl"
                upperJawCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw']+"_Ctrl"
                upperHeadCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_Ctrl"
                jawCtrlName  = side+self.userGuideName+"_"+self.dpUIinst.lang['c025_jaw']+"_Ctrl"
                chinCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c026_chin']+"_Ctrl"
                chewCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c048_chew']+"_Ctrl"
                lCornerLipCtrlName = self.dpUIinst.lang['p002_left']+"_"+self.userGuideName+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                rCornerLipCtrlName = self.dpUIinst.lang['p003_right']+"_"+self.userGuideName+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                upperLipCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                lowerLipCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c045_lower']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                lBrowCtrlName = self.dpUIinst.lang['p002_left']+"_"+self.userGuideName+"_"+self.dpUIinst.lang["c060_brow"]+"_Ctrl"
                rBrowCtrlName = self.dpUIinst.lang['p003_right']+"_"+self.userGuideName+"_"+self.dpUIinst.lang["c060_brow"]+"_Ctrl"
                lEyelidCtrlName = self.dpUIinst.lang['p002_left']+"_"+self.userGuideName+"_"+self.dpUIinst.lang["c042_eyelid"]+"_Ctrl"
                rEyelidCtrlName = self.dpUIinst.lang['p003_right']+"_"+self.userGuideName+"_"+self.dpUIinst.lang["c042_eyelid"]+"_Ctrl"
                mouthCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang["c061_mouth"]+"_Ctrl"
                lipsCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang["c062_lips"]+"_Ctrl"
                sneerCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang["c063_sneer"]+"_Ctrl"
                grimaceCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang["c064_grimace"]+"_Ctrl"
                faceCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang["c065_face"]+"_Ctrl"
                
                # get the number of joints to be created for the neck:
                self.nJoints = cmds.getAttr(self.base+".nJoints")

                # creating joints:
                cmds.select(clear=True)
                for n in range(0, self.nJoints):
                    # neck segments:
                    cvNeckLoc = side+self.userGuideName+"_Guide_Neck"+str(n)
                    self.neckLocList.append(cvNeckLoc)
                    neckJnt = cmds.joint(name=neckCtrlBaseName+"_"+str(n).zfill(2)+"_Jnt", scaleCompensate=False)
                    self.neckJointList.append(neckJnt)
                self.headJnt = cmds.joint(name=headJntName, scaleCompensate=False)
                self.upperJawJnt = cmds.joint(name=upperJawJntName, scaleCompensate=False)
                self.upperHeadJnt = cmds.joint(name=upperHeadJntName, scaleCompensate=False)
                self.upperEndJnt = cmds.joint(name=upperEndJntName, scaleCompensate=False, radius=0.5)
                cmds.setAttr(self.upperEndJnt+".translateY", 0.3*self.ctrlRadius)
                cmds.select(self.headJnt)
                self.jawJnt  = cmds.joint(name=jawJntName, scaleCompensate=False)
                self.chinJnt = cmds.joint(name=chinJntName, scaleCompensate=False)
                self.chewJnt = cmds.joint(name=chewJntName, scaleCompensate=False)
                self.endJnt  = cmds.joint(name=endJntName, scaleCompensate=False, radius=0.5)
                cmds.select(self.headJnt)
                self.lCornerLipJnt = cmds.joint(name=lCornerLipJntName, scaleCompensate=False)
                cmds.select(self.headJnt)
                self.rCornerLipJnt = cmds.joint(name=rCornerLipJntName, scaleCompensate=False)
                cmds.select(self.upperJawJnt)
                self.upperLipJnt = cmds.joint(name=upperLipJntName, scaleCompensate=False)
                cmds.select(self.chinJnt)
                self.lowerLipJnt = cmds.joint(name=lowerLipJntName, scaleCompensate=False)
                cmds.select(clear=True)
                dpARJointList = [self.headJnt, self.upperJawJnt, self.upperHeadJnt, self.jawJnt, self.chinJnt, self.chewJnt, self.lCornerLipJnt, self.rCornerLipJnt, self.upperLipJnt, self.lowerLipJnt]
                dpARJointList.extend(self.neckJointList)
                for dpARJoint in dpARJointList:
                    cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                for n in range(0, self.nJoints):
                    self.utils.setJointLabel(self.neckJointList[n], s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c023_neck']+"_"+str(n).zfill(2))
                self.utils.setJointLabel(self.headJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c024_head'])
                self.utils.setJointLabel(self.upperJawJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw'])
                self.utils.setJointLabel(self.upperHeadJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head'])
                self.utils.setJointLabel(self.jawJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c025_jaw'])
                self.utils.setJointLabel(self.chinJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c026_chin'])
                self.utils.setJointLabel(self.chewJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c048_chew'])
                self.utils.setJointLabel(self.lCornerLipJnt, 1, 18, self.userGuideName+"_"+self.dpUIinst.lang['c039_lip'])
                self.utils.setJointLabel(self.rCornerLipJnt, 2, 18, self.userGuideName+"_"+self.dpUIinst.lang['c039_lip'])
                self.utils.setJointLabel(self.upperLipJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c039_lip'])
                self.utils.setJointLabel(self.lowerLipJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c045_lower']+self.dpUIinst.lang['c039_lip'])
                # creating controls:
                for n in range(0, self.nJoints):
                    neckCtrl = self.ctrls.cvControl("id_022_HeadNeck", ctrlName=neckCtrlBaseName+"_"+str(n).zfill(2)+"_Ctrl", r=(self.ctrlRadius/((n*0.2)+1)), d=self.curveDegree, dir="-Z", guideSource=self.guideName+"_Neck"+str(n))
                    if n > 0:
                        cmds.parent(neckCtrl, self.neckCtrlList[-1])
                    self.neckCtrlList.append(neckCtrl)
                self.headCtrl = self.ctrls.cvControl("id_023_HeadHead", ctrlName=headCtrlName, r=(self.ctrlRadius * 2.5), d=self.curveDegree, guideSource=self.guideName+"_Head")
                self.headSubCtrl = self.ctrls.cvControl("id_093_HeadSub", ctrlName=headSubCtrlName, r=(self.ctrlRadius * 2.2), d=self.curveDegree, guideSource=self.guideName+"_Head")
                self.upperJawCtrl = self.ctrls.cvControl("id_069_HeadUpperJaw", ctrlName=upperJawCtrlName, r=self.ctrlRadius, d=self.curveDegree, headDef=1, guideSource=self.guideName+"_UpperJaw")
                self.upperHeadCtrl = self.ctrls.cvControl("id_081_HeadUpperHead", ctrlName=upperHeadCtrlName, r=self.ctrlRadius, d=self.curveDegree, headDef=1, guideSource=self.guideName+"_UpperHead")
                self.jawCtrl = self.ctrls.cvControl("id_024_HeadJaw", ctrlName=jawCtrlName, r=self.ctrlRadius, d=self.curveDegree, headDef=3, guideSource=self.guideName+"_Jaw")
                self.chinCtrl = self.ctrls.cvControl("id_025_HeadChin", ctrlName=chinCtrlName, r=(self.ctrlRadius * 0.2), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_Chin")
                self.chewCtrl = self.ctrls.cvControl("id_026_HeadChew", ctrlName=chewCtrlName, r=(self.ctrlRadius * 0.15), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_Chew")
                self.lCornerLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=lCornerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_LCornerLip")
                self.rCornerLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=rCornerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_RCornerLip")
                self.upperLipCtrl = self.ctrls.cvControl("id_072_HeadUpperLip", ctrlName=upperLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_UpperLip")
                self.lowerLipCtrl = self.ctrls.cvControl("id_073_HeadLowerLip", ctrlName=lowerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_LowerLip")
                # facial controls
                if cmds.getAttr(self.moduleGrp+".facial"):
                    if cmds.getAttr(self.moduleGrp+".facialBrow"):
                        
                        #lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", self.browTgtList, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "red", True, False)
                        lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", self.browTgtList, (0, 0, 0), False, False, True, True, True, True, False, True, False, "red", True, False)



                self.upperCtrlList.append(self.upperHeadCtrl)
                self.aCtrls.append([self.upperLipCtrl, self.lowerLipCtrl])
                self.aLCtrls.append([self.lCornerLipCtrl])
                self.aRCtrls.append([self.rCornerLipCtrl])
                self.aInnerCtrls.append([self.headSubCtrl])
                self.ctrls.setSubControlDisplay(self.headCtrl, self.headSubCtrl, 1)
                self.upperJawCtrlList.append(self.upperJawCtrl)

                # optimize control CV shapes:
                tempHeadCluster = cmds.cluster(self.headCtrl, self.headSubCtrl)[1]
                cmds.setAttr(tempHeadCluster+".translateY", -0.5)
                tempJawCluster = cmds.cluster(self.jawCtrl)[1]
                cmds.setAttr(tempJawCluster+".translateY", -2)
                cmds.setAttr(tempJawCluster+".translateZ", 2.1)
                tempChinCluster = cmds.cluster(self.chinCtrl)[1]
                cmds.setAttr(tempChinCluster+".translateY", -1.4)
                cmds.setAttr(tempChinCluster+".translateZ", 3.6)
                cmds.setAttr(tempChinCluster+".rotateX", 22)
                tempChewCluster = cmds.cluster(self.chewCtrl)[1]
                cmds.setAttr(tempChewCluster+".translateY", -1.35)
                cmds.setAttr(tempChewCluster+".translateZ", 3.6)
                cmds.setAttr(tempChewCluster+".rotateX", 22)
                cmds.delete([self.headCtrl, self.headSubCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl], constructionHistory=True)
                
                #Setup Axis Order
                if self.rigType == dpBaseClass.RigType.quadruped:
                    for n in range(0, self.nJoints):
                        cmds.setAttr(self.neckCtrlList[n]+".rotateOrder", 1)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.headSubCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.upperJawCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.upperHeadCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 1)
                else:
                    for n in range(0, self.nJoints):
                        cmds.setAttr(self.neckCtrlList[n]+".rotateOrder", 3)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.headSubCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.upperJawCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.upperHeadCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 3)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                for n in range(0, self.nJoints):
                    if n == 0:
                        self.utils.originedFrom(objName=self.neckCtrlList[0], attrString=self.base+";"+self.neckLocList[0]+";"+self.radiusGuide)
                    else:
                        self.utils.originedFrom(objName=self.neckCtrlList[n], attrString=self.neckLocList[n])
                self.utils.originedFrom(objName=self.headSubCtrl, attrString=self.cvHeadLoc)
                self.utils.originedFrom(objName=self.upperJawCtrl, attrString=self.cvUpperJawLoc)
                self.utils.originedFrom(objName=self.upperHeadCtrl, attrString=self.cvUpperHeadLoc)
                self.utils.originedFrom(objName=self.jawCtrl, attrString=self.cvJawLoc)
                self.utils.originedFrom(objName=self.chinCtrl, attrString=self.cvChinLoc)
                self.utils.originedFrom(objName=self.chewCtrl, attrString=self.cvChewLoc+";"+self.cvEndJoint)
                self.utils.originedFrom(objName=self.lCornerLipCtrl, attrString=self.cvLCornerLipLoc)
                self.utils.originedFrom(objName=self.rCornerLipCtrl, attrString=self.cvRCornerLipLoc)
                self.utils.originedFrom(objName=self.upperLipCtrl, attrString=self.cvUpperLipLoc)
                self.utils.originedFrom(objName=self.lowerLipCtrl, attrString=self.cvLowerLipLoc)
                
                # temporary parentConstraints:
                for n in range(0, self.nJoints):
                    cmds.delete(cmds.parentConstraint(self.neckLocList[n], self.neckCtrlList[n], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvHeadLoc, self.headCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvHeadLoc, self.headSubCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperJawLoc, self.upperJawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperHeadLoc, self.upperHeadCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvJawLoc, self.jawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChinLoc, self.chinCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChewLoc, self.chewCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLCornerLipLoc, self.lCornerLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvRCornerLipLoc, self.rCornerLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperLipLoc, self.upperLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLowerLipLoc, self.lowerLipCtrl, maintainOffset=False))

                # edit the mirror shape to a good direction of controls:
                toFlipList = [self.headCtrl, self.headSubCtrl, self.upperJawCtrl, self.upperHeadCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.lCornerLipCtrl, self.rCornerLipCtrl, self.upperLipCtrl, self.lowerLipCtrl]
                # fixing flip mirror:
                if s == 1:
                    if self.addFlip:
                        for toFlipNode in toFlipList:
                            cmds.setAttr(toFlipNode+".scaleX", -1)
                            cmds.setAttr(toFlipNode+".scaleY", -1)
                            cmds.setAttr(toFlipNode+".scaleZ", -1)

                # zeroOut controls:
                self.zeroCornerLipCtrlList = self.utils.zeroOut([self.lCornerLipCtrl, self.rCornerLipCtrl])
                self.lLipGrp = cmds.group(self.lCornerLipCtrl, name=self.lCornerLipCtrl+"_Grp")
                self.rLipGrp = cmds.group(self.rCornerLipCtrl, name=self.rCornerLipCtrl+"_Grp")
                if not self.addFlip:
                    cmds.setAttr(self.zeroCornerLipCtrlList[1]+".scaleX", -1)
                self.zeroNeckCtrlList = self.utils.zeroOut(self.neckCtrlList)
                self.zeroCtrlList = self.utils.zeroOut([self.headCtrl, self.upperJawCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.upperLipCtrl, self.lowerLipCtrl, self.upperHeadCtrl])
                self.zeroCtrlList.extend(self.zeroCornerLipCtrlList)
                self.zeroCtrlList.extend(self.utils.zeroOut([self.headSubCtrl]))
                
                # make joints be ride by controls:
                for n in range(0, self.nJoints):
                    cmds.parentConstraint(self.neckCtrlList[n], self.neckJointList[n], maintainOffset=False, name=self.neckJointList[n]+"_PaC")
                    cmds.scaleConstraint(self.neckCtrlList[n], self.neckJointList[n], maintainOffset=False, name=self.neckJointList[n]+"_ScC")
                cmds.parentConstraint(self.headSubCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_PaC")
                cmds.parentConstraint(self.upperJawCtrl, self.upperJawJnt, maintainOffset=False, name=self.upperJawJnt+"_PaC")
                cmds.parentConstraint(self.upperHeadCtrl, self.upperHeadJnt, maintainOffset=False, name=self.upperHeadJnt+"_PaC")
                cmds.parentConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_PaC")
                cmds.parentConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_PaC")
                cmds.parentConstraint(self.chewCtrl, self.chewJnt, maintainOffset=False, name=self.chewJnt+"_PaC")
                cmds.parentConstraint(self.lCornerLipCtrl, self.lCornerLipJnt, maintainOffset=False, name=self.lCornerLipJnt+"_PaC")
                cmds.parentConstraint(self.rCornerLipCtrl, self.rCornerLipJnt, maintainOffset=False, name=self.rCornerLipJnt+"_PaC")
                cmds.parentConstraint(self.upperLipCtrl, self.upperLipJnt, maintainOffset=False, name=self.upperLipJnt+"_PaC")
                cmds.parentConstraint(self.lowerLipCtrl, self.lowerLipJnt, maintainOffset=False, name=self.lowerLipJnt+"_PaC")
                cmds.scaleConstraint(self.headSubCtrl, self.headJnt, maintainOffset=True, name=self.headJnt+"_ScC")
                cmds.scaleConstraint(self.upperJawCtrl, self.upperJawJnt, maintainOffset=True, name=self.upperJawJnt+"_ScC")
                cmds.scaleConstraint(self.upperHeadCtrl, self.upperHeadJnt, maintainOffset=True, name=self.upperHeadJnt+"_ScC")
                cmds.scaleConstraint(self.jawCtrl, self.jawJnt, maintainOffset=True, name=self.jawJnt+"_ScC")
                cmds.scaleConstraint(self.chinCtrl, self.chinJnt, maintainOffset=True, name=self.chinJnt+"_ScC")
                cmds.scaleConstraint(self.chewCtrl, self.chewJnt, maintainOffset=True, name=self.chewJnt+"_ScC")
                cmds.scaleConstraint(self.lCornerLipCtrl, self.lCornerLipJnt, maintainOffset=True, name=self.lCornerLipJnt+"_ScC")
                cmds.scaleConstraint(self.rCornerLipCtrl, self.rCornerLipJnt, maintainOffset=True, name=self.rCornerLipJnt+"_ScC")
                cmds.scaleConstraint(self.upperLipCtrl, self.upperLipJnt, maintainOffset=True, name=self.upperLipJnt+"_ScC")
                cmds.scaleConstraint(self.lowerLipCtrl, self.lowerLipJnt, maintainOffset=True, name=self.lowerLipJnt+"_ScC")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False))

                # hide unnecessary zero out bone display:
                self.utils.zeroOutJoints([self.lCornerLipJnt, self.rCornerLipJnt])

                # head follow/isolate create interations between neck and head:
                self.headOrientGrp = cmds.group(empty=True, name=self.headCtrl+"_Orient_Grp")
                self.zeroHeadGrp = self.utils.zeroOut([self.headOrientGrp])[0]
                cmds.parent(self.zeroHeadGrp, self.neckCtrlList[-1])
                self.worldRef = cmds.group(empty=True, name=side+self.userGuideName+"_WorldRef_Grp")
                self.worldRefList.append(self.worldRef)
                cmds.delete(cmds.parentConstraint(self.neckCtrlList[0], self.worldRef, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.zeroCtrlList[0], self.zeroHeadGrp, maintainOffset=False))
                cmds.parent(self.zeroCtrlList[0], self.headOrientGrp, absolute=True)
                headRotateParentConst = cmds.parentConstraint(self.neckCtrlList[-1], self.worldRef, self.headOrientGrp, maintainOffset=True, skipTranslate=["x", "y", "z"], name=self.headOrientGrp+"_PaC")[0]
                cmds.setAttr(headRotateParentConst+".interpType", 2) #shortest

                # connect reverseNode:
                cmds.addAttr(self.headCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, keyable=True)
                cmds.connectAttr(self.headCtrl+'.'+self.dpUIinst.lang['c032_follow'], headRotateParentConst+"."+self.neckCtrlList[-1]+"W0", force=True)
                self.headRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.dpUIinst.lang['c032_follow'].capitalize()+"_Rev")
                cmds.connectAttr(self.headCtrl+'.'+self.dpUIinst.lang['c032_follow'], self.headRevNode+".inputX", force=True)
                cmds.connectAttr(self.headRevNode+'.outputX', headRotateParentConst+"."+self.worldRef+"W1", force=True)
                
                # setup neck autoRotate:
                for n in range(0, self.nJoints):
                    self.neckPivot = cmds.xform(self.neckCtrlList[n], query=True, worldSpace=True, translation=True)
                    self.neckOrientGrp = cmds.group(self.neckCtrlList[n], name=self.neckCtrlList[n]+"_Orient_Grp")
                    cmds.xform(self.neckOrientGrp, pivots=(self.neckPivot[0], self.neckPivot[1], self.neckPivot[2]), worldSpace=True)
                    cmds.addAttr(self.neckCtrlList[n], longName=self.dpUIinst.lang['c047_autoRotate'], attributeType='float', minValue=0, maxValue=1, defaultValue=self.autoRotateCalc(n), keyable=True)
                    neckARMDName = self.dpUIinst.lang['c047_autoRotate'][0].capitalize()+self.dpUIinst.lang['c047_autoRotate'][1:]
                    neckARMD = cmds.createNode('multiplyDivide', name=self.neckCtrlList[n]+"_"+neckARMDName+"_MD")
                    cmds.connectAttr(self.headCtrl+".rotateX", neckARMD+".input1X", force=True)
                    cmds.connectAttr(self.headCtrl+".rotateY", neckARMD+".input1Y", force=True)
                    cmds.connectAttr(self.headCtrl+".rotateZ", neckARMD+".input1Z", force=True)
                    cmds.connectAttr(self.neckCtrlList[n]+"."+self.dpUIinst.lang['c047_autoRotate'], neckARMD+".input2X", force=True)
                    cmds.connectAttr(self.neckCtrlList[n]+"."+self.dpUIinst.lang['c047_autoRotate'], neckARMD+".input2Y", force=True)
                    cmds.connectAttr(self.neckCtrlList[n]+"."+self.dpUIinst.lang['c047_autoRotate'], neckARMD+".input2Z", force=True)
                    cmds.connectAttr(neckARMD+".outputX", self.neckOrientGrp+".rotateX", force=True)
                    if self.rigType == dpBaseClass.RigType.quadruped:
                        cmds.connectAttr(neckARMD+".outputZ", self.neckOrientGrp+".rotateY", force=True)
                        quadrupedRotYZFixMD = cmds.createNode('multiplyDivide', name=self.neckCtrlList[n]+"_"+neckARMDName+"_YZ_Fix_MD")
                        cmds.connectAttr(neckARMD+".outputY", quadrupedRotYZFixMD+".input1X", force=True)
                        cmds.setAttr(quadrupedRotYZFixMD+".input2X", -1)
                        cmds.connectAttr(quadrupedRotYZFixMD+".outputX", self.neckOrientGrp+".rotateZ", force=True)
                    else:
                        cmds.connectAttr(neckARMD+".outputY", self.neckOrientGrp+".rotateY", force=True)
                        cmds.connectAttr(neckARMD+".outputZ", self.neckOrientGrp+".rotateZ", force=True)
                
                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[3], self.jawCtrl, absolute=True) #chinCtrl
                cmds.parent(self.zeroCtrlList[4], self.zeroCtrlList[6], self.chinCtrl, absolute=True) #chewCtrl, lowerLipCtrl
                cmds.parent(self.zeroCtrlList[5], self.zeroCtrlList[7], self.upperJawCtrl, absolute=True) #upperLipCtrl, upperHeadCtrl
                
                # jaw follow sub head or root ctrl (using worldRef)
                jawParentConst = cmds.parentConstraint(self.headSubCtrl, self.worldRef, self.zeroCtrlList[2], maintainOffset=True, name=self.zeroCtrlList[2]+"_PaC")[0]
                cmds.setAttr(jawParentConst+".interpType", 2) #Shortest, no flip cause problem with scrubing
                cmds.addAttr(self.jawCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.connectAttr(self.jawCtrl+"."+self.dpUIinst.lang['c032_follow'], jawParentConst+"."+self.headSubCtrl+"W0", force=True)
                jawFollowRev = cmds.createNode("reverse", name=self.jawCtrl+"_Rev")
                cmds.connectAttr(self.jawCtrl+"."+self.dpUIinst.lang['c032_follow'], jawFollowRev+".inputX", force=True)
                cmds.connectAttr(jawFollowRev+".outputX", jawParentConst+"."+self.worldRef+"W1", force=True)
                cmds.scaleConstraint(self.headSubCtrl, self.zeroCtrlList[2], maintainOffset=True, name=self.zeroCtrlList[2]+"_ScC")[0]
                
                # setup jaw move:
                # jaw open:
                self.setupJawMove(self.jawCtrl, "c108_open", True, "Y", "c049_intensity", createOutput=True)
                self.setupJawMove(self.jawCtrl, "c108_open", True, "Z", "c049_intensity")
                # jaw close:
                self.setupJawMove(self.jawCtrl, "c109_close", False, "Y", "c049_intensity", createOutput=True)
                self.setupJawMove(self.jawCtrl, "c109_close", False, "Z", "c049_intensity")
                # upper lid close:
                self.setupJawMove(self.upperLipCtrl, "c109_close", False, "Y", "c039_lip")
                self.setupJawMove(self.upperLipCtrl, "c109_close", False, "Z", "c039_lip")
                # lower lid close:
                self.setupJawMove(self.lowerLipCtrl, "c109_close", False, "Y", "c039_lip", invertRot=True)
                self.setupJawMove(self.lowerLipCtrl, "c109_close", False, "Z", "c039_lip")
                
                # set jaw move and lips calibrate default values:
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c110_start'].capitalize()+"Rotation", 5)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y", -2)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z", 0)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output'], 30)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output'], -10)
                cmds.setAttr(self.upperLipCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z", 2)
                cmds.setAttr(self.lowerLipCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y", 0)
                cmds.setAttr(self.lowerLipCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z", 2)
                
                # upper lip follows lower lip:
                cmds.addAttr(self.upperLipCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                upperLipConst = cmds.parentConstraint(self.upperJawCtrl, self.lowerLipCtrl, self.zeroCtrlList[5], maintainOffset=True, name=self.zeroCtrlList[5]+"_PaC")[0]
                upperLipRev = cmds.createNode("reverse", name=self.zeroCtrlList[5]+"_Follow_Rev")
                cmds.connectAttr(self.upperLipCtrl+"."+self.dpUIinst.lang['c032_follow'], upperLipRev+".inputX", force=True)
                cmds.connectAttr(self.upperLipCtrl+"."+self.dpUIinst.lang['c032_follow'], upperLipConst+"."+self.lowerLipCtrl+"W1", force=True)
                cmds.connectAttr(upperLipRev+".outputX", upperLipConst+"."+self.upperJawCtrl+"W0", force=True)

                # left side lip:
                lLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperJawCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_PaC")[0]
                cmds.setAttr(lLipParentConst+".interpType", 2)
                cmds.addAttr(self.lCornerLipCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.lCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], lLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.lLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.dpUIinst.lang['p002_left']+"_"+self.dpUIinst.lang['c039_lip']+"_Rev")
                cmds.connectAttr(self.lCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], self.lLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.lLipRevNode+'.outputX', lLipParentConst+"."+self.upperJawCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperJawCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_ScC")[0]
                # right side lip:
                rLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperJawCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_PaC")[0]
                cmds.setAttr(rLipParentConst+".interpType", 2)
                cmds.addAttr(self.rCornerLipCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.rCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], rLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.rLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.dpUIinst.lang['p003_right']+"_"+self.dpUIinst.lang['c039_lip']+"_Rev")
                cmds.connectAttr(self.rCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], self.rLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.rLipRevNode+'.outputX', rLipParentConst+"."+self.upperJawCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperJawCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_ScC")[0]
                
                # articulation joint:
                if self.addArticJoint:
                    # neckBase
                    neckBaseJzt = self.utils.zeroOutJoints([self.neckJointList[0]])[0]
                    if self.addCorrective:
                        # corrective controls group
                        self.correctiveCtrlsGrp = cmds.group(name=side+self.userGuideName+"_Corrective_Grp", empty=True)
                        self.correctiveCtrlGrpList.append(self.correctiveCtrlsGrp)
                        neckHeadCalibratePresetList, invertList = self.getCalibratePresetList(s)
                        
                        # neck corrective
                        for n in range(0, self.nJoints):
                            if n == 0:
                                fatherJoint = neckBaseJzt
                            else:
                                fatherJoint = self.neckJointList[n-1]
                            correctiveNetList = [None]
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_YawRight", 2, 2, -80))
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_YawLeft", 2, 2, 80))
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_PitchUp", 0, 0, 80))
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_PitchDown", 0, 0, -80))
                            
                            articJntList = self.utils.articulationJoint(fatherJoint, self.neckJointList[n], 4, [(0.5*self.ctrlRadius, 0, 0), (-0.5*self.ctrlRadius, 0, 0), (0, 0, 0.5*self.ctrlRadius), (0, 0, -0.5*self.ctrlRadius)])
                            self.setupJcrControls(articJntList, s, jointLabelAdd, neckCtrlBaseName+"_"+str(n), correctiveNetList, neckHeadCalibratePresetList, invertList, [False, True, True, False, False])
                            if s == 1:
                                if self.addFlip:
                                    cmds.setAttr(articJntList[0]+".scaleX", -1)
                                    cmds.setAttr(articJntList[0]+".scaleY", -1)
                                    cmds.setAttr(articJntList[0]+".scaleZ", -1)
                            self.utils.setJointLabel(articJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c023_neck']+"_"+str(n)+"_Jar")

                        # head corrective
                        headCorrectiveNetList = [None]
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_YawRight", 2, 2, -80))
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_YawLeft", 2, 2, 80))
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_PitchUp", 0, 0, 80))
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_PitchDown", 0, 0, -80))
                        headCalibratePresetList, invertList = self.getCalibratePresetList(s)
                        articJntList = self.utils.articulationJoint(self.neckJointList[-1], self.headJnt, 4, [(0.5*self.ctrlRadius, 0, 0), (-0.5*self.ctrlRadius, 0, 0), (0, 0, 0.5*self.ctrlRadius), (0, 0, -0.5*self.ctrlRadius)])
                        self.setupJcrControls(articJntList, s, jointLabelAdd, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head'], headCorrectiveNetList, headCalibratePresetList, invertList, [False, True, True, False, False])
                        if s == 1:
                            if self.addFlip:
                                cmds.setAttr(articJntList[0]+".scaleX", -1)
                                cmds.setAttr(articJntList[0]+".scaleY", -1)
                                cmds.setAttr(articJntList[0]+".scaleZ", -1)
                    else:
                        articJntList = self.utils.articulationJoint(neckBaseJzt, self.neckJointList[0])
                        self.utils.setJointLabel(articJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_00_"+self.dpUIinst.lang['c023_neck']+self.dpUIinst.lang['c106_base']+"_Jar")
                        cmds.rename(articJntList[0], side+self.userGuideName+"_00_"+self.dpUIinst.lang['c023_neck']+self.dpUIinst.lang['c106_base']+"_Jar")
                        articJntList = self.utils.articulationJoint(self.neckJointList[-1], self.headJnt)
                    
                    self.neckJointList.insert(0, neckBaseJzt)
                    cmds.parentConstraint(self.zeroNeckCtrlList[0], neckBaseJzt, maintainOffset=True, name=neckBaseJzt+"_PaC")
                    cmds.scaleConstraint(self.zeroNeckCtrlList[0], neckBaseJzt, maintainOffset=True, name=neckBaseJzt+"_ScC")
                    self.utils.setJointLabel(articJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_01_"+self.dpUIinst.lang['c024_head']+self.dpUIinst.lang['c106_base']+"_Jar")
                    cmds.rename(articJntList[0], side+self.userGuideName+"_01_"+self.dpUIinst.lang['c024_head']+self.dpUIinst.lang['c106_base']+"_Jar")
                
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE_PLEASE_Loc")[0]
                cmds.parent(loc, self.worldRef, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                
                # hiding visibility attributes:
                self.ctrls.setLockHide([self.headCtrl, self.upperJawCtrl, self.upperHeadCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.upperLipCtrl, self.lowerLipCtrl], ['v'], l=False)
                self.ctrls.setLockHide(self.neckCtrlList, ['v'], l=False)

                # arrange controllers hierarchy
                cmds.parent(self.zeroCtrlList[-1], self.zeroCtrlList[1], self.headCtrl, absolute=True) #headSubCtrl
                cmds.parent(self.zeroCtrlList[1], self.headSubCtrl, absolute=True) #upperJawCtrl
                
                # calibration attributes:
                neckCalibrationList = [self.dpUIinst.lang['c047_autoRotate']]
                jawCalibrationList = [
                                    self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y",
                                    self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z",
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y",
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z",
                                    self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output'],
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output']
                ]
                lipCalibrationList = [
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y",
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z"
                ]
                self.ctrls.setCalibrationAttr(self.neckCtrlList[0], neckCalibrationList)
                self.ctrls.setCalibrationAttr(self.jawCtrl, jawCalibrationList)
                self.ctrls.setCalibrationAttr(self.upperLipCtrl, lipCalibrationList)
                self.ctrls.setCalibrationAttr(self.lowerLipCtrl, lipCalibrationList)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.zeroNeckCtrlList[0], self.zeroCtrlList[2], self.zeroCtrlList[8], self.zeroCtrlList[9], name=side+self.userGuideName+"_Control_Grp")
                if self.addCorrective:
                    cmds.parent(self.correctiveCtrlsGrp, self.toCtrlHookGrp)
                self.toScalableHookGrp = cmds.group(self.neckJointList[0], name=side+self.userGuideName+"_Scalable_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.worldRef, name=side+self.userGuideName+"_Static_Grp")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                # add hook attributes to be read when rigging integrated modules:
                self.utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                self.utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                self.utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                self.hookSetup()
                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)

                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
    
    
    def dpCreateFacialCtrl(self, side, ctrlName, cvCtrl, attrList, rotVector=(0, 0, 0), lockX=False, lockY=False, lockZ=False, limitX=True, limitY=True, limitZ=True, directConnection=False, connectBS=True, connectJnt=False, color='yellow', headDefInfluence=False, jawDefInfluence=False, addTranslateY=False, limitMinY=False, *args):
        """ Important function to receive called parameters and create the specific asked control.
            Convention:
                transfList = ["tx", "tx", "ty", "ty", "tz", "tz]
                axisDirectionList = [-1, 1, -1, 1, -1, 1] # neg, pos, neg, pos, neg, pos
            Returns the created Facial control and its zeroOut group.
        """
        # force limits when working on facial joints:
        if connectJnt:
            limitX = True
            limitY = True
            limitZ = True
        
        # declaring variables:
        fCtrl = None
        fCtrlGrp = None
        
        calibrationList = []
        transfList = ["tx", "tx", "ty", "ty", "tz", "tz"]
        # naming:
        if not side == None:
            ctrlName = side+"_"+ctrlName
        fCtrlName = ctrlName+"_Ctrl"
        # skip if already there is this ctrl object:
        if cmds.objExists(fCtrlName):
            return None, None
        else:
            if self.facialUserType == self.bsType:
                if connectBS and self.bsNode:
                    # validating blendShape node:
                    if cmds.objectType(self.bsNode) == "blendShape":
                        aliasList = cmds.aliasAttr(self.bsNode, query=True)
            # create control calling dpControls function:
            fCtrl = self.ctrls.cvControl(cvCtrl, fCtrlName, d=0, rot=rotVector)
            # add head or jaw influence attribute
            if headDefInfluence:
                self.ctrls.addDefInfluenceAttrs(fCtrl, 1)                
            if jawDefInfluence:
                self.ctrls.addDefInfluenceAttrs(fCtrl, 2)
            # ctrl zeroOut grp and color:
            fCtrlGrp = self.utils.zeroOut([fCtrl])[0]
            self.ctrls.colorShape([fCtrl], color)
            # lock or limit XYZ axis:
            self.dpLockLimitAttr(fCtrl, ctrlName, [lockX, lockY, lockZ], [limitX, limitY, limitZ], limitMinY)
            self.ctrls.setLockHide([fCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
            # start work with custom attributes
            if attrList:
                for a, attr in enumerate(attrList):
                    if not attr == None:
                        if directConnection:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0, minValue=0, maxValue=1)
                            cmds.setAttr(fCtrl+"."+attr, keyable=True)
                        else:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0)
                            calibrateMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Calibrate_MD")
                            clp = cmds.createNode("clamp", name=ctrlName+"_"+attr+"_Clp")
                            invMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Invert_MD")
                            if a == 0 or a == 2 or a == 4: #negative
                                cmds.setAttr(clp+".minR", -1000)
                                cmds.setAttr(invMD+".input2X", -1)
                            else: #positive
                                cmds.setAttr(clp+".maxR", 1000)
                            # connect nodes:
                            cmds.connectAttr(fCtrl+"."+transfList[a], calibrateMD+".input1X", force=True)
                            if a == 0 or a == 1: # -x or +x
                                cmds.connectAttr(fCtrl+"."+self.calibrateName+"TX", calibrateMD+".input2X", force=True)
                                if not self.calibrateName+"TX" in calibrationList:
                                    calibrationList.append(self.calibrateName+"TX")
                            elif a == 2 or a == 3: # -y or +y
                                cmds.connectAttr(fCtrl+"."+self.calibrateName+"TY", calibrateMD+".input2X", force=True)
                                if not self.calibrateName+"TY" in calibrationList:
                                    calibrationList.append(self.calibrateName+"TY")
                            else: # -z or +z
                                cmds.connectAttr(fCtrl+"."+self.calibrateName+"TZ", calibrateMD+".input2X", force=True)
                                if not self.calibrateName+"TZ" in calibrationList:
                                    calibrationList.append(self.calibrateName+"TZ")
                            if addTranslateY: #useful for Sneer and Grimace
                                integrateTYPMA = cmds.createNode("plusMinusAverage", name=ctrlName+"_"+attr+"_TY_PMA")
                                cmds.connectAttr(calibrateMD+".outputX", integrateTYPMA+".input1D[0]", force=True)
                                if not "Front" in attr:
                                    cmds.connectAttr(fCtrl+".translateY", integrateTYPMA+".input1D[1]", force=True)
                                cmds.connectAttr(integrateTYPMA+".output1D", clp+".input.inputR", force=True)
                                if "R_" in attr: #hack to set operation as substract in PMA node for Right side
                                    cmds.setAttr(integrateTYPMA+".operation", 2)
                                cmds.setAttr(fCtrl+"."+self.calibrateName+"TY", lock=True)
                            else:
                                cmds.connectAttr(calibrateMD+".outputX", clp+".input.inputR", force=True)
                            cmds.connectAttr(clp+".outputR", invMD+".input1X", force=True)
                            cmds.connectAttr(invMD+".outputX", fCtrl+"."+attr, force=True)
                            cmds.setAttr(fCtrl+"."+attr, lock=True)
                        
                        if self.facialUserType == self.bsType:
                            # try to connect attributes into blendShape node:
                            if connectBS and self.bsNode:
                                addedSide = False
                                storedAttr = attr
                                for i, alias in enumerate(aliasList):
                                    if not side == None and not addedSide:
                                        attr = side+"_"+attr
                                        addedSide = True
                                    if attr in alias:
                                        try:
                                            cmds.connectAttr(fCtrl+"."+attr, self.bsNode+"."+alias, force=True)
                                        except:
                                            try:
                                                cmds.connectAttr(fCtrl+"."+storedAttr, self.bsNode+"."+alias, force=True)
                                            except:
                                                pass
#                        else: # setup to using facial joints:
#                            if connectJnt:
#                                sidedNodeList = None
#                                try:
#                                    sidedNodeList = self.tweaksDic[attr]
#                                except:
#                                    pass
#                                if sidedNodeList:
#                                    # sideNode is like MIDDLE or SIDED:
#                                    for sidedNode in sidedNodeList:
#                                        toNodeList = None
#                                        try:
#                                            toNodeList = self.tweaksDic[attr][sidedNode]
#                                        except:
#                                            pass
#                                        if toNodeList:
#                                            # toNodeBase is igual to facial control offset group target:
#                                            for toNodeBaseName in toNodeList:
#                                                toNode = None
#                                                toNodeSided = toNodeBaseName
#                                                addedSide = False
#                                                toNodeTargedList = []
#                                                for jntTarget in self.jntTargetList:
#                                                    toNodeSided = toNodeBaseName
#                                                    if sidedNode == SIDED:
#                                                        if not addedSide:
#                                                            if not side == None:
#                                                                # check prefix:
#                                                                if jntTarget[1] == "_":
#                                                                    if side == jntTarget[0]:
#                                                                        toNodeSided = side+"_"+toNodeBaseName
#                                                                        if jntTarget.startswith(toNodeSided):    
#                                                                            toNode = jntTarget
#                                                                            addedSide = True
#                                                            elif toNodeSided in jntTarget:
#                                                                if attr[1] == "_":
#                                                                    if attr[0] == jntTarget[0]:
#                                                                        toNode = jntTarget
#                                                                        addedSide = True
#                                                                else:
#                                                                    toNodeTargedList.append(jntTarget)
#                                                                    toNode = jntTarget
#                                                    elif jntTarget.startswith(toNodeSided):
#                                                        if cmds.objExists(jntTarget):
#                                                            toNode = jntTarget
#                                                if toNode:
#                                                    if not toNodeTargedList:
#                                                        toNodeTargedList.append(toNode)
#                                                    for toNode in toNodeTargedList:
#                                                        if cmds.objExists(toNode):
#                                                            # caculate factor for scaled item:
#                                                            sizeFactor = self.dpGetSizeFactor(toNode)
#                                                            if not sizeFactor:
#                                                                sizeFactor = 1
#                                                            toAttrList = self.tweaksDic[attr][sidedNode][toNodeBaseName]
#                                                            for toAttr in toAttrList:
#                                                                # read stored values in order to call function to make the setup:
#                                                                oMin = self.tweaksDic[attr][sidedNode][toNodeBaseName][toAttr][0]
#                                                                oMax = self.tweaksDic[attr][sidedNode][toNodeBaseName][toAttr][1]
#                                                                self.dpCreateRemapNode(fCtrl, attr, toNodeBaseName, toNode, toAttr, self.RmVNumber, sizeFactor, oMin, oMax)
#                                                                self.RmVNumber = self.RmVNumber+1
            if calibrationList:
                self.ctrls.setCalibrationAttr(fCtrl, calibrationList)
            # parenting the hierarchy:
#            if not cmds.objExists(self.headFacialCtrlsGrp):
#                cmds.group(name=self.headFacialCtrlsGrp, empty=True)
#            cmds.parent(fCtrlGrp, self.headFacialCtrlsGrp)
        
#        cmds.select(self.headFacialCtrlsGrp)
        return fCtrl, fCtrlGrp
    
    
    def dpLockLimitAttr(self, fCtrl, ctrlName, lockList, limitList, limitMinY, *args):
        """ Lock or limit attributes for XYZ.
        """
        axisList = ["X", "Y", "Z"]
        for i, axis in enumerate(axisList):
            if lockList[i]:
                cmds.setAttr(fCtrl+".translate"+axis, lock=True, keyable=False)
            else:
                # add calibrate attributes:
                cmds.addAttr(fCtrl, longName=self.calibrateName+"T"+axis, attributeType="float", defaultValue=1, minValue=0.001)
                if limitList[i]:
                    if i == 0: #X
                        cmds.transformLimits(fCtrl, enableTranslationX=(1, 1))
                    elif i == 1: #Y
                        cmds.transformLimits(fCtrl, enableTranslationY=(1, 1))
                    else: #Z
                        cmds.transformLimits(fCtrl, enableTranslationZ=(1, 1))
                    self.dpLimitTranslate(fCtrl, ctrlName, axis, limitMinY)

    
    def dpLimitTranslate(self, fCtrl, ctrlName, axis, limitMinY=False, *args):
        """ Create a hyperbolic setup to limit min and max value for translation of the control.
            Resuming it's just divide 1 by the calibrate value.
        """
        hyperboleTLimitMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_MD")
        hyperboleInvMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_Inv_MD")
        cmds.setAttr(hyperboleTLimitMD+".input1X", 1)
        cmds.setAttr(hyperboleTLimitMD+".operation", 2)
        cmds.setAttr(hyperboleInvMD+".input2X", -1)
        cmds.connectAttr(fCtrl+"."+self.calibrateName+"T"+axis, hyperboleTLimitMD+".input2X", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", fCtrl+".maxTransLimit.maxTrans"+axis+"Limit", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", hyperboleInvMD+".input1X", force=True)
        if not limitMinY:
            cmds.connectAttr(hyperboleInvMD+".outputX", fCtrl+".minTransLimit.minTrans"+axis+"Limit", force=True)
        else:
            cmds.transformLimits(fCtrl, translationY=(0, 1))
    
    
    def dpCreateRemapNode(self, fromNode, fromAttr, toNodeBaseName, toNode, toAttr, number, sizeFactor, oMin=0, oMax=1, iMin=0, iMax=1, *args):
        """ Creates the nodes to remap values and connect it to final output (toNode) item.
        """
        fromNodeName = self.utils.extractSuffix(fromNode)
        remap = cmds.createNode("remapValue", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_RmV")
        outMaxAttr = toNodeBaseName+"_"+str(number).zfill(2)+"_"+toAttr.upper()
        if "t" in toAttr:
            if not cmds.objExists(fromNode+".sizeFactor"):
                cmds.addAttr(fromNode, longName="sizeFactor", attributeType="float", defaultValue=sizeFactor, keyable=False)
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
            md = cmds.createNode("multiplyDivide", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_SizeFactor_MD")
            cmds.connectAttr(fromNode+"."+outMaxAttr, md+".input1X", force=True)
            cmds.connectAttr(fromNode+".sizeFactor", md+".input2X", force=True)
            cmds.connectAttr(md+".outputX", remap+".outputMax", force=True)
        else:
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
            cmds.connectAttr(fromNode+"."+outMaxAttr, remap+".outputMax", force=True)
        cmds.setAttr(remap+".inputMin", iMin)
        cmds.setAttr(remap+".inputMax", iMax)
        cmds.setAttr(remap+".outputMin", oMin)
        cmds.connectAttr(fromNode+"."+fromAttr, remap+".inputValue", force=True)
        # check if there's an input connection and create a plusMinusAverage if we don't have one to connect in:
        connectedList = cmds.listConnections(toNode+"."+toAttr, destination=False, source=True, plugs=False)
        if connectedList:
            if cmds.objectType(connectedList[0]) == "plusMinusAverage":
                inputList = cmds.listConnections(connectedList[0]+".input1D", destination=False, source=True, plugs=False)
                cmds.connectAttr(remap+".outValue", connectedList[0]+".input1D["+str(len(inputList))+"]", force=True)
            else:
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    connectedAttr = cmds.listConnections(connectedList[0]+".input", destination=False, source=True, plugs=True)[0]
                else:
                    connectedAttr = cmds.listConnections(toNode+"."+toAttr, destination=False, source=True, plugs=True)[0]
                pma = cmds.createNode("plusMinusAverage", name=toNode+"_"+toAttr.upper()+"_PMA")
                cmds.connectAttr(connectedAttr, pma+".input1D[0]", force=True)
                cmds.connectAttr(remap+".outValue", pma+".input1D[1]", force=True)
                cmds.connectAttr(pma+".output1D", toNode+"."+toAttr, force=True)
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    cmds.delete(connectedList[0])
        else:
            cmds.connectAttr(remap+".outValue", toNode+"."+toAttr, force=True)
    

    def dpGetSizeFactor(self, toNode, *args):
        """ Get the child control size value and return it.
        """
        childrenList = cmds.listRelatives(toNode, children=True, type="transform")
        if childrenList:
            for child in childrenList:
                if cmds.objExists(child+".dpControl"):
                    if cmds.getAttr(child+".dpControl") == 1:
                        if cmds.objExists(child+".size"):
                            sizeValue = cmds.getAttr(child+".size")
                            return sizeValue
    
    
    def integratingInfo(self, *args):
        dpBaseClass.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "worldRefList"         : self.worldRefList,
                                                "upperCtrlList"        : self.upperCtrlList,
                                                "ctrlList"             : self.aCtrls,
                                                "InnerCtrls"           : self.aInnerCtrls,
                                                "lCtrls"               : self.aLCtrls,
                                                "rCtrls"               : self.aRCtrls,
                                                "correctiveCtrlGrpList": self.correctiveCtrlGrpList,
                                                "upperJawCtrlList"     : self.upperJawCtrlList
                                              }
                                    }