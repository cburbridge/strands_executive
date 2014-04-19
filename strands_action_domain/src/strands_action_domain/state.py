'''
SymobolicState.py
-----------------

Classes for storing comparing and parsing symbolic states.
Provides underlying funtionality to PythonDomainDef etc.

It parses states in the form (forall (?o) (above ?o mug)) (not (above mug tray))
supporting forall and negations. However, don't rely on it heavily as its grown
a little ugly.
'''

#TODO: This has grown and now needs to fully parse properly, no longer simple 
#pyparsing.

# 


from pyparsing import *
from predicates import *
import re

########################################################################
class Clause:
    '''
    Class for storing symbolic state clauses. They can be created by the
    createFromParse function or initialised by hand.
    
    self.constants is a list of constant names, like ['c1','c2'], defined in
    the predicate definition in SymbolicPredicates.py. self.c1 and self.c2 are
    then the values of those constants.
    
    self.predicateFunction is the PredicateType functor for the predicate.
    
    self.name is the predicate name.
    '''
    # Pyparsing syntax of a clause
    openbracket = Suppress(Literal('('))
    closebracket = Suppress(Literal(')'))
    identifier = Word(alphas, alphanums + "_-")
    parameter = Combine(Literal("?") + NotAny(" ") + identifier)("param")
    nomatch = NoMatch()
    syntax = openbracket + OneOrMore((identifier | parameter)) + closebracket
    negated_syntax =  openbracket + Suppress(Literal("not")) + OneOrMore(Group(syntax)) + closebracket
    #(forall (?k) (thisistrue ?k))
    forall_syntax = openbracket + Suppress(Literal("forall")) + \
        openbracket + parameter + closebracket + \
        (negated_syntax("negated") | Group(syntax))  + closebracket
    
    #----------------------------------------------------------------------
    def __init__(self, name, consts, negated=False, forall=False, parameterised=False):
        '''
        To create a clause, parse a name and a list of constants. eg::
        Clause('touching',['mug','table']). The name must exist in the
        SymbolicPredicates.py file and the correct number of constants must be
        given, or a PredicateError will be raised.
        '''
        if not Predicates.doesPredicateExist(name):
            raise ClauseError('CREATE_UNKNOWN', "unknown:%s (%s)"%(name,repr(consts)))

        self.constants = list()
        # Check if the right number of consts are given for this type of predicate
        self.predicateFunction = Predicates.getPredicate(name)
        predConsts = self.predicateFunction.predicate.consts
        if not len(predConsts) == len(consts):
            raise ClauseError("MISSING_CONST")
        
            
        for constant,value in zip(predConsts,consts):
            setattr(self,constant,value)
            self.constants.append(constant)
                
        self.number_constants = len(self.constants)
        self.name = name
        self.negated = negated
        self.forall = forall
        self.parameterised = parameterised

    #----------------------------------------------------------------------
    def addMember(self,member,value):
        #self.__dict__[member] = value
        setattr(self,member,value)
        
    #----------------------------------------------------------------------
    def setMember(self,member,value):
        setattr(self,member,value)
        
    #----------------------------------------------------------------------
    def getMember(self, member):
        #return self.__dict__[member]
        return getattr(self,member)
        
    #----------------------------------------------------------------------
    @staticmethod
    def createParseSyntax(name='null', consts=[]):
        '''
        create a pyparsing syntax for the clause specified.
        depricated.
        '''
        syntax = Clause.openbracket + (Literal(name))("name")
        for i in consts:
            syntax = syntax + Clause.identifier(i)
        syntax = syntax + Clause.closebracket
        return syntax
    
    #----------------------------------------------------------------------
    @staticmethod
    def createFromParse(item, start, stop):
        '''
        Create a Clause from a pyparsing parse, as aquired from Clause.syntax.
        item is a list of the form [name const const const..]. start is the
        start point in the parsed string, stop is the end in the parsed
        string.
        '''
        p = Clause(item[0],item[1:])
        p.start = start
        p.stop = stop
        return p
    
    @staticmethod
    def createCopy(other):
        consts = [getattr(other, v) for v in other.constants]
        p = Clause(other.name, consts, other.negated, other.forall, other.parameterised)
        return p
    
    #----------------------------------------------------------------------    
    def __str__(self):
        ## Short version
        #s = ''
        #if self.forall:
            #s += '(FORALL '
        #s += '('
        #if self.negated:
            #s += "-"
        #s += self.name #self.__dict__.keys().__str__()
        #for c in self.constants:
            #s  = s  +' '+ self.__dict__[c].__str__()
        #s=s+')'
        ## Long version
        ##s = "predicate"+ " : " + self.name #self.__dict__.keys().__str__()
        ##for c in self.constants:
            ##s  = s  +'\n  '+ c + " = " + self.__dict__[c].__str__()
        #if self.forall:
            #s += ')'
        #return s
        return self.__string__()
    
    #----------------------------------------------------------------------
    def __string__(self):
        """internal method to output as a sting that can be reparsed later."""
        s = ''
        if self.forall:
            s += '( forall (?ALL)'
        if self.negated:
            s += "( not "

        s += '('
        s += self.name #self.__dict__.keys().__str__()
        for c in self.constants:
            if self.__dict__[c].__str__() == '_ALL_':
                s  = s  +' ?ALL'
            else:
                s  = s  +' '+ self.__dict__[c].__str__()
        s=s+')'        
        
            
        if self.negated:
            s += ")"            
        if self.forall:
            s += ")"            
            
        return s
    
    #----------------------------------------------------------------------
    def shop_string(self):
        """Output clause in SHOP style. This function will be removed when
        this parser is tidied."""
        s = ''
        if self.forall:
            s += '( forall (?ALL) ()'
        if self.negated:
            s += "( not "

        s += '('
        s += self.name #self.__dict__.keys().__str__()
        for c in self.constants:
            if self.__dict__[c].__str__() == '_ALL_':
                s  = s  +' ?ALL'
            else:
                s  = s  +' '+ self.__dict__[c].__str__()
        s=s+')'        
        
            
        if self.negated:
            s += ")"            
        if self.forall:
            s += ")"            
            
        return s
        
            
        
    #----------------------------------------------------------------------
    def __eq__(self, other):
        '''
        Tests if this clause is equal to another using the == operator. It is
        equal if it has the same constants and the same name.
        '''
        if not self.name == other.name:
            return False
        for i in self.constants:
            if not self.getMember(i) == other.getMember(i):
                return False
        if not self.negated == other.negated:
            return False
        if not self.forall == other.forall:
            return False
        return True

