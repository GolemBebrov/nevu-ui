import json

class Struct:
    def __init__(self, config: dict):
        self.config = config

    def add(self, key: str, value):
        keys = key.lower().split(".")
        current_conf = self.config
        for k in keys[:-1]:
            current_conf = current_conf.setdefault(k, {})
        current_conf[keys[-1]] = value
        return
    
    def get(self, key: str, default = None):
        if isinstance(key, str):
            key = key.lower()
            keys = key.split('.')
        else:
            keys = key
            return keys
        current_level = self.config
        for k in keys:
            if not isinstance(current_level, dict) or k not in current_level:
                if default is not None:
                    return default
                raise KeyError(f"Key {key} not found")
            current_level = current_level[k]
        return current_level
    
    def get_dict(self, key: str, default = None) -> dict:
        result = self.get(key)
        if not isinstance(result, dict):
            if default is not None:
                return default
            raise TypeError(f"Key {key} is not a dict")
        return result
    
    def get_any(self, key: str):
        return self.get_dict(key) or self.get(key)
    
    def _get_name(self, key: str):
        return key.split(".")[-1]
    
    def open(self, key: str, copy_dict = False):
        is_dict = isinstance(self.get(key), dict)
        if not is_dict:
            return SubItem(self._get_name(key), self.get(key))
        dict_val = self.get_dict(key).copy() if copy_dict else self.get_dict(key)
        return SubStruct(self._get_name(key), dict_val, self)
    
    def __repr__(self):
        return json.dumps(self.config)

    def __str__(self) -> str:
        return json.dumps(self.config, indent = 4)

class SubItem:
    def __init__(self, name: str, value):
        self.name = name
        self.value = value

class SubStruct(Struct):
    def __init__(self, name: str, config_part: dict, root: Struct | None = None, ):
        super().__init__(config_part)
        self.root = root
        self.name = name
        
    def close(self):
        assert self.root
        level = self.root.get(self.name)
        assert isinstance(level, dict)
        level.update(self.config)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()