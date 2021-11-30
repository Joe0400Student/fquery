



def tokenizer(s: str) -> list:
    
    def name(s: str, previous: str) -> tuple:
        print("calling name")
        print(s)
        input()
        if(len(s) == 0):
            print("exiting name")
            return ("name",previous,s)
        elif(s[0] in " \n\t:=?<>|^*+-!()[]{}\/.,;'\"~`@"):
            print("exiting name")
            return ("name",previous,s)
        else:
            ret = name(s[1:],previous+s[0])
            print("exiting name")
            return ret
    def constant_value(s: str, previous: str) -> tuple:
        print("calling const_value")
        print(s)
        input()
        if(len(s) == 0):
            print("exiting const_value")
            return ("val",previous,s)
        elif(s[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"):
            ret = name(s[1:],previous+s[0])
            print("exiting const_value")
            return ret
        elif(s[0] not in "0123456789."):
            print("exiting const_value")
            return ("val",previous,s)
        else:
            ret = constant_value(s[1:],previous+s[0])
            print("exiting const_value")
            return ret

    tokens = []
    if(len(s) == 0):
        return tokens
    
    while(len(s) != 0):
        input(s)
        if(s[0] in " \n\t"):
            s = s[1:]
        elif(s[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"):
            temp = constant_value(s,"")
            s = temp[2]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "=>"):
            temp = temp = ("lambda",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "?="):
            temp = ("lazy assign",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == ":="):
            temp = ("eager assign",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "**"):
            temp = ("power",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "|>"):
            temp = ("pipe",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "=="):
            temp = ("equal",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "<="):
            temp = ("less or equal",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == ">="):
            temp = ("greater or equal",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0:2] == "!="):
            temp = ("not equal",s[0:2],s[2:])
            s = s[2:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "*"):
            temp = ("multiply",s[0],s[1:])
            s = s[1:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "+"):
            temp = ("add",s[0],s[1:])
            s = s[1:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "/"):
            temp = ("divide",s[0],s[1:])
            s = s[1:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "-"):
            temp = ("invert/subtract",s[0],s[1:])
            s = s[1:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "<"):
            temp = ("less",s[0],s[1:])
            s = s[1:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == ">"):
            temp = ("greater",s[0],s[1:])
            s = s[1:]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "("):
            temp = ("open paren",s[0],s[1:])
            s = temp[2]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == ")"):
            temp = ("close paren",s[0],s[1:])
            s = temp[2]
            temp = (temp[0],temp[1])
            tokens.append(temp)
        elif(s[0] == "."):
            temp = ("call or member",s[0],s[1:])
            s = temp[2]
            temp = (temp[0],temp[1])
            tokens.append(temp)
            
    return tokens
        
print(tokenizer("label := thing.map(a => a * 2)"))


