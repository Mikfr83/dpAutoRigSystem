# importing libraries:
from ...Base import dpBaseCurve

# global variables to this module:    
CLASS_NAME = "Locator"
TITLE = "m115_locator"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_locator.png"

DP_LOCATOR_VERSION = 1.3


class Locator(dpBaseCurve.BaseCurve):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseCurve.BaseCurve.__init__(self, *args, **kwargs)
    
    
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
        self.cvPointList = [(0, 0, r), (0, 0, -r), (0, 0, 0), (r, 0, 0), (-r, 0, 0), 
                            (0, 0, 0), (0, r, 0), (0, -r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8]
        self.cvPeriodic = False #open
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(r, 0, 0), (r, 0, 0), (0.5*r, 0, 0), (0, 0, 0), (0, 0.5*r, 0), 
                            (0, r, 0), (0, r, 0), (0, 0.5*r, 0), (0, 0, 0), (-0.5*r, 0, 0),
                            (-r, 0, 0), (-r, 0, 0), (-0.5*r, 0, 0), (0, 0, 0), (0, -0.5*r, 0),
                            (0, -r, 0), (0, -r, 0), (0, -0.5*r, 0), (0, 0, 0), (0.5*r, 0, 0),
                            (r, 0, 0), (r, 0, 0), (0.5*r, 0, 0), (0, 0, 0), (0, 0, 0.5*r),
                            (0, 0, r), (0, 0, r), (0, 0, 0.5*r), (0, 0, 0), (-0.5*r, 0, 0), 
                            (-r, 0, 0), (-r, 0, 0), (-0.5*r, 0, 0), (0, 0, 0), (0, 0, -0.5*r),
                            (0, 0, -r), (0, 0, -r), (0, 0, -0.5*r), (0, 0, 0), (0.5*r, 0, 0),
                            (r, 0, 0), (r, 0, 0), (0.5*r, 0, 0), (0, 0, 0), (0, -0.5*r, 0),
                            (0, -r, 0), (0, -r, 0), (0, -0.5*r, 0), (0, 0, 0), (0, 0, 0.5*r), 
                            (0, 0, r), (0, 0, r), (0, 0, 0.5*r), (0, 0, 0), (0, 0.5*r, 0),
                            (0, r, 0), (0, r, 0), (0, 0.5*r, 0), (0, 0, 0), (0, 0, -0.5*r), 
                            (0, 0, -r), (0, 0, -r), (0, 0, -0.5*r), (0, 0, 0), (0, -0.5*r, 0),
                            (0, -r, 0), (0, -r, 0), (0, -0.5*r, 0), (0, 0, 0), (0.5*r, 0, 0),
                            (r, 0, 0), (r, 0, 0), (0.5*r, 0, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        self.cvPeriodic = True #closed