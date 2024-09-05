import sys

import requests
import json

vms_url = '172.19.7.98'
vms_port = '7001'
integrations_register_path = "/rest/v4/analytics/integrations/*/requests"
users_path = "/rest/v4/users"
login_path = "/rest/v4/login/sessions"
devices_path = '/rest/v4/devices'
object_path = '/rest/v4/analytics/engines/{id}/deviceAgents/{deviceId}/metadata/object'
engines_path = ''


def register(integration_manifest, engine_manifest):
    url = 'https://' + vms_url + ':' + vms_port + integrations_register_path
    data = {
        'integrationManifest': integration_manifest,
        'engineManifest': engine_manifest,
        'pinCode': '1234'
    }

    response = requests.post(url, verify=False, json=data, headers={'Content-type': 'application/json'})

    content = json.loads(response.content)
    if response.status_code == 200 and 'user' in content and 'password' in content:
        credentials = {
            'user_name': content['user'],
            'password': content['password']
        }

        return credentials, 0, 'Successfully registered'

    elif response.status_code == 200:
        return None, 0, 'No credentials returned'
    else:

        return None, content.get('errorID', None), 'Error: ' + content.get('errorString', 'Unknown error')


def authenticate(username, password):
    url = 'https://' + vms_url + ':' + vms_port + login_path
    data = {'username': username, 'password': password, 'setCookie': True, 'durationS': 100}
    response = requests.post(url=url, verify=False, headers={'Content-type': 'application/json'}, data=json.dumps(data))
    if response.status_code == 200:
        return json.loads(response.content).get('token', None)
    else:
        raise Exception(response.text)


def get_integration_approved(user_id, token):
    url = 'https://' + vms_url + ':' + vms_port + users_path + "/" + user_id
    response = requests.get(url, verify=False, headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})
    content = json.loads(response.content)
    if response.status_code == 200:
        return content.get('parameters', {}).get('integrationRequestData', {}).get('isApproved', False) is True
    else:
        return False


def get_devices(token):
    url = 'https://' + vms_url + ':' + vms_port + devices_path
    response = requests.get(url, verify=False,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})
    return json.loads(response.content)


def get_engine(integration_id):
    pass


def send_object(engine_id, device_id, object_data, token):
    url = 'https://' + vms_url + ':' + vms_port + object_path.format(id=engine_id, deviceId=device_id)
    response = requests.get(url, verify=False, data=object_data,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})

    if response.status_code == 200:
        sys.stdout.write('Successfully sent object')
    else:
        sys.stdout.write(str(response.status_code) + ':' + response.text)
