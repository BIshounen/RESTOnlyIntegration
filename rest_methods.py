import sys

import requests
import json

import vms_config


def register(integration_manifest, engine_manifest, device_agent_manifest):
    url = 'https://' + vms_config.vms_url + ':' + vms_config.vms_port + vms_config.integrations_register_path
    data = {
        'integrationManifest': integration_manifest,
        'engineManifest': engine_manifest,
        'deviceAgentManifest': device_agent_manifest,
        'pinCode': '1234',
        'isRestOnly': True
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
    url = 'https://' + vms_config.vms_url + ':' + vms_config.vms_port + vms_config.login_path
    data = {'username': username, 'password': password, 'setCookie': True, 'durationS': 100}
    response = requests.post(url=url, verify=False, headers={'Content-type': 'application/json'}, data=json.dumps(data))
    if response.status_code == 200:
        return json.loads(response.content).get('token', None)
    else:
        raise RuntimeError(response.text)


def get_user_parameters(user_id, token):
    url = 'https://' + vms_config.vms_url + ':' + vms_config.vms_port + vms_config.users_path + "/" + user_id
    response = requests.get(url, verify=False,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})
    if response.status_code == 200:
        return json.loads(response.content).get('parameters', {})
    else:
        raise RuntimeError(response.text)

def get_integration_approved(user_id, token):

    parameters = get_user_parameters(user_id, token)
    return parameters.get('integrationRequestData', {}).get('isApproved', False)


def get_devices(token):
    url = 'https://' + vms_config.vms_url + ':' + vms_config.vms_port + vms_config.devices_path
    response = requests.get(url, verify=False,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})
    return json.loads(response.content)


def get_device_agents(engine_id, token):
    url = ('https://' + vms_config.vms_url + ':' + vms_config.vms_port +
           vms_config.device_agents_path.format(engineId=engine_id))

    response = requests.get(url, verify=False,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise RuntimeError(response.text)


def get_integration_id(user_id, token):
    parameters = get_user_parameters(user_id, token)
    return parameters.get('integrationRequestData', {})['integrationId']


def get_engine_id(integration_id, token):
    url = 'https://' + vms_config.vms_url + ':' + vms_config.vms_port + vms_config.engines_path
    payload = {"integrationId": str(integration_id)}
    response = requests.get(url,
                            verify=False, params=payload,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})
    if response.status_code == 200:
        return json.loads(response.content)[0]['id']
    else:
        raise RuntimeError(response.text)


def send_object(engine_id, device_id, object_data, token):
    url = ('https://' + vms_config.vms_url + ':' +
           vms_config.vms_port + vms_config.object_path.format(id=engine_id, deviceId=device_id))
    response = requests.post(url, verify=False, data=json.dumps(object_data),
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})

    if response.status_code == 200:
        sys.stdout.write('Successfully sent object')
    else:
        sys.stdout.write(str(response.status_code) + ':' + response.text)


def send_event(engine_id, device_id, event_data, token):
    url = ('https://' + vms_config.vms_url + ':' +
           vms_config.vms_port + vms_config.event_path.format(id=engine_id, deviceId=device_id))
    response = requests.post(url, verify=False, json=event_data,
                            headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token})

    if response.status_code == 200:
        sys.stdout.write('Successfully sent event')
    else:
        sys.stdout.write(str(response.status_code) + ':' + response.text)
