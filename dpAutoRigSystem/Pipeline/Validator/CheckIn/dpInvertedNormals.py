# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "InvertedNormals"
TITLE = "v086_invertedNormals"
DESCRIPTION = "v087_invertedNormalsDesc"
ICON = "/Icons/dp_invertedNormals.png"

DP_INVERTEDNORMALS_VERSION = 1.1


class InvertedNormals(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_INVERTEDNORMALS_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

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
            invertedObjList = []
            if objList:
                objMeshList = objList
            else:
                objMeshList = cmds.ls(selection=False, type='mesh')
            if objMeshList:
                self.utils.setProgress(max=len(objMeshList), addOne=False, addNumber=False)
                geomIter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kMesh)
                while not geomIter.isDone():
                    nextGeom = False
                    useThisObj = False
                    # get mesh data
                    shapeNode = geomIter.thisNode()
                    fnShapeNode = OpenMaya.MFnDagNode(shapeNode)
                    shapeName = fnShapeNode.name()
                    parentNode = fnShapeNode.parent(0)
                    fnParentNode = OpenMaya.MFnDagNode(parentNode)
                    objName = fnParentNode.name()
                    self.utils.setProgress(self.dpUIinst.lang[self.title]+": "+shapeName)
                    # verify if objName or shapeName is in objMeshList
                    for obj in objMeshList:
                        if objName in obj or shapeName in obj:
                            useThisObj = True
                            break
                    if useThisObj:
                        # get faces
                        faceIter   = OpenMaya.MItMeshPolygon(shapeNode)
                        conFacesIt = OpenMaya.MItMeshPolygon(shapeNode)
                        # run in faces listing vertices
                        while not faceIter.isDone() and not nextGeom:
                            # list vertices from this face
                            vtxIntArray = OpenMaya.MIntArray()
                            faceIter.getVertices(vtxIntArray)
                            vtxIntArray.append(vtxIntArray[0])
                            # get connected faces of this face
                            conFacesIntArray = OpenMaya.MIntArray()
                            faceIter.getConnectedFaces(conFacesIntArray)
                            # run in adjacent faces to list them vertices
                            for f in conFacesIntArray:
                                # say this is the face index to use for next iterations
                                lastIndexPtr = OpenMaya.MScriptUtil().asIntPtr()
                                conFacesIt.setIndex(f, lastIndexPtr)
                                # get vertices from this adjacent face
                                conVtxIntArray = OpenMaya.MIntArray()
                                conFacesIt.getVertices(conVtxIntArray)
                                conVtxIntArray.append(conVtxIntArray[0])
                                # compare vertex in order to find double consecutive vertices
                                for i in range(0, len(vtxIntArray)-1):
                                    iPair = str(vtxIntArray[i])+","+str(vtxIntArray[i+1])
                                    for c in range(0, len(conVtxIntArray)-1):
                                        cPair = str(conVtxIntArray[c])+","+str(conVtxIntArray[c+1])
                                        if iPair == cPair:
                                            # found inverted normals
                                            invertedObjList.append(objName)
                                            nextGeom = True
                            faceIter.next()
                    # go to next geometry
                    geomIter.next()
            # verify if there are inverted normals
            if invertedObjList:
                invertedObjList = list(set(invertedObjList))
                for mesh in invertedObjList:
                    self.checkedObjList.append(mesh)
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            # conform normals to fix
                            cmds.polyNormal(mesh, normalMode=2, userNormalMode=0, constructionHistory=False)
                            #cmds.setAttr(mesh+".displayNormal", 0)
                            #cmds.setAttr(mesh+".doubleSided", 0)
                            #cmds.setAttr(mesh+".opposite", 0)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+mesh)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+mesh)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic