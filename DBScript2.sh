#!/bin/bash

# DB Refresh Script
# Copyright (C) 2013 Finxera - All Rights Reserved
# Permission to copy and modify is NOT granted !
# Created On 1 May 2015
# Author Arun Dalal <arun@bancbox.com>
# Team Network Operations(Team Lead:Amit(amit@finxera.com)
########
#Left for condition to be matched before further execution
#########
#Commands

#PARAMETERS
INSTANCE_ID="i-4d9468b0"
SNAPSHOT_ID=$(cat DB_SHARE_INFO.sh | cut -d"=" -f2 ) ##This Define parameter like SNAPSHOT_ID
SLAVE_PROFILE="QADEV"
WORK_DIR="/db_dump"

RDS_ENGINE_VERSION="5.6.19a"
RDS_PARAM_GP="qa-parametergroup"
SLAVE_RDS="slaveRDSbbx"
SLAVE_DB_SIZE="db.m3.xlarge"
SLAVE_DB_SUB_GP="db-qa-dbsubnetgroup"
SLAVE_DB_SEC_GP="sg-172ff273"
#Credentials
SLAVE_USER="cftdba"
SLAVE_PASS="Leopard123"
SLAVE_DB="cp20"


#VARIABLES


#Functions
function VOLUMEREADYWAIT { 
	VOL_STATUS=$(aws ec2 describe-volumes --volume-ids $1 --query Volumes[*].State --profile $2 --output text)  
	if [ $VOL_STATUS != "available" ] || [ $VOL_STATUS != "attached" ] ; then
		WAIT_TIME=$[$WAIT_TIME+10]
        sleep 10 
        VOLUMEREADYWAIT "$1" "$2"
    else
    	echo "Volume $1 is now $VOL_STATUS "
		echo "Took $WAIT_TIME seconds for $1 "
        sleep 30		
		WAIT_TIME=0 

	fi
}

function INSTANCEREADYWAIT { 
	INS_STATUS=$(aws rds describe-db-instances --db-instance-identifier $1 --query DBInstances[*].DBInstanceStatus --profile $2 --output text)  
	if [ $INS_STATUS != "available" ]; then
		WAIT_TIME=$[$WAIT_TIME+10]
        sleep 10 
        INSTANCEREADYWAIT "$1" "$2"
    else
    	echo "Instance $1 is now $INS_STATUS "
		echo "Took $WAIT_TIME seconds for $1 "
        sleep 60		
		WAIT_TIME=0 

	fi
}
function SNAPSHOTREADYWAIT { 
	SNAP_STATUS=$(aws ec2 describe-snapshots --snapshot-ids $1 --query Snapshots[*].State --output text --profile $2)  
	if [ $SNAP_STATUS != "completed" ]; then
		WAIT_TIME=$[$WAIT_TIME+30]
        sleep 30
        VOLUMEREADYWAIT "$1" "$2"
    else
    	echo "Snapshot $1 is now $SNAP_STATUS "
		echo "Took $WAIT_TIME seconds for $1 "
        sleep 30		
		WAIT_TIME=0 

	fi
}


#EXECUTION
##EBS VOLUME SETUP 

## EBS VOL SETUP
INS_AZ=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query Reservations[*].Instances[].Placement[].AvailabilityZone --profile $SLAVE_PROFILE --output text)
VOLUME_ID=$(aws ec2 create-volume --size 500 --snapshot-id $SNAPSHOT_ID --availability-zone $INS_AZ --profile $MASTER_PROFILE | grep VolumeId | cut -d'"' -f4)
VOLUMEREADYWAIT $VOLUME_ID $SLAVE_PROFILE
aws ec2 attach-volume --volume-id $VOLUME_ID --instance $INSTANCE_ID --device /dev/sdj --profile $SLAVE_PROFILE
VOLUMEREADYWAIT $VOLUME_ID $SLAVE_PROFILE
VOLUME_NAME=$(lsblk | tail -1 | cut -d' ' -f1)
mkfs -t ext4 /dev/$VOLUME_NAME
mkdir $WORK_DIR
mount /dev/$VOLUME_NAME $WORK_DIR

##RDS SETUP 
aws rds create-db-instance  --db-instance-identifier $SLAVE_RDS  --allocated-storage 500 --db-instance-class $SLAVE_DB_SIZE  --engine MySQL  --master-username $SLAVE_USER   --master-user-password $SLAVE_PASS --db-subnet-group-name "$SLAVE_DB_SUB_GP"  --vpc-security-group-ids  $SLAVE_DB_SEC_GP  --no-multi-az  --db-parameter-group-name $RDS_PARAM_GP --engine-version $RDS_ENGINE_VERSION --no-publicly-accessible  --profile $SLAVE_PROFILE

INSTANCEREADYWAIT "$SLAVE_RDS" "$SLAVE_PROFILE"

SLAVE_DB_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier $SLAVE_RDS --query DBInstances[*].Endpoint[].Address --profile $SLAVE_PROFILE --output text)

echo "INSTANCE IS READY TO BE Loaded with data"

####Loading the DB

cd $WORK_DIR
mysql -h $SLAVE_DB_ENDPOINT -u $SLAVE_USER -p"$SLAVE_PASS" << EOF
create database cp20;
create database cp20_star;
create database cp20_mig_staging;
create database invest;
create database percona;
create database test;
create database tmp;
EOF

sh load_schema.sh $SLAVE_USER $SLAVE_DB_ENDPOINT  $SLAVE_PASS
sh loader.sh $SLAVE_USER $SLAVE_DB_ENDPOINT  $SLAVE_PASS
mysql -u $SLAVE_USER -h $SLAVE_DB_ENDPOINT  -p"$SLAVE_PASS" < cp20_users.sql
sh proc_load.sh $SLAVE_USER $SLAVE_DB_ENDPOINT  $SLAVE_PASS

sleep 60

#####Create DB Snapshot####
DATE=$(date +"%Y%m%d")
aws rds create-db-snapshot --db-snapshot-identifier slaverds-$DATE --db-instance-identifier $SLAVE_RDS --profile $SLAVE_PROFILE

SNAPSHOTREADYWAIT slaverds-$DATE $SLAVE_PROFILE

#######Deleting
#######Delete all Cost increasing Items####
##Database
aws rds delete-db-instance --db-instance-identifier $SLAVE_RDS --skip-final-snapshot --profile $SLAVE_PROFILE
##VOLUME
umount /dev/$VOLUME_NAME
rm -rf $WORK_DIR
aws ec2 detach-volume --volume-id $VOLUME_ID  --profile $SLAVE_PROFILE
VOLUMEREADYWAIT $VOLUME_ID $SLAVE_PROFILE
aws ec2  delete-volume --volume-id $VOLUME_ID  --profile $SLAVE_PROFILE
echo "work completed"
