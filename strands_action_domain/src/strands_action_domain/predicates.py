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
