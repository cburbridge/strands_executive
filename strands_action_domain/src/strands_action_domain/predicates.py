'''
SymbolicPredicate.py
--------------------

This file provides the *Predicates* class which stores what predicates exist,
and how to evaluate them on a given *GeometricState*. Predicates are created
by defining a function::

  @Predicate(number_constants,evaluatable)
  def have_arm(geometric_state, c):
     return True if predicate is true on state

The decorator allows the predicates to be found so that no list needs to be
maintained.

When the predicates are called, if evaluatable is False then a PredicateError
will be raised

Constant Symbols
Objects: 		On = > n an integer
Categories: 	Cn => n an integer

Predicates:
( type On Cn )
( 'belongs' On Om ) where 'belongs' is a component relationship see p. 6 Spec of Action Language

'''
import numpy as np
import math

# These two classes provide the @Predicate decorator that turns a funtion into
# an idenfiable predicate. The decorator takes as an argument the number of 
# constant symbols that that predicate takes.

class PredicateType(object):
    '''
    This class is esentially what each predicate function in the *Predicates*
    class will be converted into.
    '''
    def __init__(self, predicate, f):
        self.f=f
        self.predicate=predicate
    def __call__(self, *args):
        if self.predicate.evaluatable:
            return self.f(*args)
        else:
            raise PredicateError("EVAL_NO_EVAL")

class Predicate(object):
    def __init__(self,  arg_count, evaluatable=True, colour=(1,0,0), singular=False):
        self.consts = []
        self.evaluatable = evaluatable
        self.arg_count = arg_count
        self.colour = colour    # for displaying in rave...
        self.singular = singular  # If this predicate can only apply once in a state
        for i in range(1,arg_count+1):
            self.consts.append('c'+repr(i))

    def __call__(self, f):
        return PredicateType(self, f)


