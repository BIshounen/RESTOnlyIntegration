from rest_methods import register, get_integration_approved, authenticate, get_devices
import json
import os
import sys

integration_manifest_path = "manifests/integration.json"
engine_manifest_path = "manifests/engine.json"
device_engine_manifest_path = "manifests/device_agent.json"
credentials_path = ".credentials/credentials.json"


def register_integration():
    with open(integration_manifest_path, 'r') as integration_manifest, open(engine_manifest_path,
                                                                            'r') as engine_manifest:
        result = register(integration_manifest=json.load(integration_manifest),
                          engine_manifest=json.load(engine_manifest))

        if result[0] is None:
            sys.stdout.write(result[2])
            return

        credentials = result[0]
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        with open(credentials_path, 'w') as f:
            json.dump(credentials, f)
            sys.stdout.write('Registered. Waiting for approval')


try:
    with open(credentials_path, 'r') as credentials_file:
        credentials = json.load(credentials_file)
        if 'user_name' in credentials and 'password' in credentials:
            token = authenticate(credentials['user_name'], credentials['password'])
            approved = get_integration_approved(credentials['user_name'], token)
            if approved:
                devices = get_devices(token)
                if len(devices) == 0:
                    raise RuntimeError('No devices')
                else:
                    pass

        else:
            raise RuntimeError('Corrupted credentials file')

except OSError as e:
    if e.errno == 2:
        register_integration()
