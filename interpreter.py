
    
VERSION = "0.1.0-dev"
YEAR = "2021"

from functools import reduce
from zipfile import ZipFile
from io import TextIOWrapper as io_wrap


class UnresolvableVariable(Exception):
    pass



class Value:
    
    """Value Object
    This type stores the evaluation of any data
    
    Attributes:
        __init__: Constructor
        step:     Small-step executive function
        pr:       Human-Readable format string-builder
        value:    Contained value of the type
        
    """
    def __init__(self, value, environ={}):
        """Creates a Value Object
        Parameter:
            value   -> any:  The stored evaluation
            environ -> dict: 
        
        """
        self.value, self.environment = value, environ
    
    def step(self,local_environment: dict):
        """ Iteratively small-step execution
        
        Parameter:
            local_environment -> dict: local updates to the stored environment
        
        Returns:
            Value-Object
        """
        return self
    def pr(self):
        return f"{self.value}"
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
    def apply_all_dts(self,f):
        return f(self)


class Operator:
    
    def __init__(self, oper, arg1, arg2, environ={}):
        self.oper = oper
        self.arg1, self.arg2 = arg1, arg2
        self.environment = environ
    
    def step(self, local_environment: dict):
        #print("step in operator")
        temp_local = local_environment
        for k in self.environment:
            e = self.environment[k]
            temp_local[k] = e
        if(not isinstance(self.arg1, Value)):
            return Operator(self.oper, self.arg1.step(temp_local), self.arg2, self.environment)
        if(not isinstance(self.arg2, Value)):
            return Operator(self.oper, self.arg1, self.arg2.step(temp_local), self.environment)
        return Value(self.oper(self.arg1.value,self.arg2.value),self.environment)
    def pr(self):
        return f"{self.arg1.pr()} operator {self.arg2.pr()}"
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.arg1.update_all_variables(kwargs)
        self.arg2.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.arg1 = self.arg1.apply_all_dts(f)
        self.arg2 = self.arg2.apply_all_dts(f)
        return self

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
    def apply_all_dts(self,f):
        return f(self)
    
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
    
    def apply_all_dts(self,f):
        self.assigned = self.assigned.apply_all_dts(f)
        self.program = self.program.apply_all_dts(f)
        return self

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
    def apply_all_dts(self,f):
        self.conditional = self.conditional.apply_all_dts(f)
        self.yes = self.yes.apply_all_dts(f)
        self.no = self.no.apply_all_dts(f)
        return self
    def pr(self):
        return f"if {self.conditional.pr()} then {self.yes.pr()} else {self.no.pr()}"
class QuitException(Exception):
    pass


class Chain:
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
        name = self.name
        ass = self.assigned
        def tester(v):
            if(isinstance(v,Variable)):
                if(v.name == name):
                    return ass
            return v
        return self.program.apply_all_dts(tester)
    
    def pr(self):
        return f"Apply {self.name}={self.assigned.pr()} on {self.program.pr()}"
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.assigned.update_all_variables(kwargs)
        self.program.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.program =  self.program.apply_all_dts(f)
        self.assigned = self.assigned.apply_all_dts(f)
        return self

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
            self.environment[k] = kwargs[k]
        self.file_name.update_all_variables(kwargs)
        self.descriptor.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.file_name = self.file_name.apply_all_dts(f)
        return self
        
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
    def apply_all_dts(self,f):
        return self

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
    
    def apply_all_dts(self,f):
        self.file_loader = self.file_loader.apply_all_dts(f)
        self.table_name  = self.table_name.apply_all_dts(f)
        return self

class Iterator:
    
    def __init__(self, iterator, environment={}):
        self.iterator = iterator
        self.environment = environment
    def step(self, local_environment={}):
        return self
    def update_all_variables(self,kwargs):
         for k in kwargs:
            self.environment[k] = kwargs[k]
    def apply_all_dts(self,f):
        return self

class FullResolvedIterator(Iterator):
    
    def __init__(self,iterator, environment={}):
        super().__init__(iterator, environment)
    
class List(FullResolvedIterator):
    def __init__(self, lst, environment={}):
        super().__init__(lst, environment)


from itertools import chain

