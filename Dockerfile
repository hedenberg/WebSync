FROM	ubuntu:12.10
RUN 	apt-get update
RUN 	DEBIAN_FRONTEND=noninteractive apt-get install -q -y python
RUN 	DEBIAN_FRONTEND=noninteractive apt-get install -q -y python-pip
RUN 	DEBIAN_FRONTEND=noninteractive apt-get install -q -y curl
RUN 	curl -L https://github.com/hedenberg/WebSync/archive/master.tar.gz | tar -xzv
RUN 	pip install flask
RUN 	pip install sqlalchemy
