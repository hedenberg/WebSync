WebSync
=======

Distributed File Synchronization Service as a lab in the course D7024E

For more information, see https://sites.google.com/site/d7024eboxdrop

## Setup and Testing

1) Make sure you have Vagrant 1.3.1 or greater and Virtualbox 4.0 or greater.

2) Clone this git

3) Start vagrant

```
vagrant up
vagrant ssh
```

4) Unfortunately you need to start by installing some things

```
sudo apt-get install python-pip
cd /vagrant/
sudo pip install -r requirements.txt
# ignore warnings, they’re there to make you feel special.
```
```
sudo apt-get update
sudo apt-get install linux-image-extra-`uname -r`

sudo sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
sudo sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"

sudo apt-get update
sudo apt-get install lxc-docker
```

5) Create the base docker-image 

```
sudo docker build -t websync .
# Wait a very long time. I recommend coffee.
```

6) You can now run the manager

```
python runmanager.py [Port, 8000 if left empty]
```

7) Open your favorit browser and visit localhost:[Port]

Remember to create nodes at 10.10.10.15 if you are behind a firewall. 
The nodes are currently started at offline-state. Change it by pressing “Go Online”.

The application assume that our OpenStack server is still active and that our RabbitMQ server is running on it. If these go down: On OpenStack; install and run RabbitMQ-server on an ubuntu server change the IP-address used in the manager and websync rabbitmq-files. Create a coreos image. Run docker build on a it and save as a snapshot for OpenStack to use (this means changing the ami’s in the openstack python file. Update the EC2-endpoint IP address to the new OpenStack address.
