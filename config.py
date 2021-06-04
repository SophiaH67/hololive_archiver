from yaml import safe_load, YAMLError
with open("config.yaml", 'r') as stream:
  try:
    tmp_config = safe_load(stream)
  except YAMLError as exc:
    print("invalid config")
    raise exc

categories = tmp_config['categories']

locations = {
  "tmp": tmp_config['locations']['tmp'],
  "final": tmp_config['locations']['final']
}

streams = []

def add_stream(target):
  streams.append(target)