########################################################################
class Predicates(object):
    #----------------------------------------------------------------------
    def __init__(self):
        '''
        This class never needs to be instantiated!
        '''
        print "Hello. Don't do it."
        pass
    
    #----------------------------------------------------------------------
    @staticmethod
    def getPredicates(seperate=False):
        '''
        Returns a dictionarry of predicates, where the predicate name is the
        key and the definition is a list of constants. If seperate is True,
        then two dictionaries in a list are returned, the first being the
        predicates that can not be evaluated, and the second being all the
        others.
        '''
        predicates={}
        predicates_noeval={}
        for method in dir(Predicates):
            if isinstance(getattr(Predicates,method), PredicateType):
                pred = getattr(Predicates,method).predicate
                if pred.evaluatable:
                    predicates[method.replace('_','-')]=pred.consts
                else:
                    predicates_noeval[method.replace('_','-')]=pred.consts

            
        #print predicates
        if seperate:
            return [predicates_noeval, predicates]
        else:
            return dict(predicates_noeval.items() + predicates.items())

    #----------------------------------------------------------------------        
    @staticmethod
    def getPredicate(predicateName, use_learned_when_available=True):
        '''
        Returns the predicate method given the predicate name. The returned
        predicate will be a functor of type *PredicateType*.
        '''
        pred = getattr(Predicates,predicateName.replace('-','_'))
        #if not isinstance(pred, PredicateType):
            #raise PredicateError
        return pred

    #----------------------------------------------------------------------
    @staticmethod
    def doesPredicateExist(predicateName):
        '''
        Returns True if the predicate exists, otherwise False.
        Uses getPredicates to get a list of all predicates and then 
        looks for the argument in that list.
        '''
        predicates = Predicates.getPredicates()
        return predicates.has_key(predicateName)

    #----------------------------------------------------------------------
    #   All predicate below....
    #----------------------------------------------------------------------
    @Predicate(2,colour=(1,0,0), evaluatable=False)
    def touching(geometric_state, c):
        '''
        Is c[0] touching c[1]. 
        Ie, do the bounding boxes intersect?
        TODO: Maybe consider padding bounding boxes a little so to 
        increase chance of predicate
        '''
        #b1=geometric_state.getObjectBox(c[0])
        #b2=geometric_state.getObjectBox(c[1])
        #if b1^b2:
            #return True
        #else:
            #return False
        return geometric_state.checkCollision(c[0],c[1])

    #----------------------------------------------------------------------    
    @Predicate(2,colour=(1,1,0), evaluatable=False)
    def tipping(geometric_state, c):
        '''
        Is c[0] tipping into c[1]....
        So, is the top of c[0] above c[1] and is c[0] angled sufficiently...
        '''
        b1=geometric_state.getObjectBox(c[0])
        b2=geometric_state.getObjectBox(c[1])
        c2TopMinX = np.min(b2.points[0,4:])
        c2TopMinY = np.min(b2.points[1,4:])
        c2TopMaxX = np.max(b2.points[0,4:])
        c2TopMaxY = np.max(b2.points[1,4:])
        c1TopCentre = b1.getTopCentre()
        c2TopCentre = b2.getTopCentre()
        c1BotCentre = b1.getBottomCentre()
        
        # If the centre of the tipping item is not above the top of the
        # receiving item then no
        if (c1TopCentre[0] > c2TopMaxX or c1TopCentre[0] < c2TopMinX or
            c1TopCentre[1] > c2TopMaxY or c1TopCentre[1] < c2TopMinY or
            c1TopCentre[2] < c2TopCentre[2] ):
            return False

        # If the angle that c1 is at is not 'horizontal' enough then no.
        # Horizontal enough is defined as at >90^o -> just past horizontal
        c1Direction = c1TopCentre - c1BotCentre
        c1Direction = c1Direction / np.dot(c1Direction,c1Direction)
        cosTh = np.dot(c1Direction,[0,0,1])
        #th=np.arccos(cosTh)
        if ( cosTh > 0) :
            return False
        
        return True
    
    #----------------------------------------------------------------------
    @Predicate(1, evaluatable=True, colour=(1, 1, 0))
    def upside_down(geometric_state, c):
        """Is the object fully upside-down?"""
        b1=geometric_state.getObjectBox(c[0])
        c1TopCentre = b1.getTopCentre()
        c1BotCentre = b1.getBottomCentre()
        

        # If the angle that c1 is at is not 'horizontal' enough then no.
        # Horizontal enough is defined as at >90^o -> just past horizontal
        c1Direction = c1TopCentre - c1BotCentre
        c1Direction = c1Direction / np.dot(c1Direction,c1Direction)
        cosTh = np.dot(c1Direction,[0,0,1])
        th=np.arccos(cosTh)
        if c1TopCentre[2] < c1BotCentre[2]:
            return True
        
        return False

    #----------------------------------------------------------------------
    @Predicate(2,evaluatable=False,colour=(0,1,0))
    def next_to(geometric_state, c):
        '''
        (next-to A B) is a little vague, but I define it as there being less
        than 1/2 object B width between A and B for B to be classified as
        'next to' A Only considered in x,y direction, z ignored...
        '''
        b1=geometric_state.getObjectBox(c[0])
        b2=geometric_state.getObjectBox(c[1])
        mean1=b1.getMeanPosition()
        mean2=b2.getMeanPosition()
        between=mean2-mean1
        
        (AxMin,AyMin,AzMin)=b1.getMinPosition()
        (BxMin,ByMin,BzMin)=b2.getMinPosition()
        (AxMax,AyMax,AzMax)=b1.getMaxPosition()
        (BxMax,ByMax,BzMax)=b2.getMaxPosition()
        
        distance_between =np.sqrt( np.dot(between[0:2],between[0:2]) )
        a_size=np.sqrt((AxMin-AxMax)*(AxMin-AxMax) + (AyMin-AyMax)*(AyMin-AyMax))
        b_size=np.sqrt((BxMin-BxMax)*(BxMin-BxMax) + (ByMin-ByMax)*(ByMin-ByMax))
        #if c[0].find('cube')>-1 and c[1].find('cube')>-1:
            #print "between",repr(c),"=",distance_between
            #print "a_size=",a_size,"b_size=",b_size
            #print "eval_dist=",( distance_between - a_size/2.0 -b_size/2.0 )
            #print '( ',AzMin,' < ',BzMax,' and ',AzMax,' > ',BzMin,')'
        
        # Object heights
        a_h = AzMax - AzMin
        b_h = BzMax - BzMin
        
        # If the objects are not at least a bit in the some z plane then they
        # are not next to eachother. 80% of the smaller object should be in the
        # larger object z plane
        overlap = min(AzMax,BzMax)-max(AzMin,BzMin)
        #if c[0].find('blue')>-1 :
            #print "overlap=",overlap
        if overlap < 0.8*min(a_h,b_h):
            return False
        
        if not ( AzMin < BzMax and AzMax > BzMin): # not any z overlap
            return False
        if ( distance_between - a_size/2.0 -b_size/2.0 ) < 0.5*b_size:
            return True
        else:
            return False

    #----------------------------------------------------------------------    
    @Predicate(2,colour=(0,1,1))
    def above(geometric_state, c):
        '''
        Is the centre of c[0] above the bounding box of c[1]
        ''' 
        #b1=geometric_state.getObjectBox(c[0])
        #b2=geometric_state.getObjectBox(c[1])
        #a_mean=b1.getMeanPosition()
        #b_mean=b2.getMeanPosition()
        
        #(BxMin,ByMin,BzMin)=b2.getMinPosition()
        #(BxMax,ByMax,BzMax)=b2.getMaxPosition()
        #(AxMin,AyMin,AzMin)=b1.getMinPosition()
        #(AxMax,AyMax,AzMax)=b1.getMaxPosition()
        ## Object heights
        #a_h = AzMax - AzMin
        #b_h = BzMax - BzMin
        
        #if (a_mean[0] < BxMin or a_mean[0]>BxMax or 
            #a_mean[1] < ByMin or a_mean[1] > ByMax):
            #return False
        
        ## If it is touching, is it still above? first says no, second says ok
        ##if a_mean[2] - b_mean[2] < (a_h/2.0 + b_h/2.0):
            ##return False
        #if a_mean[2] < b_mean[2]+b_h/2.0:
            #return False
        #return True
        return geometric_state.checkAbove(c[0],c[1])
    
    #----------------------------------------------------------------------
    @Predicate(2,evaluatable=False, colour=(1,0,1))
    def inside(geometric_state, c):
        '''
        Is object c[0] inside object c[1]?
        '''
        # ie. is the box of c0 completely inside c[1]
        b1=geometric_state.getObjectBox(c[0])
        b2=geometric_state.getObjectBox(c[1])
        
        (BxMin,ByMin,BzMin)=b2.getMinPosition()
        (BxMax,ByMax,BzMax)=b2.getMaxPosition()
        (AxMin,AyMin,AzMin)=b1.getMinPosition()
        (AxMax,AyMax,AzMax)=b1.getMaxPosition()
        if (AxMax > BxMax or AxMin < BxMin or AyMax > ByMax or AyMin < ByMin  or
            AzMax > BzMax or AzMin < BzMin):
            return False
        return True

    #----------------------------------------------------------------------
    @Predicate(1, singular=True)
    def right_hand_holding(geometric_state, c):
        return geometric_state.checkHolding(c[0], "rightArm")

    #----------------------------------------------------------------------
    @Predicate(1, singular=True)
    def left_hand_holding(geometric_state, c):
        return geometric_state.checkHolding(c[0], "leftArm")

    #----------------------------------------------------------------------
    @Predicate(1)
    def left_hand_reachable(geometric_state, c):
        b1=geometric_state.getObjectBox(c[0])
        mean1=b1.getMeanPosition()
        if mean1[1]>-0.1:
            return True

        return False

    #----------------------------------------------------------------------    
    @Predicate(1)
    def right_hand_reachable(geometric_state, c):
        b1=geometric_state.getObjectBox(c[0])
        mean1=b1.getMeanPosition()
        if mean1[1]<0.1:
            return True
        return False

    #----------------------------------------------------------------------
    @Predicate(1, singular=True)
    def right_can_grasp(geometric_state, c):
        # When the object is between fingers, but the hand is empty
        # this should ultimately be provided by the grasp planning work...
        if not Predicates.right_hand_empty(geometric_state, []):
            return False
        return geometric_state.checkObjectBetweenFingers(c[0], "right")

    #----------------------------------------------------------------------
    @Predicate(1, singular=True)
    def left_can_grasp(geometric_state, c):
        # When the object is between fingers, but the hand is empty
        # this should ultimately be provided by the grasp planning work...
        if not Predicates.left_hand_empty(geometric_state, []):
            return False
        return geometric_state.checkObjectBetweenFingers(c[0], "left")

    #----------------------------------------------------------------------
    @Predicate(1)
    def object(geometric_state, c):
        if not Predicates.category(geometric_state, c):
            return True
        else:
            return False

    #----------------------------------------------------------------------
    @Predicate(1)
    def grasp(geometric_state, c):
        return False

    #----------------------------------------------------------------------
    @Predicate(1)
    def category(geometric_state, c):
        if c[0] in ['mug1-category', 'leather_tray-category','mug2-category','mug3-category','mug4-category',
                    "carafe-category", "cube-category", "sugar-category"]: #  ["mug-category", "tray-category", , "jar-category"]:
            return True
        return False
        
    #----------------------------------------------------------------------
    @Predicate(0)
    def right_hand_empty(geometric_state,c):
        #TODO: This could be more efficient by moving into rave_worker
        for obj in geometric_state.getObjectNames():
            if Predicates.right_hand_holding(geometric_state, [obj]):
                return False
        return True

    #----------------------------------------------------------------------
    @Predicate(0)
    def left_hand_empty(geometric_state,c):
        #TODO: This could be more efficient by moving into rave_worker
        for obj in geometric_state.getObjectNames():
            if Predicates.left_hand_holding(geometric_state, [obj]):
                return False
        return True

    @Predicate(0)
    def left_arm_home(geometric_state,c):
        return geometric_state.checkLeftHome() 

    @Predicate(0)
    def right_arm_home(geometric_state,c):
        return geometric_state.checkRightHome() 
    
    #----------------------------------------------------------------------
    @Predicate(2,evaluatable=False)
    def belongs(geometric_state, c):
        pass
    
    #----------------------------------------------------------------------
    @Predicate(2)
    def type(geometric_state, c):
        p = c[1].find("-category")
        #print "type", c[0], c[1]
        if p == -1:
            return False
        
        s = c[1][:p]
        #print s
        if c[0].find(s) != -1:
            return True
        else:
            return False
        
    @Predicate(1, evaluatable=False)
    def running(geometric_state, c):
        pass
    
    
########################################################################
class PredicateError(Exception):
    '''
    Class for predicate exceptions....
    '''
    def __init__(self, type, additional_info=None):
        self.types={}
        self.types["EVAL_NO_EVAL"] = "Error - attempting to evaluate non evaluatable predicate"

        self.type = type
        self.additional_info=additional_info
    def __str__(self):
        if self.additional_info:
            return str(self.types[self.type] + '\n\n'+str(self.additional_info))
        else:
            return repr(self.types[self.type] )

        
########################################################################
########################################################################
if __name__=='__main__':
    print "Predicates tests..."
    print Predicates.getPredicates()
