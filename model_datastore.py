from google.cloud import datastore
from config import PROJECT_NAME

def get_client():
    return datastore.Client(PROJECT_NAME)


def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity


def create(data, kind, id):
    ds = get_client()
    key = ds.key(kind, int(id))
    entity = datastore.Entity(
        key=key,)
    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)
