import rest_methods
import json
import os
import sys
import time

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
            sys.stdout.write(_result[2])
            return

        _credentials = _result[0]
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        with open(credentials_path, 'w') as f:
            json.dump(_credentials, f)
            sys.stdout.write('Registered. Waiting for approval')


try:
    with open(credentials_path, 'r') as credentials_file:
        credentials = json.load(credentials_file)
        if 'user_name' in credentials and 'password' in credentials:
            token = rest_methods.authenticate(credentials['user_name'], credentials['password'])
            approved = rest_methods.get_integration_approved(credentials['user_name'], token)
            if approved:

                integration_id = rest_methods.get_integration_id(user_id=credentials['user_name'], token=token)
                engine_id = rest_methods.get_engine_id(integration_id=integration_id, token=token)
                device_agents = rest_methods.get_device_agents(engine_id=engine_id, token=token)
                if len(device_agents) == 0:
                    raise RuntimeError('No devices with Integration enabled')
                else:
                    with (open(event_data_path, 'r') as event_data_file,
                          open(object_data_path, 'r') as object_data_file
                          ):

                        events = json.load(event_data_file)
                        additional_data = {
                            "id": engine_id,
                            "timestampUs": int(time.time()),
                            "durationUs": 30000
                        }
                        event_data = additional_data | events
                        rest_methods.send_event(engine_id=engine_id,
                                                token=token,
                                                device_id=device_agents[0]['id'],
                                                event_data=event_data)

                        objects = json.load(object_data_file)
                        additional_data = {
                            "id": engine_id,
                            "timestampUs": int(time.time()),
                            "durationUs": 30000,
                        }
                        object_data = additional_data | objects
                        rest_methods.send_object(engine_id=engine_id,
                                                 token=token,
                                                 device_id=device_agents[0]['id'],
                                                 object_data=object_data)


            else:
                sys.stdout.write('Integration request is not approved yet')

        else:
            raise RuntimeError('Corrupted credentials file')

except OSError as e:
    if e.errno == 2:
        register_integration()
