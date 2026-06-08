from nevu_ui.core.enums import EventType

class NevuEvent:
    __slots__ = ("_sender", "_function", "_type", "_args", "_kwargs")
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
            raise e
            print(f"Event function execution Error: {e}\nsender: {self._sender}, function: {self._function}, type: {self._type}, args: {self._args}, kwargs: {self._kwargs}")
    
    def __repr__(self) -> str:
        return f"Event(sender={self._sender}, function={self._function}, type={self._type}, args={self._args}, kwargs={self._kwargs})"
