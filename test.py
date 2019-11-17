from db_operations import get_mongo_client
from tabulate import tabulate
db = get_mongo_client()
pipeline = [
    {
        '$lookup': {
            'from': 'players', 
            'localField': 'player', 
            'foreignField': '_id', 
            'as': 'newplayer'
        }
    }, {
        '$project': {
            'player.platform': 1, 
            'mu': 1, 
            'sigma': 1, 
            'first': {
                '$arrayElemAt': [
                    '$newplayer', 0
                ]
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'mu': 1, 
            'sigma': 1, 
            'result': {
                '$subtract': [
                    '$mu', {
                        '$multiply': [
                            3, '$sigma'
                        ]
                    }
                ]
            }, 
            'name': {
                '$arrayElemAt': [
                    '$first.name', 0
                ]
            }
        }
    }, {
        '$sort': {
            'result': -1
        }
    }
]

result = list(db.dm_profiles.aggregate(pipeline))

print(tabulate(result, headers="keys"))