from pydantic import BaseModel, field_validator

def valid_data(value, lsit_fields):
    data = {}
    
    try:
        if value is not None:
            value = value.split(",", -1)
            for i in value:
                n = i.split(":", -1)
                if n[0] in lsit_fields:
                    data[n[0]] = n[1]
                else:
                    raise ValueError(f"The invalid field must be the {lsit_fields}.")
    except ValueError:
        raise ValueError(f"The invalid field must be the {lsit_fields}.")
    return data

class GetData(BaseModel):
    offset: int = 0
    limit: int = 10

class SearchData(BaseModel):
    offset: int = 0
    limit: int = 10
    sorting: str = None

    @field_validator("sorting")
    def valid_sorting(cls, value) -> list[tuple[str, bool]]:
        value = value.replace(" ", "").split(",", -1)
        output_list = []
        
        for i in value:
            sorting_field = i.split(":", 1)

            if len(sorting_field) == 2:
                reverse = sorting_field[1]
                field = sorting_field[0]

                if reverse.lower() == "true":
                    reverse = True
                elif reverse.lower() == "false":
                    reverse = False
                else:
                    raise ValueError("reverse parameter error (must be true or false)")

                if "--" in field:
                    raise ValueError("field error")

                output_list.append((field, reverse))

            else:
                raise ValueError("Error, the string must contain field:revers (str:bool)")
        return output_list