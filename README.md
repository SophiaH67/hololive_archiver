# hololive_archiver
Automatically archives hololive karaoke streams

## Setup (docker)
### Docker run (recommended)

To run the archiver, run
```bash
docker run -it -d \
    --name "hololive_archiver" \
    --restart=unless-stopped \
    --network bridge \
    -v /path/to/downloads/:/downloads/ \
    -v /path/to/config.yaml:/app/config.yaml \
    marnixah/hololive_archiver:latest
```

### Docker compose
```bash
git clone https://github.com/marnixah/hololive_archiver.git
cd hololive_archiver
```
Change the docker-compose file to match your directories, then run
```
docker-compose up -d
```
## Setup (ubuntu)
!! THIS IS UNSUPPORTED !!

To run the archiver, run the following
```bash
git clone https://github.com/marnixah/hololive_archiver.git
cd hololive_archiver
pip3 install -r requirements.txt
python3 main.py
```
## Configuration
In order to configure this, just edit config.yaml. An example is provided in this repository