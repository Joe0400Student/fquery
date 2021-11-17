
    
VERSION = "0.0.2-dev"
YEAR = "2021"

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

from zipfile import ZipFile
from io import TextIOWrapper as io_wrap

class FSLoader:
    
    def __init__(self,file_name,environment={}):
        descriptor=Value("a",{})
        self.file_name = file_name
        self.descriptor = descriptor
        self.environment=environment

    def step(self, local_environment={}):

        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.file_name, Value)):
            return FSLoader(self.file_name.step(temp_env),self.descriptor,{})
        if(not isinstance(self.descriptor, Value)):
            return FSLoader(self.file_name, self.descriptor.step(temp_env),{})
        self.file_name = self.file_name.value
        self.descriptor = self.descriptor.value
        self.file = ZipFile(self.file_name,self.descriptor)
        self.manifest = io_wrap(self.file.open("manifest.txt"))
        table_names = map(lambda a: a[:-1], self.manifest.readlines())
        self.tables = {line:io_wrap(self.file.open(f"{line}.table")) for line in table_names}
        return Loaded_Table(self.file, self.manifest, self.tables,self.environment)
    def update_all_variables(self, kwargs):
        for k in kwargs:
            self.environ[k] = kwargs[k]
        self.file_name.update_all_variables(kwargs)
        self.descriptor.update_all_variables(kwargs)
        
class Loaded_Table:
    def __init__(self,file, manifest, tables, environment={}):
        self.file = file
        self.manifest = manifest
        self.tables = tables
        self.environment = environment
    
    def step(self, local_environment={}):
        raise Exception("Loaded table trying to be propogated back down the call trace, <you shouldnt be seeing this, make an issue on https://github.com/Joe0400Student/fquery>")
    
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]


class UnwrapTable:
    
    def __init__(self, file_loader, table_name,environment={}):
        self.file_loader = file_loader
        self.table_name = table_name
        self.environment = environment
    
    def step(self, local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.file_loader, Loaded_Table)):
            return UnwrapTable(self.file_loader.step(temp_env),self.table_name,self.environment)
        if(not isinstance(self.table_name, Value)):
            return UnwrapTable(self.file_loader,self.table_name.step(temp_env),self.environment)
        return Value(self.file_loader.tables[self.table_name.value],self.environment)

    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.file_loader.update_all_variables(kwargs)
        self.table_name.update_all_variables(kwargs)


class Print:
    def __init__(self,expression,environment={}):
        self.expression = expression
        self.environment = environment
    def step(self, local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.expression, Value)):
            return Print(self.expression.step(temp_env),self.environment)
        print(self.expression.value)
        return Value(None,self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.expression.update_all_variables(kwargs)

    
    

def execute(program, environment: dict) -> Value:
    while(not isinstance(program, Value)):
        #print("stepping")
        #print(environment['A'].value)
        program = program.step(environment)
        #print(program.pr())
        #input()
    return program



def main() -> None:
    print(f"fang[ver:{VERSION}][{YEAR}] -- Copyright Joseph Scannell - Python 3.10")
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
        )}
    
    execute(Print(Apply("A",Value(69,{}),Variable("collatz",{}),{}),{}),environment)
    print(execute(UnwrapTable(FSLoader(Value("./Loaders/table.ftab",{})),Value("table1",{}),{}),environment).value)
    while True:
        selected_text = input(">> ")
        

    
    
try:    
    main()
except QuitException:
    print("Quitting the interpreter, bye!")
except KeyboardInterrupt:
    print("\nKeyboard interrupt triggered")

    



