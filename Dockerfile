FROM	ubuntu:12.10
RUN 	apt-get update
RUN 	DEBIAN_FRONTEND=noninteractive apt-get install -q -y python
RUN 	DEBIAN_FRONTEND=noninteractive apt-get install -q -y python-pip
RUN 	DEBIAN_FRONTEND=noninteractive apt-get install -q -y curl
RUN 	curl -L https://github.com/hedenberg/WebSync/archive/master.tar.gz | tar -xzv
RUN 	pip install flask
RUN 	pip install sqlalchemy
EXPOSE  5000
#RUN		pip install .

#https://github.com/hedenberg/WebSync.git
#RUN 	pip install flask
#RUN 	pip install sqlalchemy

#sudo docker build -t websync/ubuntu .
#docker run -d websync/ubuntu python WebSync-master/runserver.py
#docker rmi ...
#docker docker logs 742