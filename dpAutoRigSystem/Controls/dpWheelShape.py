# importing libraries:
from maya import cmds
from . import dpBaseControlClass
from importlib import reload
reload(dpBaseControlClass)

# global variables to this module:    
CLASS_NAME = "WheelShape"
TITLE = "m162_wheelShape"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_wheelShape.png"

dpWheelShapeVersion = 1.1

class WheelShape(dpBaseControlClass.ControlStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseControlClass.ControlStartClass.__init__(self, *args, **kwargs)
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        result = self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide)
        return result
    
    
    def getLinearPoints(self, *args):
        """ Get a list of linear points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, -r, 0), (0.382*r, -0.921*r, 0), (0.707*r, -0.707*r, 0), (0.92*r, -0.381*r, 0), (r, 0, 0), 
                            (0.92*r, 0.381*r, 0), (0.708*r, 0.708*r, 0), (0.385*r, 0.92*r, 0), (0, r, 0), (-0.385*r, 0.92*r, 0), 
                            (-0.708*r, 0.708*r, 0), (-0.92*r, 0.381*r, 0), (-r, 0, 0), (-0.92*r, -0.381*r, 0), (-0.707*r, -0.707*r, 0), 
                            (-0.382*r, -0.921*r, 0), (0, -r, 0), (0, -0.722*r, 0), (0.276*r, -0.666*r, 0), (0.51*r, -0.51*r, 0), 
                            (0.667*r, -0.274*r, 0), (0.723*r, 0, 0), (0.667*r, 0.278*r, 0), (0.516*r, 0.511*r, 0), (0.277*r, 0.666*r, 0), 
                            (0, 0.726*r, 0), (-0.277*r, 0.666*r, 0), (-0.516*r, 0.511*r, 0), (-0.667*r, 0.278*r, 0), (-0.723*r, 0, 0), 
                            (-0.667*r, -0.274*r, 0), (-0.51*r, -0.51*r, 0), (-0.276*r, -0.666*r, 0), (0, -0.722*r, 0), (0, -0.333*r, 0),
                            (0.125*r, -0.307*r, 0), (0.236*r, -0.236*r, 0), (0.306*r, -0.129*r, 0), (0.333*r, 0, 0), (0.308*r, 0.127*r, 0), 
                            (0.237*r, 0.237*r, 0), (0.127*r, 0.308*r, 0), (0, 0.335*r, 0), (-0.127*r, 0.308*r, 0), (-0.237*r, 0.237*r, 0), 
                            (-0.308*r, 0.127*r, 0), (-0.333*r, 0, 0), (-0.306*r, -0.129*r, 0), (-0.236*r, -0.236*r, 0), (-0.125*r, -0.307*r, 0), 
                            (0, -0.333*r, 0), (0.125*r, -0.307*r, 0), (0.276*r, -0.666*r, 0), (0.51*r, -0.51*r, 0), (0.667*r, -0.274*r, 0), 
                            (0.306*r, -0.129*r, 0), (0.333*r, 0, 0), (0.723*r, 0, 0), (0.667*r, 0.278*r, 0), (0.516*r, 0.511*r, 0), 
                            (0.237*r, 0.237*r, 0), (0.127*r, 0.308*r, 0), (0.277*r, 0.666*r, 0), (0, 0.726*r, 0), (-0.277*r, 0.666*r, 0), 
                            (-0.127*r, 0.308*r, 0), (-0.237*r, 0.237*r, 0), (-0.516*r, 0.511*r, 0), (-0.667*r, 0.278*r, 0), (-0.723*r, 0, 0), 
                            (-0.333*r, 0, 0), (-0.306*r, -0.129*r, 0), (-0.667*r, -0.274*r, 0), (-0.51*r, -0.51*r, 0), (-0.276*r, -0.666*r, 0), 
                            (-0.125*r, -0.307*r, 0), (0, -0.333*r, 0), (0, -0.722*r, 0), (0, -r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 
                            61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]
        self.cvPeriodic = True #closed
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, -0.97*r, 0), (0, -0.97*r, 0), (0.382*r, -0.921*r, 0), (0.707*r, -0.707*r, 0), (0.92*r, -0.381*r, 0),
                            (r, 0, 0), (0.92*r, 0.381*r, 0), (0.708*r, 0.708*r, 0), (0.385*r, 0.92*r, 0), (0, r, 0), 
                            (-0.385*r, 0.92*r, 0), (-0.708*r, 0.708*r, 0), (-0.92*r, 0.381*r, 0), (-r, 0, 0), (-0.92*r, -0.381*r, 0), 
                            (-0.707*r, -0.707*r, 0), (-0.382*r, -0.921*r, 0), (0, -0.97*r, 0), (0, -0.97*r, 0), (0, -0.707*r, 0), 
                            (0, -0.707*r, 0), (0.276*r, -0.666*r, 0), (0.51*r, -0.51*r, 0), (0.667*r, -0.274*r, 0), (0.723*r, 0, 0), 
                            (0.667*r, 0.278*r, 0), (0.516*r, 0.511*r, 0), (0.277*r, 0.666*r, 0), (0, 0.726*r, 0), (-0.277*r, 0.666*r, 0), 
                            (-0.516*r, 0.511*r, 0), (-0.667*r, 0.278*r, 0), (-0.723*r, 0, 0), (-0.667*r, -0.274*r, 0), (-0.51*r, -0.51*r, 0), 
                            (-0.276*r, -0.666*r, 0), (0, -0.707*r, 0), (0, -0.707*r, 0), (0, -0.333*r, 0), (0, -0.333*r, 0), 
                            (0.125*r, -0.307*r, 0), (0.236*r, -0.236*r, 0), (0.306*r, -0.129*r, 0), (0.333*r, 0, 0), (0.308*r, 0.127*r, 0), 
                            (0.237*r, 0.237*r, 0), (0.127*r, 0.308*r, 0), (0, 0.335*r, 0), (-0.127*r, 0.308*r, 0), (-0.237*r, 0.237*r, 0), 
                            (-0.308*r, 0.127*r, 0), (-0.333*r, 0, 0), (-0.306*r, -0.129*r, 0), (-0.236*r, -0.236*r, 0), (-0.125*r, -0.307*r, 0), 
                            (-0.125*r, -0.307*r, 0), (0, -0.333*r, 0), (0.125*r, -0.307*r, 0), (0.125*r, -0.307*r, 0), (0.276*r, -0.666*r, 0), 
                            (0.51*r, -0.51*r, 0), (0.667*r, -0.274*r, 0), (0.306*r, -0.129*r, 0), (0.333*r, 0, 0), (0.723*r, 0, 0), 
                            (0.667*r, 0.278*r, 0), (0.516*r, 0.511*r, 0), (0.237*r, 0.237*r, 0), (0.127*r, 0.308*r, 0), (0.277*r, 0.666*r, 0), 
                            (0, 0.726*r, 0), (-0.277*r, 0.666*r, 0), (-0.127*r, 0.308*r, 0), (-0.237*r, 0.237*r, 0), (-0.516*r, 0.511*r, 0), 
                            (-0.667*r, 0.278*r, 0), (-0.723*r, 0, 0), (-0.333*r, 0, 0), (-0.306*r, -0.129*r, 0), (-0.667*r, -0.274*r, 0), 
                            (-0.51*r, -0.51*r, 0), (-0.276*r, -0.666*r, 0), (-0.125*r, -0.307*r, 0), (-0.125*r, -0.307*r, 0), (0, -0.333*r, 0), 
                            (0, -0.333*r, 0), (0, -0.707*r, 0), (0, -0.97*r, 0), (0, -0.97*r, 0), (0.382*r, -0.921*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 
                            61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91]
        self.cvPeriodic = True #closed