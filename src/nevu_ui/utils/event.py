from nevu_ui.core_types import EventType

class Event:
    DRAW = 0
    UPDATE = 1
    RESIZE = 2
    RENDER = 3
    def __init__(self,type,function,*args, **kwargs):
        """
        Initializes an Event object with a type, function, and optional arguments.

        Parameters:
        type (int): The type of event, indicating the kind of operation.
        function (callable): The function to be executed when the event is triggered.
        *args: Variable length argument list to be passed to the function.
        **kwargs: Arbitrary keyword arguments to be passed to the function.
        """
        self.type = type
        
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def __call__(self,*args, **kwargs):
        if args: self._args = args
        if kwargs: self._kwargs = kwargs
        self._function(*self._args, **self._kwargs)

class NevuEvent:
    def __init__(self, sender, function, type: EventType, *args, **kwargs):
        self._sender = sender
        self._function = function
        self._type = type
        self._args = args
        self._kwargs = kwargs
        
    def __call__(self, *args, **kwargs):
        if args: self._args = args
        if kwargs: self._kwargs = kwargs
        try:
            self._function(*self._args, **self._kwargs)
        except Exception as e:
            print(f"Event function execution Error: {e}")
    def __repr__(self) -> str:
        return f"Event(sender={self._sender}, function={self._function}, type={self._type}, args={self._args}, kwargs={self._kwargs})"
