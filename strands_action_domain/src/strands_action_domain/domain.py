"""
PythonDomainDef.py
------------------
Provides classes for storing domain definitions and problem definitions. The
"native" format of these definitions is as python pickled objects, not PDDL.
However, each provide methods for generating a PDDL representation.
"""
import copy
import predicates
import state
from action import Action, ActionError


########################################################################
class DomainDefinition(object):
    """
    A class for domain definitions learned from examples.
    To be created by ss_log_to_pdd.
    Much like PDDL domain definitions, added STRANDS stuff.
    """

    #----------------------------------------------------------------------
    def __init__(self, domain_name, comment=''):
        """Constructor"""
        # All domains are using these predicates for now..
        self.predicates = predicates.Predicates
        # Store names of actions in a list
        self.actions = []
        self.domain_name = domain_name
        self.commment = comment
        self.source_header = ""
        
    #----------------------------------------------------------------------
    def addAction(self, name, preconditions, add, delete, parameter_order):
        """ Adds an action to the domain as an Action object 
        :Parameters:
            preconditions, add, delete : SymbolicState
                state object listing preconditions, adds or deletes
        """
        if name.lower() in self.actions:
            raise DomainDefinition("DUPLICATEACTION")
        params = set([])
        params.update(preconditions.whatParameters())
        params.update(add.whatParameters())
        params.update(delete.whatParameters())
        diff = set(parameter_order).difference(params)
        diff.update(params.difference(set(parameter_order)))
        if len(diff) > 0:
            raise DomainDefinition("PARAMSORDER")
        self.actions.append(name.lower())
        setattr(self, name.lower(), Action(name.lower(), preconditions, add, delete, parameter_order))
        return self.getAction(name.lower())
    
    #----------------------------------------------------------------------
    def addExistingAction(self, action):
        """add the Action object"""
        if action.name.lower() in self.actions:
            raise DomainDefinition("DUPLICATEACTION")
        setattr(self, action.name.lower(), action)
        self.actions.append(action.name.lower())

    #----------------------------------------------------------------------
    def setActionSource(self, name, source):
        """Set the python snipet for the give action"""
        self.getAction(name).setSource(source)
    
    #----------------------------------------------------------------------
    def getAction(self, name):
        """Get the action object"""
        name = name.lower()
        if name not in self.actions:
            raise DomainDefinitionError("BADACTION", "("+str(name)+")")
        act = getattr(self, name)
        isinstance(act, Action)
        return act
        
    #----------------------------------------------------------------------
    def setDomainSourceHeader(self, source):
        """ Set the source header of this domain."""
        self.source_header = source
        
    #----------------------------------------------------------------------
    def __getstate__(self):
        """ 
        For pickling this class, predicates need attention
        """
        odict = self.__dict__.copy()
        odict['predicates'] = None
        return odict    
    
    #----------------------------------------------------------------------
    def __setstate__(self, state):
        """Unpickle"""
        self.__dict__.update(state)   # update attributes
        
        # Manage predicates
        self.predicates = predicates.Predicates
               
    #----------------------------------------------------------------------
    def saveToDisk(self, filename):
        """Save the domain to a file"""
        import pickle
        out = open(filename, "w")
        pickle.dump(self, out)
        out.close()

    #----------------------------------------------------------------------
    @staticmethod
    def createFromFile(filename):
        """Create an instance of this class from a pickled copy"""
        import pickle
        file_in = open(filename, "r")
        load = pickle.load(file_in)
        file_in.close()
        isinstance(load, DomainDefinition)
        return load
    
    #----------------------------------------------------------------------
    def __str__(self):
        retstr = 'DOMAIN: %s\n' % self.domain_name
        retstr += '; %s\n' % self.commment
        retstr += 'PREDICATES:\n'
        preds = self.predicates.getPredicates()
        for pred in preds:
            retstr += '    ( %s ' % pred
            for c in preds[pred]:
                retstr += '?%s ' % c
            retstr += ')\n'
        retstr += 'ACTIONS:\n'
        for act in self.actions:
            retstr += '    ( %s ' % act
            for c in self.getAction(act).parameter_types.keys():
                retstr += '?%s ' % c
            retstr += ')\n'
            retstr += "        PRECON:%s\n"%repr(self.getAction(act).preconditions)
            retstr += "        EFFECTS:%s\n"%repr(self.getAction(act).effects)
        return retstr
    
    #----------------------------------------------------------------------
    def generatePDDL(self):
        """Returns a PDDL string of the domain."""
        ident = '    '
        retstr = '; ' + self.commment + '\n'
        retstr += '(define (domain %s)\n' % self.domain_name
        retstr += ident + '(:requirements :strips :equality)\n'
        retstr += ident + '(:predicates\n'
        preds = self.predicates.getPredicates()
        for pred in preds:
            retstr += ident + ident + '(%s' % pred
            for c in preds[pred]:
                retstr += ' ?%s' % c
            retstr += ')\n'
        retstr += ident + ')\n'
        for act in self.actions:
            retstr +=  ident + '(:action %s :parameters ( ' % act
            for c in self.getAction(act).parameters:
                retstr += '%s ' % c
            retstr += ')\n'
            retstr += ident + ident + ':precondition (and\n'
            for c in self.getAction(act).preconditions.state:
                retstr += ident + ident + ident + str(c) + '\n'
            if len(self.getAction(act).parameters) > 1:
                retstr += ident + ident + ident + "(not (= %s %s))\n" % (self.getAction(act).parameters[0], self.getAction(act).parameters[1])
            retstr += ident + ident + ')\n'
           
            retstr += ident + ident + ':effect (and\n'
            for c in self.getAction(act).add_list.state:
                retstr += ident + ident + ident + str(c) + '\n'
            for c in self.getAction(act).delete_list.state:
                c.negated = not c.negated  #delete list is not default negated...
                retstr += ident + ident + ident +  str(c) + '\n'
                c.negated = not c.negated
                    
            retstr += ident + ident + ')\n'              
            
            retstr += ident + ')\n'
        retstr += ')'
        return retstr
    
    #----------------------------------------------------------------------
    def generateSHOP(self):
        """Generate the shop domain data."""
        ident = '    '
        retstr = '; ' + self.commment + '\n'
        retstr += '(defdomain %s\n' % self.domain_name
        for act in self.actions:
            retstr +=  ident + '(:operator ( !%s   ' % act
            for c in self.getAction(act).parameters:
                retstr += '%s ' % c
            retstr += ')\n'
            retstr += ident + ident + '(and\n'  # precond
            for c in self.getAction(act).preconditions.state:
                retstr += ident + ident + ident + c.shop_string() + '\n'
            if len(self.getAction(act).parameters) > 1:
                retstr += ident + ident + ident + "(not (= %s %s))\n" % (self.getAction(act).parameters[0], self.getAction(act).parameters[1])
            retstr += ident + ident + ')\n'
           
            retstr += ident + ident + '( \n'  # delete list
            for c in self.getAction(act).delete_list.state:
                retstr += ident + ident + ident +  c.shop_string() + '\n'
            retstr += ident + ident + ') \n'
            retstr += ident + ident + '( \n'  # add list
            for c in self.getAction(act).add_list.state:
                retstr += ident + ident + ident + c.shop_string() + '\n'
                    
            retstr += ident + ident + ')\n'              
            
            retstr += ident + ')\n'
        retstr += ')'
        return retstr
    
        
