#!/bin/sh

USER=objectstore

echo 'Creating user: ${USER}'
adduser --disabled-password --gecos '' --uid 1000 ${USER} 
adduser ${USER} sudo
echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
chown -R ${USER}:${USER} /app/ 
chown -R ${USER}:${USER} /data/
exec su - ${USER}

