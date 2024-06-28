import json

# Assuming instances.json exists and contains valid JSON data
file_path = '/Users/altar/Desktop/rizzSim/games/datingsim/in/instances.json'

# Step 1: Read instances.json
with open(file_path, 'r') as file:
    data = json.load(file)

# Step 2: Modify the data (assuming data is structured as you described)
# For example, modifying some part of the data
# Assuming you have experiment["location"]["MAIN-ACTIONS"] ready to replace in data

# Example modification:
# data["some_key"] = some_value

# Step 3: Save back to instances.json with indentation
with open('/Users/altar/Desktop/rizzSim/games/datingsim/in/instances-readable.json', 'w') as file:
    json.dump(data, file, indent=4)
