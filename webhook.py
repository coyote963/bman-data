import requests
import json

def execute_webhook(content, url = None):
    data = {}
    data["content"] = content
    data["username"] = "coybot"

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))


def send_discord(js, url):
    content = "**{}**: {}".format(js['Name'], js['Message'])
    execute_webhook(content, url)
