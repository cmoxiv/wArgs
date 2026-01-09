
from wArgs import wArgs

@wArgs
class MyClass:
    def __init__(self, a=123, b=12.3, c='c', d=dict(aa=123,
                                                    bb=12.3,
                                                    cc='q'),
                 e=2.71123, f=False, g=1, h=4., i="qwe", j=[1, 2, 3],
                 k=(4, 5, 6), l={7, 8, 9}, m=None,
                 n=complex(1, 2), o=b'byte_string',
                 p=set([10, 11, 12]), q=frozenset([13, 14, 15]),
                 r=range(5), s="this is a string!!",
                 t=memoryview(b'memory_view'), value=42,
                 w=..., x=lambda x: x * 2, y=bytes([65, 66, 67]), z=None):
        """Initializes MyClass with various parameters.
        Args:
            a (int): An integer parameter. Default is 123.
            b (float): A float parameter. Default is 12.3.
            c (str): A string parameter. Default is 'c'.
            d (dict): A dictionary parameter. Default is {'aa': 123, 'bb': 12.3, 'cc': 'q'}.
            e (float): A float parameter. Default is 2.71123.
            f (bool): A boolean parameter. Default is False.
            g (int): An integer parameter. Default is 1.
            h (float): A float parameter. Default is 4.0.
            i (str): A string parameter. Default is "qwe".
            j (list): A list parameter. Default is [1, 2, 3].
            k (tuple): A tuple parameter. Default is (4, 5, 6).
            l (set): A set parameter. Default is {7, 8, 9}.
            m: A parameter with default None.
            n (complex): A complex number parameter. Default is complex(1, 2).
            o (bytes): A bytes parameter. Default is b'byte_string'.
            p (set): A set parameter. Default is {10, 11, 12}.
            q (frozenset): A frozenset parameter. Default is frozenset({13, 14, 15}).
            r (range): A range parameter. Default is range(5).
            s (str): A string parameter. Default is "this is a string!!".
            t (memoryview): A memoryview parameter. Default is memoryview(b'memory_view').
            value (int): An integer value to be stored in the instance. Default is 42.
            w: A parameter with default Ellipsis (...).
            x (function): A lambda function that doubles its input. Default is lambda x: x * 2.
            y (bytes): A bytes parameter. Default is bytes([65, 66, 67]).
            z: A parameter with default None.
        """
        
        self.__dict__.update(locals())
        pass

    

    def display(self, x, y, z=10):
        """Displays the value of the instance variable 'value'.
        Args:
            x: An unused parameter.
            y: An unused parameter.
            z (int): An unused parameter with default value 10.
        """
        print(f"Value: {self.value}")
        return self.value

    pass


if __name__ == "__main__":
    obj = MyClass(a=423)
    print(f"{type(obj)} created.")
    obj.display(1, 2)
    print(obj.__dict__)
    print("Done")

    
        
