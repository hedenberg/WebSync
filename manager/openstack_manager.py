import boto, os, sys
import boto.ec2
import time
#import config

COREOS_OCT22 =  "ami-00000025"
COREOS_OCT23 =  "ami-00000031"
#COREOS_IMAGE = "ami-00000003"
#COREOS_SNAP = "ami-0000001d"
#COREOS_CONT = "ami-0000001e"
#COREOS_IMAGE = "56eed2c2-40b6-4a52-bd55-823457f0ee66"
EC2_ENDPOINT = "130.240.233.106"
EC2_ACCESS_KEY="58433a1650b14ac2a62a9ad06b9cf1c9"
EC2_SECRET_KEY="2fa63408610b427a8e5a080126d70e0e"

boto_region = boto.ec2.regioninfo.RegionInfo(name="nova", endpoint=EC2_ENDPOINT)
boto_connection = boto.connect_ec2(
    aws_access_key_id=EC2_ACCESS_KEY,
    aws_secret_access_key=EC2_SECRET_KEY,
    is_secure=False,
    region=boto_region,
    port=8773,
    path="/services/Cloud")

def add_instance():
    try:
        response = boto_connection.run_instances(
            #image_id="56eed2c2-40b6-4a52-bd55-823457f0ee66",
            #COREOS_CONT, 
            COREOS_OCT23,
            key_name="web_sync2", 
            instance_type="m1.tiny", 
            security_groups=["default"]
            #min_count=instances_count,
            #max_count=instances_count
        )

        for instance in response.instances:                         #waiting for the instance to ge an ip
            while instance.private_ip_address == "":
                instance.update()
        inst = response.instances[0]
        return inst



    except Exception as e:
        raise e
        #print "Exception when creating node: "+ str(e) 


def remove_instance(instance,ip):                                #removes the instance provided
    instances = [instance]
    if (boto_connection.disassociate_address(ip)):                  #disassociate ip from instance before removing to avoid errors
        boto_connection.terminate_instances(instances)
        boto_connection.release_address(ip)
        #return "vm at "+ ip +" removed"
    #boto_connection.terminate_instances(instances)
    #time.sleep(1)                                                    #sleep because instance needs to be terminated before ip is removed
    #ip = (str(addr).split(":"))[1]
    #boto_connection.release_address(ip)
    #return "something went wrong when removing vm.. :<"

def get_floating():
    addr = boto_connection.allocate_address()
    return (str(addr).split(":"))[1]


def assign_floating(instance, ip):
    boto_connection.associate_address(instance,ip)


