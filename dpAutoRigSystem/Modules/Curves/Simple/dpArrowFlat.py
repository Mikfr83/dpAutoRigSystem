# importing libraries:
from ...Base import dpBaseCurve

# global variables to this module:    
CLASS_NAME = "ArrowFlat"
TITLE = "m112_arrowFlat"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_arrowFlat.png"

DP_ARROWFLAT_VERSION = 1.3


class ArrowFlat(dpBaseCurve.BaseCurve):
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
        self.cvPointList = [(0, 0, 0), (-0.5*r, 0.4*r, 0), (-0.25*r, 0.4*r, 0), (-0.25*r, r, 0), (0.25*r, r, 0), 
                            (0.25*r, 0.4*r, 0), (0.5*r, 0.4*r, 0), (0, 0, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8]
        self.cvPeriodic = True #closed
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, 0, 0), (-0.125*r, 0.1*r, 0), (-0.25*r, 0.2*r, 0), (-0.5*r, 0.4*r, 0), (-0.465471500274*r, 0.4*r, 0),
                            (-0.298095832074*r, 0.4*r, 0), (-0.25*r, 0.4*r, 0), (-0.25*r, 0.45507734556*r, 0), (-0.25*r, 0.94955051446*r, 0), (-0.25*r, r, 0),
                            (-0.194052638657*r, r, 0), (0.219315978634*r, r, 0), (0.25*r, r, 0), (0.25*r, 0.94955051446*r, 0), (0.25*r, 0.45507734556*r, 0),
                            (0.25*r, 0.4*r, 0), (0.298095832074*r, 0.4*r, 0), (0.465471500274*r, 0.4*r, 0), (0.5*r, 0.4*r, 0), (0.25*r, 0.2*r, 0),
                            (0.125*r, 0.1*r, 0), (0, 0, 0), (-0.125*r, 0.1*r, 0), (-0.25*r, 0.2*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        self.cvPeriodic = True #closed