########################################################################    
class ClauseError(Exception):
    '''
    Class for errors when create a clause.
    '''
    #----------------------------------------------------------------------
    def __init__(self, type, additional_info=None):
        self.types={}
        self.types["CREATE_UNKNOWN"]="Error creating a symbolic state clause, unknown predicate."
        self.types["MISSING_CONST"]="Error creating a symbolic state clause, wrong number of constants supplied."

        self.type = type
        self.additional_info=additional_info
        
    #----------------------------------------------------------------------
    def __str__(self):
        if self.additional_info:
            return '\n\n' + str(self.types[self.type] + '\n'+str(self.additional_info))
        else:
            return '\n\n' + repr(self.types[self.type] )#+ str(additional_info))

        
########################################################################
class SymbolicState:
    '''
    Class for storing the symbolic state. The state is stored as a list of
    *Clause* objects in self.state. It can be created manually, or from a
    string description that is parsed.
    '''
    #----------------------------------------------------------------------
    def __init__(self, state=None):
        ''' Create a SymbolicState from the list of Clause objects '''
        if state is None:
            self.state=[]
        else:
            self.state = state
            
    #----------------------------------------------------------------------
    def __str__(self):
        s="Number of statements = " + str(len(self.state))+'\n'
        for p in self.state:
            s=s+p.__str__()+'\n'
        return s
    
    #----------------------------------------------------------------------
    def __repr__(self):
        """"""
        s=""
        for p in self.state:
            s=s+p.__str__()+' '
        return s
    #----------------------------------------------------------------------
    def stateSize(self):
        ''' return the number of clauses in the state '''
        return len(self.state)
    
    #----------------------------------------------------------------------
    @staticmethod
    def createFromString(input):
        '''
        This function takes a string as input and returns a SymbolicState of
        the string. The input is of the form:
        
        (predicate const const)....
        
        If a predicate is parsed that is not specified in
        SymbolicPredicates.py then an exception is raised.
        '''
        newstate = SymbolicState()
        #syntax = Clause.nomatch
        #predicates = Predicates.getPredicates()
        
        #for predicate in predicates:
        #    syntax = syntax ^ Clause.createParseSyntax(predicate,predicates[predicate])
                
        #for item,s,e in Clause.syntax.scanString(input):
        #    print item[0], "(",")"
        #exit(0)
        # "forall" clauses
        input_remain = ""
        prevStop = 0
        for item,start,stop in Clause.forall_syntax.scanString(input):
            param = item.asList()[0]
            c = item.asList()[1]
            c = ["_ALL_" if const == param else const for const in c]
            predicate = Clause.createFromParse(c, start, stop)
            predicate.forall = True
            if item.asDict().has_key("negated"):
                predicate.negated = True
            try:
                newstate.addClause(predicate)
            except StateError:
                raise StateError("PARSE_DUP")
            
            input_remain += input[prevStop:start]
            prevStop = stop
        input_remain += input[prevStop:]
        input =  input_remain        

        # negated clauses
        prevStop = 0
        input_remain = ""
        for item,start,stop in Clause.negated_syntax.scanString(input):
            for c in item:
                predicate = Clause.createFromParse(c, start, stop)
                predicate.negated = True
                if c.asDict().has_key("param"):
                    predicate.parameterised = True                
                try:
                    newstate.addClause(predicate)
                except StateError:
                    raise StateError("PARSE_DUP")
            input_remain += input[prevStop:start]
            prevStop = stop
        input_remain += input[prevStop:]
        input =  input_remain
        # standard clauses
        begin = 0
        for item,start,stop in Clause.syntax.scanString(input):
            if start > begin:
                if len(input[begin:start].strip()):
                    raise StateError("PARSE_UNKNOWN", "Unknown: %s"%input[begin:start])
            begin = stop
            predicate = Clause.createFromParse(item, start, stop)
            if item.asDict().has_key("param"):
                predicate.parameterised = True                            
                
            try:
                newstate.addClause(predicate)
            except StateError:
                raise StateError("PARSE_DUP")
              
        if len(input) > begin:
                if len(input[begin:len(input)].strip()):
                    raise StateError("PARSE_UNKNOWN", "Unknown: %s"%input[begin:])
        
        return newstate
        
    #----------------------------------------------------------------------
    def hasClause(self, p):
        ''' Check if this state contains the clause p '''
        for i in self.state:
            if p==i:
                return True
        return False

    #----------------------------------------------------------------------
    def addClause(self, p):
        ''' Add the Clause p to this state, checking for duplicatation '''
        if self.hasClause(p):
            raise StateError("ADD")
        self.state.append(p)
    
    #----------------------------------------------------------------------
    def removeClause(self, p):
        ''' Remove the clause, exception if not found. '''
        if not self.hasClause(p):
            raise StateError("DEL")
        self.state.remove(p)
        
    #----------------------------------------------------------------------
    def findClauses(self, expression):
        """ Find clauses like  supplied
        :Parameters:
            string_rep : str
                string representation of clause to look for, incorporated RE
                eg "(above mug1_* tray)
        """
        ex = re.compile(expression)
        clauses = []
        for c in self.state:
            match =  ex.search(str(c))
            #print "Compare to : ["+str(c) + ']'
            if match:
                #print "MATCH ", c
                clauses.append(c)
        return clauses
            
    #----------------------------------------------------------------------
    def __xor__(self, other):
        ''' 
        The ^ operator for state intersection, return the clause commen to
        both this and the other
        '''
        newstate = SymbolicState()
        for i in self.state:
            if other.hasClause(i):
                newstate.addClause(i)
        
        return newstate
    
    #----------------------------------------------------------------------
    def __and__(self, other):
        '''
        The & operator for state combination, returns the combination of this
        state and the other state without the duplicated entries
        '''
        newstate = SymbolicState()
        for i in self.state:
            newstate.addClause(i)
        for i in other.state:
            if not newstate.hasClause(i):
                newstate.addClause(i)
        
        return newstate

    #----------------------------------------------------------------------
    def __sub__(self,other):
        '''
        Subtract: return a state that is this one minus what ever is in common
        with the other one
        '''
        common = self ^ other
        newstate = SymbolicState()
        for i in self.state:
            if not common.hasClause(i):
                newstate.addClause(i)
        return newstate
    
    #----------------------------------------------------------------------
    def __eq__(self, other):
        """same set of clauses, if paramed then same params"""
        assert isinstance(other, SymbolicState)
        if other.state == self.state:
            return True
        return False
        
    #----------------------------------------------------------------------
    def transitionListsTo(self, other):
        '''
        Return (A, D) where A is the add list to go from this state to 'other'
        and D is the corresponding delete list. Each list is supplied as a
        SymbolicState
        '''
        delete_list = self - other
        add_list = other - self
        return (add_list, delete_list)

    
    #----------------------------------------------------------------------
    def whatObjects(self):
        '''
        Return a set of what objects this state concerns - ie what objects
        appear in the constant list in this state
        '''
        objects = set([])
        predicates = Predicates.getPredicates()
        for p in self.state:
            for const in predicates[p.name]:
                if p.getMember(const)[0] != '?' and p.getMember(const) != '_ALL_':
                    objects.add(p.getMember(const))
        return objects

    #----------------------------------------------------------------------
    def whatParameters(self):
        """Return set of parameters involved in state"""
        objects = set([])
        predicates = Predicates.getPredicates()
        for p in self.state:
            for const in predicates[p.name]:
                if p.getMember(const)[0] == '?':
                    objects.add(p.getMember(const))
        return objects        
    
    #----------------------------------------------------------------------
    def groundParameters(self, params):
        """
        Alters the state, filling in the parameters with those supplied.
        :Parameters:
            params : dictionary
                the parameters that appear throughought state
        """
        allobjects = self.whatObjects()
        grounded = self.whatObjects()
        param = self.whatParameters()
        for i in param:
            if not params.has_key(i):
                raise StateError("PARAM", "Don't have value for "+str(i))
            
        for c in self.state:
            if c.parameterised:
                for const in c.constants:
                    if c.getMember(const).find("?") != -1:
                        try:
                            setattr(c, const, params[c.getMember(const)])
                        except KeyError:
                            raise StateError("PARAM")
                c.parameterised = False       
    #----------------------------------------------------------------------
    def expandForAlls(self, expand_as=None):
        """Expands all the forall statements"""
        if expand_as != None:
            grounded = expand_as
        else:
            grounded = self.whatObjects()
        
        expanded_foralls = []
        remove_foralls = []
        
        for c in self.state:
            isinstance(c, Clause)
            if c.forall:
                remove_foralls.append(c)
                # for all the symbols the state considers, create a clause copy replace __ALL__ with a
                for sym in grounded:
                    vals = [getattr(c, a) if getattr(c, a) != "_ALL_" else sym for a in c.constants]
                    cnew = Clause(c.name, vals)
                    cnew.negated = c.negated
                    cnew.parameterised = True
                    expanded_foralls.append(cnew)
        self.state.extend(expanded_foralls)
        #print "Expanding forall "
        #print remove_foralls
        for c in remove_foralls:
            self.state.remove(c)        

    #----------------------------------------------------------------------
    def parameterise(self, params):
        """
        :Parameters:
            params : dict of parameters
                object:paramstring
        """
        assert isinstance(params, dict )
        print params
        for c in self.state:
            for const in c.constants:
                if c.getMember(const) in params:
                    c.setMember(const, params[c.getMember(const)])
                    c.parameterised = True
        
    #----------------------------------------------------------------------
    def __getstate__(self):
        """Return a string representation"""
        s = ''
        for p in self.state:
            s=s+p.__string__()+' '
        return s
    
    #----------------------------------------------------------------------
    def __setstate__(self, s):
        """Set from string representation"""
        new = self.createFromString(s)
        self.__dict__ = new.__dict__
        
    #----------------------------------------------------------------------
    def __iter__(self):
        return iter(self.state)
        
    