########################################################################
class DomainDefinitionError(Exception):
    '''
    Class for definition exceptions
    '''
    def __init__(self, type, additional_info=None):
        self.types={}
        self.types["PARAMSORDER"]="Error creating action, parameters are not all listed or too many."
        self.types["DUPLICATEACTION"]="Error creating action, existing action by same name already."
        self.types["BADACTION"]="Trying to get an action that doesnt exist."

        self.type = type
        self.additional_info=additional_info
    def __str__(self):
        if self.additional_info:
            return '\n\n' + str(self.types[self.type] + '\n'+str(self.additional_info))
        else:
            return '\n\n' +repr(self.types[self.type] )#+ str(additional_info))

    
    

    
########################################################################
class ProblemDefinition(object):
    """Definition of problems for plan solving."""

    #----------------------------------------------------------------------
    def __init__(self, problem_name, domain, initial_state=None):
        """Constructor
        :Parameters:
            domain : DomainDefinition
                the domain to work inside
            problem_name : string
                arbritatry name of problem
            initial_state : SymbolicState
                initial state, should not contain parameterised clauses
        """
        self.problem_name = problem_name
        self.domain = domain
        if initial_state:
            self.setInitialState(initial_state)
        
        self.exclude_goals = []
        
    #----------------------------------------------------------------------
    def setInitialState(self, initial_state):
        for i in initial_state.state:
            if i.parameterised:
                raise ProblemDefinitionError("PARAMINITIAL")
        self.initial_state = initial_state
        isinstance(self.initial_state, state.SymbolicState)
        
    #----------------------------------------------------------------------
    def setGoal(self, goal_state, back_track_negateds=None):
        """
        :Parameters:
            back_track_negateds : a list of solution states that need to be excluded as solutions
        """
        #TODO: may need to adapt SymbolicState so that when a forall ocurs, but 
        # is not paramaterised, parameterised is not set...
        for i in goal_state.state:
            if i.parameterised:
                raise ProblemDefinitionError("PARAMGOAL")
        self.goal_state = goal_state
        if back_track_negateds is not None:
            self.exclude_goals = back_track_negateds
        isinstance(self.goal_state, state.SymbolicState)
        isinstance(self.exclude_goals, state.SymbolicState)
        
    #----------------------------------------------------------------------
    def addExcludedGoalState(self, exclude):
        isinstance(exclude, state.SymbolicState)
        self.exclude_goals.append(exclude)
    
    #----------------------------------------------------------------------
    def generatePDDL(self):
        """Generate PDDL of problem. Return as string."""
        retstr = '(define (problem %s) (:domain %s)\n' % (self.problem_name, self.domain.domain_name)
        obs = self.initial_state.whatObjects()
        retstr += '  (:objects'
        for objectname in obs:
            retstr += ' ' + objectname
        retstr += '  )\n'
        retstr += '  (:init\n'
        retstr += repr(self.initial_state)
        retstr += '  )\n'
        retstr += '  (:goal (and\n'
        retstr += repr(self.goal_state)
        for i in self.exclude_goals:
            retstr += '    (not (and\n'
            retstr += repr(i)
            retstr += '    ))\n'
        retstr += '    )\n'
        retstr += '  )\n'
        retstr += ')'
        return retstr
        

########################################################################
class ProblemDefinitionError(Exception):
    '''
    Class for definition exceptions
    '''
    def __init__(self, type, additional_info=None):
        self.types={}
        self.types["PARAMINITIAL"]="Initial state in a problem can not be paramaterised."
        self.types["PARAMGOAL"]="Goal in a problem can not be paramaterised."

        self.type = type
        self.additional_info=additional_info
    def __str__(self):
        if self.additional_info:
            return '\n\n' + str(self.types[self.type] + '\n'+str(self.additional_info))
        else:
            return '\n\n' +repr(self.types[self.type] )

