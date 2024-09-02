import os
import json

config_file_name = "modify_vault_config.json"

# Check if the configuration file exists
if not os.path.exists(config_file_name):
    print(f"Configuration file '{config_file_name}' does not exist.")
    exit(1)

# Load configuration file
try:
    with open(config_file_name, 'r') as config_file:
        config_data = json.load(config_file)
except Exception as e:
    print(f"Failed to read configuration file '{config_file_name}': {e}")
    exit(1)

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Check if 'run.bat' exists in the current directory
bat_file_exists = os.path.exists(os.path.join(current_dir, 'run.bat'))

# Iterate through each file configuration
for file_config in config_data['files']:
    full_path = file_config['full_path']
    relative_path = os.path.join(current_dir, file_config['relative_path'].replace('/', os.sep))

    # Determine the file path to use based on the existence of 'run.bat'
    file_path = relative_path if bat_file_exists else full_path

    # Read the JSON file
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Failed to read JSON file '{file_path}': {e}")
        continue

    # Apply modifications
    for modification in file_config['modifications']:
        keys = modification['path']
        value = modification['value']

        print(f"Applying modification: {modification}")

        # Navigate to the target key
        obj = data
        try:
            for i, key in enumerate(keys):
                if i == len(keys) - 1:
                    # We're at the last key, so apply the modification
                    if 'match' in modification and 'key_to_modify' in modification:
                        # Ensure we have a list for matching
                        if not isinstance(obj[key], list):
                            raise KeyError(f"Expected a list at path {keys[:-1]} but got {type(obj[key]).__name__}")
                        
                        match_key = list(modification['match'].keys())[0]
                        match_value = modification['match'][match_key]
                        found = False

                        for item in obj[key]:
                            if item.get(match_key) == match_value:
                                item[modification['key_to_modify']] = value
                                found = True
                                break

                        if not found:
                            raise KeyError(f"No matching item found for match criteria {modification['match']} in path {keys}")
                    else:
                        # Direct modification
                        obj[key] = value

                else:
                    # Navigate deeper into the JSON structure
                    obj = obj[key]

        except Exception as e:
            print(f"Failed to apply modification {modification} on file '{file_path}': {e}")
            continue

    # Write the modified JSON content back to the file
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Modified the file: {file_path}")
    except Exception as e:
        print(f"Failed to write JSON file '{file_path}': {e}")