from ffmpeg import probe, Error
from pathlib import Path

def generate_documentation(filepath: str):
  try:
    input_video = probe(filepath)
  except Error as err:
    print(10*'-')
    print("ffprobe exception!")
    print(err.stderr)
    print(err.stdout)
    print(10*'-')
    return ""
  documentation_array = []
  documentation_array.append(f"# {Path(filepath).stem}")
  documentation_array.append(f"## Streams")
  for stream in input_video["streams"]:
    documentation_array.append(f"### Stream {stream['index']} ({stream['codec_type']})")
    documentation_array.append("```") # codeblock for codec
    documentation_array.append(f"Codec: {stream['codec_name']}")

    if stream['codec_type'] == 'audio':
      documentation_array.append(f"Channels: {stream['channels']}")
      documentation_array.append(f"Channel layout: {stream['channel_layout']}")
      documentation_array.append(f"Sample rate: {stream['sample_rate']}")
    elif stream['codec_type'] == 'video':
      documentation_array.append(f"Resolution: {stream['width']}x{stream['height']} ({stream['display_aspect_ratio']})")
      documentation_array.append(f"Pixel format: {stream['pix_fmt']}")
      documentation_array.append(f"Color space: {stream['color_range']}")
      documentation_array.append(f"Duration: {stream['tags']['DURATION']}")

    documentation_array.append("```") # end codeblock
    
  return "\n".join(documentation_array)
      
if __name__ == '__main__':
  print(generate_documentation("./test.mkv"))