########################################################################
class StateError(Exception):
    '''
    Class for state exceptions
    '''
    def __init__(self, type, additional_info=None):
        self.types={}
        self.types["ADD"]="Error adding to state, entry already exists."
        self.types["DEL"]="Error deleteing from state, entry doesn't exist."
        self.types["PARSE_DUP"]="Error parsing string into symbolic state, duplicate clause found."
        self.types["PARSE_UNKNOWN"]="Error parsing string into symbolic state, unknown syntax found."
        self.types["PARAM"]="No instantiation for parameter given, but trying to ground state!"

        self.type = type
        self.additional_info=additional_info
    def __str__(self):
        if self.additional_info:
            return '\n\n' + str(self.types[self.type] + '\n'+str(self.additional_info))
        else:
            return '\n\n' +repr(self.types[self.type] )#+ str(additional_info))

        
########################################################################
if __name__ == '__main__':
    string = "(belongs hand robot) (left-hand-empty) (touching mug1 table) (touching mug2 table) (next-to mug1 mug27) (above mug1 mug3) "
    s = SymbolicState.createFromString(string)
    print s.whatObjects()
    s.addClause(Clause('touching',['mug1','thesky']))
    s.addClause(Clause('left-hand-holding',['mug1']))
    print s
    t = SymbolicState.createFromString("(touching mug1 table) (left-hand-empty) (right-hand-empty)")
    print "union: " + str(s&t)
    #s.removeClause(t.state[1])
    a = s^t
    print "intersect: " + str(a)
    print s
    
    #s.removeClause(t.state[2])
    print "==ADD=="
    print s.transitionListsTo(t)[0]
    print "==DEL=="
    print s.transitionListsTo(t)[1]
    
    print "====== Geo->Sym function tests ========="
    # Test each clause in state S
    for clause in s.state:
        if clause.predicateFunction.predicate.evaluatable:
            clauseValues=list()
            for i in clause.constants:
                clauseValues.append(clause.getMember(i))
            #clause.predicateFunction(None,clauseValues)
            pass
    
    raw_input()
    tests = ["(not (touching ?alpha beta) (above farm tree)) (forall (?T) (not (touching ?T ?o))) (object table) (touching ?h table) (forall (?I) (touching ?I ?h))",
             "(object ?alpha) (touching ?alpha ?o) (forall (?K) (touching ?K table))" ]
    for teststr in tests:
        s =  SymbolicState.createFromString(teststr)
        print s
        #s.groundParameters({'?alpha': 'h','?o': 'ohoh', '?h': 'alphasooma'})
        s.expandForAlls()
        print s
    raw_input()

