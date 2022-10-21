def serializeDict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'},**{i:a[i] for i in a if i!='_id'},**{i:str(a[i]) for i in a if i=='until_date'}}

def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]
