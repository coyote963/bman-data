from db_operations import get_mongo_client
from tabulate import tabulate
from webhook import execute_webhook
from webhook_url import urlranking
db = get_mongo_client()
def round_floats(results):
    for result in results:
        for k, v in result.items():
            try:
                result[k] = int(v)
            except ValueError:
                pass

def merge_values(results):
    for result in results:
        result['trueskill'] = str(result['mu']) + " +/- " + str(result['sigma'])
        result['kd'] = str(result['kills']) + " / " + str(result['deaths'])
        result['win/loss'] = str(result['wins']) + " / " + str(result['losses'])
        del result['mu']
        del result['sigma']
        del result['wins']
        del result['losses']
        del result['kills']
        del result['deaths']

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

result = list(db.dm_profiles.aggregate(pipeline))[:20]
for i in range(0, len(result)):
    result[i]['rank'] = i+1
round_floats(result)
rankings = tabulate(result, headers="keys")

execute_webhook("DM Rankings```{}```".format(rankings), url = urlranking)


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
            'elo': 1, 
            'kills': 1, 
            'deaths': 1, 
            'wins': 1, 
            'losses': 1, 
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
            'elo': 1, 
            'kills': 1, 
            'deaths': 1, 
            'wins': 1, 
            'losses': 1, 
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

full_result = list(db.tdm_profiles.aggregate(pipeline))
result = full_result[:15]
for i in range(0, len(result)):
    result[i]['rank'] = i+1
round_floats(result)
merge_values(result)
rankings = tabulate(result , headers="keys")
execute_webhook("TDM Rankings```{}```".format(rankings), url = urlranking)

print(rankings)
rankings = tabulate(full_result , headers="keys")

