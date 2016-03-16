#!/bin/bash

# DB Refresh Script
# Copyright (C) 2013 Finxera - All Rights Reserved
# Permission to copy and modify is NOT granted !
# Created On 1 May 2015
# Author Arun Dalal <arun@bancbox.com>
# Team Network Operations(TL:Amit(amit@finxera.com)

#Commands



#Parameters
RDS_INSTANCE_ID="regressiondb"
RDS_SNAPSHOT_ID="NULL"
MASTER_PROFILE="PREPROD"
SLAVE_PROFILE="QADEV"
MASTER_RDS="masterRDSbbx"
MASTER_DB_SIZE="db.m3.xlarge"
MASTER_SUBNET_GP="db-regressionprivatesg"
WORK_DIR="/db_dump"
DEFAULT_SETUP_DIR="/usr/local/BBX_DB_DUMP"
INSTANCE_ID="i-c67df93a"
USER_ID_1="862389706708"
USER_ID_2="530674835197"
#Credentials
MASTER_USER="cftdba"
MASTER_PASS="Leopard123"
MASTER_DB="cp20"

#VARIABLES
WAIT_TIME=0
MSG=""


#Functions

function GETLATESTSNAPSHOTID {

RDS_SNAPSHOT_ID=$(aws rds describe-db-snapshots --db-instance-identifier $1 --snapshot-type automated  --query 'DBSnapshots[*].DBSnapshotIdentifier' --profile $2 --output text | awk '{ print $NF }')

}

function RESTOREDBFROMSNAPSHOT {

aws rds restore-db-instance-from-db-snapshot --db-instance-identifier $1 --db-snapshot-identifier $2  --db-instance-class $2 --db-subnet-group-name $4 --no-multi-az --no-publicly-accessible --profile $5
 
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

function MODIFYDBINSTANCE{
aws rds modify-db-instance --db-instance-identifier $1 --master-user-password $2  --db-parameter-group-name $3  --apply-immediately true --profile $4
}

function PARAMAPPLYSTATUS{
	INS_STATUS=$(aws rds describe-db-instances --db-instance-identifier $1 --query DBInstances[*].DBParameterGroups[*].ParameterApplyStatus --profile $2 --output text)
	if [ $INS_STATUS != "pending-reboot" ]; then
		WAIT_TIME=$[$WAIT_TIME+5]
        sleep 5 
        PARAMAPPLYSTATUS "$1" "$2"
    else
    	echo "Paramater Group Applied "
		echo "Took $WAIT_TIME seconds for $1 "
        sleep 60		
		WAIT_TIME=0 

	fi
}

function REBOOTDB{
aws rds reboot-db-instance  --db-instance-identifier $1 --profile $2
}

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

##Script Execution

GETLATESTSNAPSHOTID "$RDS_INSTANCE_ID" "$MASTER_PROFILE"

echo $RDS_SNAPSHOT_ID

RESTOREDBFROMSNAPSHOT "$MASTER_RDS" "$RDS_SNAPSHOT_ID" "MASTER_DB_SIZE" "$MASTER_SUBNET_GP" "MASTER_PROFILE"

INSTANCEREADYWAIT "$MASTER_RDS" "$MASTER_PROFILE"

MODIFYDBINSTANCE "$MASTER_RDS"  "$MASTER_PASS" "$MASTER_PARAM_GP" "$MASTER_PROFILE"

PARAMAPPLYSTATUS "$MASTER_RDS" "$MASTER_PROFILE"

REBOOTDB "$MASTER_RDS" "$MASTER_PROFILE"

INSTANCEREADYWAIT "$MASTER_RDS" "$MASTER_PROFILE"

MASTER_DB_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier $MASTER_RDS --query DBInstances[*].Endpoint[].Address --profile $MASTER_PROFILE --output text)

echo "INSTANCE IS READY TO BE SCRUBBED"

## EBS VOL SETUP
INS_AZ=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query Reservations[*].Instances[].Placement[].AvailabilityZone --profile $MASTER_PROFILE --output text)
VOLUME_ID=$(aws ec2 create-volume --size 500 --availability-zone $INS_AZ --profile $MASTER_PROFILE | grep VolumeId | cut -d'"' -f4)
VOLUMEREADYWAIT $VOLUME_ID $MASTER_PROFILE
aws ec2 attach-volume --volume-id $VOLUME_ID --instance $INSTANCE_ID --device /dev/sdj --profile $MASTER_PROFILE
VOLUMEREADYWAIT $VOLUME_ID $MASTER_PROFILE
VOLUME_NAME=$(lsblk | tail -1 | cut -d' ' -f1)
mkfs -t ext4 /dev/$VOLUME_NAME
mkdir $WORK_DIR
mount /dev/$VOLUME_NAME $WORK_DIR

####
cd $WORK_DIR
cp -rf $DEFAULT_SETUP_DIR/* . 
###SCRUBBING&Dumping###

mysql -h $MASTER_DB_ENDPOINT -u $MASTER_USER -p"$MASTER_PASS" $MASTER_DB < Scrubbing.sql
echo "Scrubbing Complete"
sh dump_nodata.sh $MASTER_USER  $MASTER_DB_ENDPOINT $MASTER_PASS
sh dumper.sh $MASTER_USER  $MASTER_DB_ENDPOINT $MASTER_PASS
echo "DB DUMP Complete"
mysqldump -u $MASTER_USER -h $MASTER_DB_ENDPOINT -p$MASTER_PASS $MASTER_DB users > cp20_users.sql
sh proc_dump.sh $MASTER_USER  $MASTER_DB_ENDPOINT $MASTER_PASS  
sh update_definer.sh

sleep 30

#########SnapShot Creation######

SNAPSHOT_ID=$(aws ec2 create-snapshot --volume-id $VOLUME_ID --description "This is DB Backup." --profile $MASTER_PROFILE | grep SnapshotId | cut -d'"' -f4)

SNAPSHOTREADYWAIT $SNAPSHOT_ID $MASTER_PROFILE

aws ec2 modify-snapshot-attribute  --snapshot-id $SNAPSHOT_ID --attribute  createVolumePermission --user-ids $USER_ID_1  --create-volume-permission "{\"Add\":[{\"UserId\":\"$USER_ID_1\"}]}" --profile $MASTER_PROFILE
#aws ec2 modify-snapshot-attribute  --snapshot-id $SNAPSHOT_ID --attribute  createVolumePermission --user-ids $USER_ID_2  --create-volume-permission "{\"Add\":[{\"UserId\":\"$USER_ID_2\"}]}" --profile $MASTER_PROFILE

#######Delete all Cost increasing Items####
##Database
aws rds delete-db-instance --db-instance-identifier $MASTER_RDS --skip-final-snapshot --profile $MASTER_PROFILE
##VOLUME
umount /dev/$VOLUME_NAME
rm -rf $WORK_DIR
aws ec2 detach-volume --volume-id $VOLUME_ID  --profile $MASTER_PROFILE
VOLUMEREADYWAIT $VOLUME_ID $MASTER_PROFILE
aws ec2  delete-volume --volume-id $VOLUME_ID  --profile $MASTER_PROFILE
