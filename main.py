import rest_methods
import json
import os
import sys
import time
from pathlib import Path

integration_manifest_path = "manifests/integration.json"
engine_manifest_path = "manifests/engine.json"
device_agent_manifest_path = "manifests/device_agent.json"
credentials_path = ".credentials/credentials.json"
object_data_path = "data/object_data.json"
event_data_path = "data/event_data.json"


def register_integration():
    with (open(integration_manifest_path, 'r') as integration_manifest,
          open(engine_manifest_path, 'r') as engine_manifest,
          open(device_agent_manifest_path, 'r') as device_agent_manifest):
        _result = rest_methods.register(integration_manifest=json.load(integration_manifest),
                                        engine_manifest=json.load(engine_manifest),
                                        device_agent_manifest=json.load(device_agent_manifest)
                                        )

        if _result[0] is None:
            return _result[2]

        _credentials = _result[0]
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

        with open(credentials_path, 'w') as f:
            json.dump(_credentials, f)
        sys.stdout.write('Registered. Waiting for approval\n')
        return None


if __name__ == '__main__':
    credentials_path = Path(credentials_path)

    # If no credentials file, assuming that Integration is not registered.
    # Try to register and finish with registration result
    if not credentials_path.exists():
        sys.exit(register_integration())

    with open(credentials_path, 'r') as credentials_file:
        credentials = json.load(credentials_file)

    token = rest_methods.authenticate(credentials['user_name'], credentials['password'])
    approved = rest_methods.is_integration_approved(credentials['user_name'], token)

    if not approved:
        sys.exit('Integration request is not approved yet')

    integration_id = rest_methods.get_integration_id(user_id=credentials['user_name'], token=token)
    engine_id = rest_methods.get_engine_id(integration_id=integration_id, token=token)
    device_agents = rest_methods.get_device_agents(engine_id=engine_id, token=token)

    if len(device_agents) == 0:
        raise RuntimeError('No devices with Integration enabled')

    with (open(event_data_path, 'r') as event_data_file, open(object_data_path, 'r') as object_data_file):
        events = json.load(event_data_file)
        objects = json.load(object_data_file)

    # Send Event
    additional_data = {
        "id": engine_id,
        "timestampUs": int(time.time()),
        "durationUs": 30000
    }
    event_data = additional_data | events

    rest_methods.send_event(engine_id=engine_id, token=token, device_id=device_agents[0]['id'], event_data=event_data)
    sys.stdout.write('Successfully sent an event\n')

    # Send Object
    additional_data = {
        "id": engine_id,
        "timestampUs": int(time.time()),
        "durationUs": 30000,
        }

    object_data = additional_data | objects
    rest_methods.send_object(engine_id=engine_id, token=token,
                             device_id=device_agents[0]['id'], object_data=object_data)
    sys.stdout.write('Successfully sent an object\n')
