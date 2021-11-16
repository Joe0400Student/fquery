

from functools import reduce

class UnresolvableVariable(Exception):
    pass

class Value:
    
    def __init__(self, value, environ: dict):
        self.value, self.environ = value, environ
    
    def step(self,local_environment: dict):
        #print("step in value")
        return self
    def pr(self):
        return f"{self.value}"
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environ[k] = kwargs[k]



class Operator:
    
    def __init__(self, oper, arg1, arg2, environ={}):
        self.oper = oper
        self.arg1, self.arg2 = arg1, arg2
        self.environ = environ
    
    def step(self, local_environment: dict):
        #print("step in operator")
        temp_local = local_environment
        for k in self.environ:
            e = self.environ[k]
            temp_local[k] = e
        if(not isinstance(self.arg1, Value)):
            return Operator(self.oper, self.arg1.step(temp_local), self.arg2, self.environ)
        if(not isinstance(self.arg2, Value)):
            return Operator(self.oper, self.arg1, self.arg2.step(temp_local), self.environ)
        return Value(self.oper(self.arg1.value,self.arg2.value),self.environ)
    def pr(self):
        return f"{self.arg1.pr()} operator {self.arg2.pr()}"
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environ[k] = kwargs[k]
        self.arg1.update_all_variables(kwargs)
        self.arg2.update_all_variables(kwargs)

class Variable:
    def __init__(self, name: str, environment: dict):
        self.environment = environment
        if(name in environment):
            self.name = environment[self.name]
            self.resolved = True
        else:
            self.name = name
            self.resolved = False
    def step(self, local_environment):
        for k in self.environment:
            local_environment[k] = self.environment[k]
        if(self.resolved):
            return self.name
        else:
            if self.name in local_environment:
                temp = local_environment[self.name]
                temp.update_all_variables(self.environment)
                return temp
            else:
                raise UnresolvableVariable()
    def pr(self):
        return self.name
    def update_all_variables(self,diction):
        for k in diction:
            self.environment[k] = diction[k]
    
class Apply:
    def __init__(self, name: str, assigned, program, environment: dict):
        self.name, self.program = name, program
        self.environment = environment
        self.name = name
        self.assigned = assigned
        #print(self.assigned.pr())
    
    def step(self, local_environment: dict):
        #rint("step in apply")
        temp_env = local_environment
        for k in self.environment:
            temp_env[k] = self.environment[k]
        if(not isinstance(self.assigned, Value)):
            #self.assigned = self.assigned.step(temp_env)
            return Apply(self.name, self.assigned.step(temp_env), self.program, self.environment)
        self.program.update_all_variables({self.name:self.assigned})
        return self.program
    
    def pr(self):
        return f"Apply {self.name}={self.assigned.pr()} on {self.program.pr()}"
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.assigned.update_all_variables(kwargs)
        self.program.update_all_variables(kwargs)

class If_Else:
    
    def __init__(self, conditional, yes, no, environment: dict):
        self.conditional, self.yes, self.no, self.environment = conditional, yes, no, environment
    
    def step(self, local_environment: dict):
        
        #print("step in if_else")
        updated_local_env = local_environment
        for k in self.environment:
            updated_local_env[k] = self.environment[k]
        if(isinstance(self.conditional, Value)):
            return self.yes if self.conditional.value else self.no
        else:
            return If_Else(self.conditional.step(updated_local_env),self.yes,self.no,self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.conditional.update_all_variables(kwargs)
        self.yes.update_all_variables(kwargs)
        self.no.update_all_variables(kwargs)
        
        
    def pr(self):
        return f"if {self.conditional.pr()} then {self.yes.pr()} else {self.no.pr()}"
class QuitException(Exception):
    pass

class List(Value):
    def __init__(self, value=[], environment: dict):
        self.value = value
        self.environment = environment
    def push

def execute(program, environment: dict) -> Value:
    while(not isinstance(program, Value)):
        #print("stepping")
        #print(environment['A'].value)
        program = program.step(environment)
        #print(program.pr())
        #input()
    return program



def main() -> None:
    print("Starting the fquery interpreter")
    environment = {"collatz":
        If_Else(
            Operator(
                lambda a,b: a != b,
                Variable('A',{}),
                Value(1,{}),
                {}
            ),
            If_Else(
                Operator(
                    lambda a,b: a % b == 0,
                    Variable('A',{}),
                    Value(2,{}),
                    {}
                ),
                Apply(
                    'A',
                    Operator(
                        lambda a,b: a // b,
                        Variable('A',{}),
                        Value(2,{}),
                        {}
                    ),
                    Variable("collatz",{}),
                    {}
                ),
                Apply(
                    'A',
                    Operator(
                        lambda a,b: a + b,
                        Operator(
                            lambda c,d: c*d,
                            Variable('A',{}),
                            Value(3,{}),
                            {}
                        ),
                        Value(1,{}),
                        {}
                    ),
                    Variable("collatz",{}),
                    {}
                ),
                {}
            ),
            Variable('A',{}),
            {}
        ),
        'A':Value(69,{})}
    print(execute(Variable("collatz",{}),environment).value)
    while True:
        selected_text = input(">> ")
        

    
    
try:    
    main()
except QuitException:
    print("Quitting the interpreter, bye!")
except KeyboardInterrupt:
    print("\nKeyboard interrupt triggered")

    



