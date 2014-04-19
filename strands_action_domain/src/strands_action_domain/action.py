import yaml
import predicates
import state

from strands_executive_msgs import task_utils
from strands_executive_msgs.msg import Task

########################################################################
class Action(object):
    """
    An action in the domain. Stores the effect on the state, what the
    preconditions of exectution are, action server etc. Loads yaml files.
    """
    #----------------------------------------------------------------------
    def __init__(self, name, action_server,
                 preconditions, effects, 
                 action_parameters=None, 
                 parameter_types=None):
        """
        :Parameters:
            preconditions, add, delete : SymbolicState
                state object listing preconditions, adds or deletes            
            action_parameters : list
                list of parameters taken
        """
        self.name = name
        self.action_server = action_server
        self.preconditions = preconditions
        self.effects = effects
        if action_parameters == None:
            self.action_parameters = {}
        else:
            self.action_parameters = action_parameters
        if parameter_types == None:
            self.parameter_types = {}
        else:
            self.parameter_types = parameter_types
            
    
    #----------------------------------------------------------------------
    def createCopy(self):
        return copy.deepcopy(self)
        
    #----------------------------------------------------------------------
    def checkApplicable(self, symbolicstate, parameters, return_diff=False):
        """Test the preconditions hold with given parameters
        
        :Parameters:
            symbolicstate : SymbolicState
                state to test against
            parameters : dict
                dict of parameter strings
            return_diff : bool
                should return the preconditons diff? default no, if true returns
                a tuple (False|True,diff)
        """
        ground_precond = copy.deepcopy(self.preconditions)
        ground_precond.groundParameters(parameters)
        diff =  state.SymbolicState()
        for c in ground_precond.state:
            if c.negated:
                cc = copy.deepcopy(c)
                cc.negated = False
                if symbolicstate.hasClause(cc):
                    cc.negated = True
                    diff.addClause(cc)
            else:
                if not symbolicstate.hasClause(c):
                    diff.addClause(copy.deepcopy(c))
        #diff = ground_precond - symbolicstate
        if len(diff.state) != 0: #len(ground_precond.state):
            if return_diff:
                return (False, diff)
            else:
                return False
        else:
            if return_diff:
                return (True, diff)
            else:
                return True
    
    #----------------------------------------------------------------------
    def applyToState(self, symbolicstate, parameters, check_conditions=True, object_list=None):
        """Applies the action to a symbolic state. Return new state
        
        :Parameters:
            symbolicstate : SymbolicState, not altered
                state to apply against
            parameters : dict
                dict of parameter strings
        """
        if check_conditions and not self.checkApplicable(symbolicstate, parameters):
            raise ActionError("NOTAPLIC", "%s not applicable"%self.name)
        ground_add = copy.deepcopy(self.add_list)
        ground_del = copy.deepcopy(self.delete_list)
        ground_add.groundParameters(parameters)
        ground_add.expandForAlls(object_list)
        ground_del.groundParameters(parameters)
        ground_del.expandForAlls(object_list)
        symbolicstate = symbolicstate - ground_del
        #print "GROUND DELETEE:"
        #print ground_del
        symbolicstate = symbolicstate & ground_add
        #print "apply to state:"
        #print "Add:", ground_add
        #print "Del:", ground_del
        return symbolicstate
        
    #----------------------------------------------------------------------
    def __str__(self):
        s = ""
        s += "Action: " + self.name + "\n"
        s += "Params: " +  str(self.parameters)
        return s
    
    #----------------------------------------------------------------------
    def __eq__(self, other):
        """are these two action the same in that they have same precond and same
        add and delete lists. Equal in all but source code."""
        assert isinstance(other, Action)
        if (self.preconditions == other.preconditions and
            self.effects == other.effects):
            return True
        
    
        return False
        
    @classmethod
    def load_yaml(cls, yml):
        data = yaml.load(yml)
        name = data['ActionName']
        act_server = data['ActionServer']
        if data.has_key("Preconditions"):
            precond = state.SymbolicState.createFromString(data['Preconditions'])
        else:
            precond = state.SymbolicState()
        if data.has_key("Effects"):
            effects = state.SymbolicState.createFromString(data['Effects'])
        else:
            effects = state.SymbolicState()
        if data.has_key("ActionServerParameters"):
            act_server_params = data['ActionServerParameters']
        else:
            act_server_params = None
            
        if data.has_key("ParameterTypes"):
            param_types = data['ParameterTypes']
        else:
            param_types = None
                  
        act = cls(name, act_server, precond, effects, act_server_params,
                  param_types)
        return act
        
    def create_executive_task(self,  parameters):
        task = Task(node_id='', action=self.action_server)
        for arg, value in self.action_parameters.items():
            if parameters.has_key(value): # fill in parameter
                value = parameters[value]
            task_utils.add_argument(arg, value) # this requires the change discussed on gitter
        return task
        
        
########################################################################
class ActionError(Exception):
    '''
    Class for definition exceptions
    '''
    def __init__(self, type, additional_info=None):
        self.types={}
        self.types["NOTAPLIC"]="Error applying action, preconditions not met."

        self.type = type
        self.additional_info=additional_info
    def __str__(self):
        if self.additional_info:
            return '\n\n' + str(self.types[self.type] + '\n'+str(self.additional_info))
        else:
            return '\n\n' +repr(self.types[self.type] )