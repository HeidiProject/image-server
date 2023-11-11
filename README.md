# MX image server

Serves sample microscope images to Heidi for display in webpage.

## Getting started

## Docker

```bash
# build image
sudo docker build -t myimage .

# run image using a local image repository 
sudo docker run --log-driver=journald -d --volume /home/scratch/heidi/image_db:/images:ro --name mxims_container -p 3434:80 myimage

# run image using the real repository with https
sudo docker run --log-driver=journald -d --volume /sls/MX/applications/heidi/image_db:/images:ro --name mxims_container -p 8443:8443 myimage

# update docker to always restart this containrer upon reboot
sudo docker update --restart always mxims_container

# follow log messages from this container
sudo docker logs --follow mxims_container

# stop & remove container to be able to run a new image
sudo docker stop mxims_container
sudo docker rm mxims_container
```

## Docker-compose

```bash
# automatically build a new image
docker-compose build

# start the docker container with config
docker-compose up -d
```