class ConcatenateIterator(Iterator):
    
    def __init__(self, iter1, iter2, environment={}):
        super().__init__((iter1,iter2), environment)
    
    def step(self, local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.iterator[0], FullResolvedIterator)):
            return ConcatenateIterator(self.iterator[0].step(local_env), self.iterator[1], self.environment)
        if(not isinstance(self.iterator[1], FullResolvedIterator)):
            return ConcatenateIterator(self.iterator[0],self.iterator[1].step(local_env),self.environment)
        return FullResolvedIterator(chain(self.iterator[0].iterator, self.iterator[1].iterator),self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        for iterators in self.iterator:
            iterators.update_all_variables(kwargs)

    def apply_all_dts(self,f):
        for iterators in self.iterator:
            iterators = iterators.apply_all_dts(f)
        return self
        
class Map(Iterator):

    def __init__(self, iter1, lambd, val, environment={}):
        super().__init__(iter1, environment)
        self.lambd = lambd
        self.val = val
    
    def step(self, local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.iterator, Map) and not isinstance(self.iterator, FullResolvedIterator)):
            return Map(self.iterator.step(temp_env), self.lambd, self.val, self.environment)
        if(not isinstance(self.val, Value)):
            return Map(self.iterator, self.lambd, self.val.step(temp_env), self.environment)
        if(isinstance(self.iterator, Map)):
            return Map(self.iterator.iterator, Chain(self.iterator.val.value,self.iterator.lambd,self.lambd,self.iterator.lambd.environment),self.val,self.environment)
        return FullResolvedIterator(map(lambda a: execute(Apply(self.val.value, a, self.lambd, self.lambd.environment), temp_env), self.iterator.iterator),self.environment)
    
    def update_all_variables(self, kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.iterator.update_all_variables(kwargs)
        self.lambd.update_all_variables(kwargs)
        self.val.update_all_variables(kwargs)
        
    
    def apply_all_dts(self, f):
        self.lambd = self.lambd.apply_all_dts(f)
        self.iterator.apply_all_dts(f)
        self.val.apply_all_dts(f)
        return self

class Filter(Iterator):
    
    def __init__(self, iter1, lambd, val, environment={}):
        super().__init__(iter1, environment)
        self.lambd = lambd
        self.val = val
    
    def step(self, local_environment={}):
        temp_env = local_environment
        for k in self.environment:
            temp_env[k] = self.environment[k] 
        if(not isinstance(self.iterator, Filter) and not isinstance(self.iterator, Map) and not isinstance(self.iterator, FullResolvedIterator)):
            return Filter(self.iterator.step(temp_env), self.lambd, self.val, self.environment)
        if(not isinstance(self.val, Value)):
            return Filter(self.iterator, self.lambd, self.val.step(temp_env), self.environment)
        if(isinstance(self.iterator, Map)):
            return Map(Filter(self.iterator.iterator, Chain(self.val.value, self.iterator.lambd, self.lambd,self.iterator.lambd.environment), self.iterator.val,self.iterator.environment),self.iterator.lambd, self.iterator.val, self.iterator.environment)
        if(isinstance(self.iterator, Filter)):
            return Filter(self.iterator.iterator, Apply(self.iterator.val.value, Variable(self.value.val,temp_env), And(self.lambd,self.iterator.lambd,temp_env),temp_env), self.value, self.environment)
        return FullResolvedIterator(filter(lambda a: execute(Apply(self.val.value,a,self.lambd,temp_env),temp_env).value, self.iterator.iterator),self.environment)

    def update_all_variables(self, kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.iterator.update_all_variables(kwargs)
        self.lambd.update_all_variables(kwargs)
        self.val.update_all_variables(kwargs)
        
    
    def apply_all_dts(self, f):
        self.lambd = self.lambd.apply_all_dts(f)
        self.iterator.apply_all_dts(f)
        self.val.apply_all_dts(f)
        return self
            

class ToList:
    
    def __init__(self,iterator, environment={}):
        self.iterator = iterator
        self.environment=environment
    def step(self, local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.iterator, FullResolvedIterator)):
            return ToList(self.iterator.step(temp_env),self.environment)
        if(isinstance(self.iterator, List)):
            return self.iterator
        return List(list(self.iterator.iterator),self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.iterator.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.iterator = self.iterator.apply_all_dts(f)
        return self
class Access:
    
    def __init__(self,array, location, environment={}):
        self.array = array
        self.location = location
        self.environment = enivronment
    def step(self,local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.array, List) and not isinstance(self.array,Iterator)):
            return Access(self.array.step(temp_env),self.location, self.environment)
        if(isinstance(self.array,Iterator)):
            return Access(ToList(self.array, self.environment), self.location,self.environment)
        if(not isinstance(self.location, Value)):
            return Access(self.array, self.location.step(temp_env),self.environment)
        return Value(self.array.iterator[self.location.value],self.array.environment)
    
            
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.array.update_all_variables(kwargs)
        self.location.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.array = self.array.apply_all_dts(f)
        self.location = self.location.apply_all_dts(f)
        return self


class Print:
    def __init__(self,expression,environment={}):
        self.expression = expression
        self.environment = environment
    def step(self, local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.expression, Value) and not isinstance(self.expression, List)):
            return Print(self.expression.step(temp_env),self.environment)
        if(isinstance(self.expression,List)):
            print(f'[{", ".join(map(lambda a: str(execute(a,temp_env).value) ,self.expression.iterator))}]')
            return Value(None,self.environment)
        if(isinstance(self.expression,NamedTuple)):
            for key in self.expression.value:
                while(not isinstance(self.expression.value[key],Value)):
                    self.expression.value[key] = self.expression.value[key].step(temp_env)
            print({key:self.expression.value[key].value for key in self.expression.value})
            return Value(None,self.environment)
        print(self.expression.value)
        return Value(None,self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.expression.update_all_variables(kwargs)
    
    def apply_all_dts(self,f):
        self.expression = self.expression.apply_all_dts(f)
        return self
    
class Get:
    def __init__(self,Input_Response=Value(">:",{}),force_type=lambda a:a,environment={}):
        self.force_type = force_type
        self.environment = environment
        self.input_response = Input_Response
    def step(self,local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.input_response,Value)):
            return Get(self.input_response.step(temp_env),self.force_type,self.environment)
        return Value(self.force_type(input(self.input_response.value)),self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.input_response.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.input_response = self.input_response.apply_all_dts(f)
        return self

class Not(Operator):
    def __init__(self,arg1,env={}):
        super().__init__(lambda a,b: not a, arg1, arg1, env)

class And(Operator):
    def __init__(self,arg1,arg2,env={}):
        super().__init__(lambda a,b: a and b, arg1, arg2, env)

class Or(Operator):
    def __init__(self,arg1,arg2,env={}):
        super().__init__(lambda a,b: a or b, arg1, arg2, env)

class Negate(Operator):
    def __init__(self,arg1,env={}):
        super().__init__(lambda a,b: -a, arg1, arg1, env)

class Equal(Operator):
    def __init__(self, arg1, arg2, env={}):
        super().__init__(lambda a, b: a == b, arg1, arg2, env)

class Less(Operator):
    def __init__(self, arg1, arg2, env={}):
        super().__init__(lambda a, b: a < b, arg1, arg2, env)

class Add(Operator):
    def __init__(self, arg1, arg2, env={}):
        super().__init__(lambda a,b: a+b, arg1, arg2, env)

class Mult(Operator):
    def __init__(self, arg1, arg2, env={}):
        super().__init__(lambda a,b: a*b, arg1, arg2, env)

class Invert(Operator):
    def __init__(self, arg1, env={}):
        super().__init__(lambda a,b: 1/a, arg1, arg2, env)

class NamedTuple(Value):
    
    def __init__(self,data,env={}):
        
        if(isinstance(data,list)):
            super().__init__({name:None for name in data},env)
        else:
            super().__init__(data,env)
    
    def step(self,local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        for vals in self.value:
            if(not isinstance(self.value[vals],Value)):
                data_cpy = self.value
                data_cpy[vals] = data_cpy[vals].step(temp_env)
                return NamedTuple(data_cpy,self.environment)
        return EvaluatedTuple(self.value,self.environment)
    
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        for keys in self.value:
            self.value[keys].update_all_variables(kwargs)
    def apply_all_dts(self,f):
        for keys in self.value:
            self.value[keys] = self.value[keys].apply_all_dts(f)
        return self

class EvaluatedTuple(NamedTuple):
    
    def __init__(self,data,env={}):
        print("constructing")
        super().__init__(data,env)
    
    def step(self,local_environment={}):
        raise Exception(" YOU SHOULD NOT BE ABLE TO SEE THIS! ")
    
class GetTupleData:
    def __init__(self,tup,attribute_name,environment={}):
        self.tup = tup
        self.attribute_name = attribute_name
        self.environment = environment
    def step(self,local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.tup,EvaluatedTuple)):
            return GetTupleData(self.tup.step(temp_env),self.attribute_name,self.environment)
        if(not isinstance(self.attribute_name,Value)):
            return GetTupleData(self.tup,self.attribute_name.step(temp_env),self.environment)
        if(self.attribute_name.value not in self.tup.value):
            raise Exception(f"Member Name {self.attribute_name.value} not in tuple!")
        return self.tup.value[self.attribute_name.value]

class UpdateTuple:
    def __init__(self,tup,attribute_name,value,eager=True,environment={}):
        self.tup = tup
        self.attribute_name = attribute_name
        self.value = value
        self.eager = eager
        self.environment = environment
    def step(self,local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.tup,NamedTuple)):
            return UpdateTuple(self.tup.step(temp_env),self.attribute_name,self.value,self.eager,self.environment)
        if(not isinstance(self.attribute_name,Value)):
            return UpdateTuple(self.tup,self.attribute_name.step(temp_env),self.value,self.eager,self.environment)
        if(self.eager and not isinstance(self.value,Value)):
            return UpdateTuple(self.tup,self.attribute_name,self.value.step(temp_env),self.eager,self.environment)
        if(self.attribute_name.value not in self.tup.value):
            raise Exception(f"Member Name {self.attribute_name.value} not in tuple!")
        copy_of_tuple_data = self.tup.value
        copy_of_tuple_data[self.attribute_name.value] = self.value
        return NamedTuple(copy_of_tuple_data,self.tup.environment)



