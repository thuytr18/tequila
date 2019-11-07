from openvqe import OpenVQEException
from functools import total_ordering
from openvqe import copy
from openvqe import numbers
from inspect import signature
from openvqe import numpy as np

class SympyVariable:

    def __init__(self, name=None, value=None):
        self._name = name
        self._value = value

    def __call__(self, *args, **kwargs):
        return self._value

    def __sub__(self, other):
        return SympyVariable(name=self._name, value=self._value - other)

    def __add__(self, other):
        return SympyVariable(name=self._name, value=self._value + other)

    def __mul__(self, other):
        return SympyVariable(name=self._name, value=self._value * other)

    def __neg__(self):
        return SympyVariable(name=self._name, value=-self._value)

def enforce_number(number, numeric_type=complex) -> complex:
    """
    Try to convert number into a numeric_type
    No converion is tried when number is already a numeric type
    If numeric_type is set to None, then no conversion is tried
    :param number: the number to convert
    :param numeric_type: the numeric type into which conversion shall be tried when number is not identified as a number
    :return: converted number
    """
    if isinstance(number, numbers.Number):
        return number
    elif numeric_type is None:
        return number
    else:
        numeric_type(number)


def enforce_number_decorator(*numeric_types):
    """
    :param numeric_types: type for argument 0, 1, 3. Set to none if an argument shall not be converted
    :return: If the arguments are not numbers this decorator will try to convert them to the given numeric_types
    """

    def decorator(function):
        def wrapper(self, *args):
            assert (len(numeric_types) == len(args))
            converted = [enforce_number(number=x, numeric_type=numeric_types[i]) for i, x in enumerate(args)]
            return function(self, *converted)

        return wrapper

    return decorator

class Variable():
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value=value

    @property
    def name(self):
        return self._name
    


    def __init__(self, value=None, name: str = ''):
        self._value = value
        self._name = name

    def has_var(self,x):
        if type(x) is Variable:
            return self == x
        elif type(x) is str:
            return self._name == x
        else:
            raise TypeError('Unsupported type')

    def __eq__(self,other):
        if type(self)==type(other):
            self.name ==other.name and self.value==other.value
            return True
        return False

    def __add__(self, other: float):
        return Transform(Add,[self,other])

    def __radd__(self, other: float):
        if other == 0:
            return self
        else:
            return Transform(Add,[other,self])

    def __sub__(self, other):
        return Transform(Sub,[self,other])

    def __rsub__(self,other):
            return Transform(Sub,[other,self])

    def __mul__(self, other):
        # return self._return*other
         return Transform(Mul,[self,other])

    def __rmul__(self,other):

        return Transform(Sub,[other,self])

    def __neg__(self):
        return Transform(Mul,[self,-1])


    def __div__(self, other):
        return Transform(Div,[self,other])

    def __rdiv__(self, other):
        return Transform(Div,[other,self])

    def __truediv__(self, other):
        return Transform(Div,[self,other])


    def __pow__(self, other):
        return Transform(Pow,[self,other])

    def __rpow__(self,other):
        return Transform(Pow,[other,self])

    def __iadd__(self,other):
        self._value+=other
        return self

    def __isub__(self,other):
        self._value -= other
        return self

    def __imul__(self,other):
        self._value *= other
        return self


    def __idiv__(self,other):
        self._value /= other
        return self

    def __ipow__(self,other):
        self._value **= other
        return self

    def __getstate__(self):
        return self

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __le__(self, other):
        return self.value <= other

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        else:
            return True

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __call__(self):
        return self.value

    def __repr__(self):
        return self.name + ', ' + str(self._value) 

class Transform():

    @property
    def variables(self):
        vl=[]
        for obj in self.args:
            if type(obj) is Variable:
                if obj not in vl:
                    vl.append(obj)
            elif type(obj) is Transform:
                for v in obj.variables:
                    if v not in vl:
                        vl.append(v)
            else:
                pass
        return vl

    @property
    def eval(self):
        new_a=[]
        for arg in self.args:
            if hasattr(arg,'__call__'):
                new_a.append(arg())
            else:
                new_a.append(arg)

        return self.f(*new_a)


    
    

    def __init__(self,func,args):
        assert callable(func)
        assert len(args) == len(signature(func).parameters)
        self.args=args
        self.f=func




    def has_var(self,x):
        if x in self.variables:
            return True
        else:
            return False

    def __call__(self):
        return self.eval

    def __eq__(self, other):
        if type(self) == type(other):
            if self.eval==other.eval:
                return True

        return False


    def __add__(self, other: float):
        return Transform(Add,[self,other])

    def __radd__(self, other: float):
        if other == 0:
            return self
        else:
            return Transform(Add,[other,self])

    def __sub__(self, other):
        return Transform(Sub,[self,other])

    def __rsub__(self,other):
            return Transform(Sub,[other,self])

    def __mul__(self, other):
        # return self._return*other
         return Transform(Mul,[self,other])

    def __rmul__(self,other):

        return Transform(Sub,[other,self])

    def __neg__(self):
        return Transform(Mul,[self,-1])


    def __div__(self, other):
        return Transform(Div,[self,other])

    def __rdiv__(self, other):
        return Transform(Div,[other,self])

    def __truediv__(self, other):
        return Transform(Div,[self,other])


    def __pow__(self, other):
        return Transform(Pow,[self,other])

    def __rpow__(self,other):
        return Transform(Pow,[other,self])

    def __getstate__(self):
        return self

    def __lt__(self, other):
        return self.eval < other

    def __gt__(self, other):
        return self.eval > other

    def __ge__(self, other):
        return self.eval >= other

    def __le__(self, other):
        return self.eval <= other

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        else:
            return True

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result



def has_variable(obj,var):
    assert type(var) is Variable
    if hasattr(obj,'has_var'):
        return obj.has_var(var)
    else:
        return False

def Add(l,r):
    if type(l) in [Variable, Transform]:
        lv=l()
    else:
        lv=l
    if type(r) in [Variable, Transform]:
        rv=r()
    else:
        rv=r
    return lv+rv

def Sub(l,r):
    if type(l) in [Variable, Transform]:
        lv=l()
    else:
        lv=l
    if type(r) in [Variable, Transform]:
        rv=r()
    else:
        rv=r
    return lv -rv

def Mul(l,r):
    if type(l) in [Variable, Transform]:
        lv=l()
    else:
        lv=l
    if type(r) in [Variable, Transform]:
        rv=r()
    else:
        rv=r
    return lv*rv

def Div(l,r):
    if type(l) in [Variable, Transform]:
        lv=l()
    else:
        lv=l
    if type(r) in [Variable, Transform]:
        rv=r()
    else:
        rv=r
    return lv/rv

def Inverse(l):
    if type(l) in [Variable, Transform]:
        lv=l()
    else:
        lv=l

    return 1.0/l

def Pow(l,r):
    if type(l) in [Variable, Transform]:
        lv=l()
    else:
        lv=l
    if type(r) in [Variable, Transform]:
        rv=r()
    else:
        rv=r
    return l**r