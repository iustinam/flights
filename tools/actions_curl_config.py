import json
import sys
import yaml

if len(sys.argv) != 2:
    print("Usage: python actions_curl_config.py <config_file.yaml|json>")
    sys.exit(1)

config_path = sys.argv[1]
if config_path.endswith('.yaml'):
    with open(config_path) as f:
        config = yaml.safe_load(f)
elif config_path.endswith('.json'):
    with open(config_path) as f:
        config = json.load(f)

github_action_inputs = {
    "ref": "main",
    "inputs": {
        "config_json": json.dumps(config)
    }
}
print(json.dumps(github_action_inputs))