def execute(program, environment: dict) -> Value:
    while(not isinstance(program, Value)):
        #print("stepping")
        #print(environment['A'].value)
        program = program.step(environment)
        #print(program.pr())
        #input()
    return program




class Type:
    def __init__(self,expression,environment={}):
        self.expression = expression
        self.environment = environment
    def step(self,local_environment={}):
        temp_env = local_environment
        for var in self.environment:
            temp_env[var] = self.environment[var]
        if(not isinstance(self.expression, Value)):
            return Type(self.expression.step(temp_env),self.environment)
        if(isinstance(self.expression,NamedTuple)):
            return Value("NamedTuple",self.environment)
        return Value(type(self.expression.value),self.environment)
    def update_all_variables(self,kwargs):
        for k in kwargs:
            self.environment[k] = kwargs[k]
        self.expression.update_all_variables(kwargs)
    def apply_all_dts(self,f):
        self.expression = self.expression.apply_all_dts(f)
        return self
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
        ),

        }
    execute(Print(Get(Value("please input something here: ",{})),{}),environment)
    execute(Print(Apply("A",Value(69,{}),Variable("collatz",{}),{}),{}),environment)
    execute(Print(Apply("B",Value(20,{}),Chain("C",Operator(lambda a,b: a*b,Variable("B",{}),Variable("B",{}),{}),Operator(lambda a,b: a+b,Variable("C",{}),Value(2,{}),{}),{}),{}),{}),environment)
    execute(Print(Add(Value(69,{}),Value(42000,{}),{}),{}),environment)
    execute(Print(GetTupleData(NamedTuple({"first":Value(2,{}),"second":Value(3,{})},{}),Value("second"),{}),{}),environment)
    execute(Print(UpdateTuple(UpdateTuple(NamedTuple({"first":Value(2,{}),"second":Value(1,{})},{}),Value("second"),GetTupleData(NamedTuple({"first":Value(2,{}),"second":Value(3,{})},{}),Value("first"),{}),True,{}),Value("first"),GetTupleData(NamedTuple({"first":Value(2,{}),"second":Value(3,{})},{}),Value("second"),{}),True,{}),{}),environment)
    execute(Print(List([Value("first"),Value("second"),Value("third")]),{}),environment)
    #print(execute(UnwrapTable(FSLoader(Value("./Loaders/table.ftab",{})),Value("table1",{}),{}),environment).value)
    execute(Print(Type(Value(None,{}),{}),{}),environment)
    execute(Print(ToList(Map(List([Value(3),Value(9),Value(2)]),Mult(Variable("var",{}),Value(2,{}),{}),Value("var",{}),{}),{}),{}),environment)
    while True:
        selected_text = input(">> ")
        

    
    
try:    
    main()
except QuitException:
    print("Quitting the interpreter, bye!")
except KeyboardInterrupt:
    print("\nKeyboard interrupt triggered")

    



