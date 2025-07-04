# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = 'FreezeTransform'
TITLE = 'v015_freezeTransform'
DESCRIPTION = 'v016_freezeTranformDesc'
ICON = '/Icons/dp_freezeTransform.png'

DP_FREEZETRANSFORM_VERSION = 1.7


class FreezeTransform(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs['CLASS_NAME'] = CLASS_NAME
        kwargs['TITLE'] = TITLE
        kwargs['DESCRIPTION'] = DESCRIPTION
        kwargs['ICON'] = ICON
        self.version = DP_FREEZETRANSFORM_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)


    def runAction(self, firstMode=True, objList=None, *args):
        ''' Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        '''
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
        if not self.utils.getAllGrp():
            if not self.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    allObjectList = []
                    toFixList = []
                    if objList:
                        allObjectList = list(filter(lambda obj: cmds.objectType(obj) == 'transform', objList))
                    if len(allObjectList) == 0:
                        allObjectList = cmds.ls(selection=False, type='transform', long=True)
                    # analisys transformations
                    if len(allObjectList) > 0:
                        self.utils.setProgress(max=len(allObjectList), addOne=False, addNumber=False)
                        self.animCurvesList = cmds.ls(type='animCurve')
                        zeroAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
                        oneAttrList = ['scaleX', 'scaleY', 'scaleZ']
                        camerasList = ['|persp', '|top', '|side', '|front', '|bottom', '|back', '|left']
                        allValidObjs = list(filter(lambda obj: obj not in camerasList, allObjectList))
                        for idx, obj in enumerate(allValidObjs):
                            self.utils.setProgress(self.dpUIinst.lang[self.title])
                            if cmds.objExists(obj):
                                # run for translates and rotates
                                frozenTR = self.checkFrozenObject(obj, zeroAttrList, 0)
                                # run for scales
                                frozenS = self.checkFrozenObject(obj, oneAttrList, 1)
                                self.checkedObjList.append(obj)
                                if frozenTR and frozenS:
                                    self.foundIssueList.append(False)
                                    self.resultOkList.append(True)
                                else:
                                    self.foundIssueList.append(True)
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v018_foundTransform']+obj)
                                    toFixList.append((obj, idx))
                        if not self.firstMode and len(toFixList) > 0: #one item to fix
                            for obj in toFixList:
                                if self.unlockAttributes(obj[0], zeroAttrList) and self.unlockAttributes(obj[0], oneAttrList):
                                    try:
                                        cmds.makeIdentity(obj[0], apply=True, translate=True, rotate=True, scale=True)
                                        if self.checkFrozenObject(obj[0], zeroAttrList, 0) and self.checkFrozenObject(obj[0], oneAttrList, 1):
                                            self.foundIssueList[obj[1]] = False
                                            self.resultOkList[obj[1]] = True
                                            self.messageList.append(self.dpUIinst.lang['v019_frozenTransform']+obj[0])
                                        else:
                                            raise Exception('Freeze Tranform Failed')
                                    except:
                                        self.messageList.append(self.dpUIinst.lang['v017_freezeError'] + obj+'.')
                                else:
                                    self.messageList.append(self.dpUIinst.lang['v017_freezeError'] + obj+'.')
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v100_cantExistsGuides'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def checkFrozenObject(self, obj, attrList, compValue, *args):
        """ Compare values.
            Return True if equal.
        """
        for attr in attrList:
            if cmds.getAttr(obj+'.'+attr) != compValue:
                return False
        return True


    def unlockAttributes(self, obj, attrList, *args):
        """ Just unlock attributes.
        """
        for attr in attrList:
            if self.animCurvesList:
                if obj+'_'+attr in self.animCurvesList:
                    return False
                else:
                    cmds.setAttr(obj+'.'+attr, lock=False)
            else:
                cmds.setAttr(obj+'.'+attr, lock=False)
        return True
