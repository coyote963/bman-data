from db_operations import get_mongo_client
from datetime import datetime
db = get_mongo_client()
db.dm_profiles.update_many({},{'$set' : {
    'last_updated' : datetime.utcnow()
}}, False)