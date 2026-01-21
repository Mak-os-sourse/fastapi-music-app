import re
from enum import StrEnum

class Base(StrEnum):
    def paste(self, **args) -> str:
        data = self.value
        for key, value in args.items():
            data = re.sub("{" + key + "}", str(value), data)
            
        return data

    def __str__(self) -> str:
        return self.value