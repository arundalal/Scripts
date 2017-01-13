#!/usr/bin/python
#####Importing Libraries######
import subprocess
import json
import xlwt
from array import *

#######Setting Up Variable

a = 0
INS_COUNT = array('i',[0,0,0])
ENV_LIST = ["PROD", "PREPROD", "QADEV"];

for ENV in ENV_LIST:
    AWS_PROFILE = ENV

    ######Loading AWS IDS########
    # INS_ID_DATA = subprocess.Popen(["aws", "ec2", "describe-instances", "--query", "Reservations[*].Instances[*].[InstanceId]", "--output", "text", "--profile", AWS_PROFILE], stdout=subprocess.PIPE).stdout.readlines()
    INS_DATA = subprocess.Popen(["aws", "ec2", "describe-instances", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
    TEMP_INS_DATA = json.loads(INS_DATA.stdout.read())
    AWS_INS_DATA = TEMP_INS_DATA['Reservations']
    # VPC_ID_DATA = subprocess.Popen(["aws", "ec2", "describe-vpcs", "--query", "Vpcs[*].[VpcId]", "--output", "text", "--profile", AWS_PROFILE], stdout=subprocess.PIPE).stdout.readlines()
    VPC_DATA = subprocess.Popen(["aws", "ec2", "describe-vpcs", "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
    TEMP_VPC_DATA = json.loads(VPC_DATA.stdout.read())
    AWS_VPC_DATA = TEMP_VPC_DATA['Vpcs']
    # SUBNET_ID_DATA = subprocess.Popen(["aws", "ec2", "describe-subnets", "--query", "Subnets[*].[SubnetId]", "--output", "text", "--profile", AWS_PROFILE], stdout=subprocess.PIPE).stdout.readlines()
    SUBNET_DATA = subprocess.Popen(["aws", "ec2", "describe-subnets", "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
    TEMP_SUBNET_DATA = json.loads(SUBNET_DATA.stdout.read())
    AWS_SUBNET_DATA = TEMP_SUBNET_DATA['Subnets']
    EIP_INS_ID_DATA =  subprocess.Popen(["aws", "ec2", "describe-addresses", "--query", "Addresses[*].[InstanceId]", "--output", "text", "--profile", AWS_PROFILE], stdout=subprocess.PIPE).stdout.readlines()
    SEC_GP_DATA = subprocess.Popen(["aws", "ec2", "describe-security-groups", "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
    AWS_SEC_GP_DATA =  json.loads(SEC_GP_DATA.stdout.read())
    SECURITY_GROUPS = AWS_SEC_GP_DATA['SecurityGroups']
    INS_COUNTER = 0
    i = 0
    j = 0
    k =0
    ######Creating Initial WorkBooks####
    book = xlwt.Workbook(encoding="utf-8")
    style = xlwt.easyxf('font: bold 1')
    sheet1 = book.add_sheet("EC2")
    sheet2 = book.add_sheet("VPC")
    sheet3 = book.add_sheet("Sec GP")
    sheet1.col(0).width = 256 * 32
    sheet1.col(1).width = 256 * 15
    sheet1.col(2).width = 256 * 15
    sheet1.col(3).width = 256 * 15
    sheet1.col(4).width = 256 * 16
    sheet1.col(5).width = 256 * 14
    sheet1.col(6).width = 256 * 25
    sheet1.col(7).width = 256 * 23
    sheet1.col(8).width = 256 * 32

    sheet2.col(0).width = 256 * 18
    sheet2.col(1).width = 256 * 13
    sheet2.col(2).width = 256 * 15
    sheet2.col(3).width = 256 * 30
    sheet2.col(4).width = 256 * 16
    sheet2.col(5).width = 256 * 16
    sheet2.col(6).width = 256 * 12

    sheet3.col(0).width = 256 * 23
    sheet3.col(1).width = 256 * 18
    sheet3.col(2).width = 256 * 20
    sheet3.col(3).width = 256 * 15
    sheet3.col(4).width = 256 * 17
    sheet3.col(5).width = 256 * 12
    sheet3.col(6).width = 256 * 9
    sheet3.col(7).width = 256 * 17
    sheet3.col(8).width = 256 * 12
    sheet3.col(9).width = 256 * 9

    sheet1.write(0, 0, "Instance Name", style)
    sheet1.write(0, 1, "Instance ID", style)
    sheet1.write(0, 2, "Instance State", style)
    sheet1.write(0, 3, "Private IP", style)
    sheet1.write(0, 4, "Elastic IP", style)
    sheet1.write(0, 5, "Instance Type", style)
    sheet1.write(0, 6, "Instance Security GP", style)
    sheet1.write(0, 7, "Instance VPC NAME", style)
    sheet1.write(0, 8, "Instance Subnet NAME", style)

    sheet2.write(0, 0, "VPC Name", style)
    sheet2.write(0, 1, "VPC ID", style)
    sheet2.write(0, 2, "VPC CIDR Block", style)
    sheet2.write(0, 3, "Subnet Name", style)
    sheet2.write(0, 4, "Subnet ID", style)
    sheet2.write(0, 5, "Subnet CIDR Block", style)
    sheet2.write(0, 6, "Subnet A-Z", style)

    sheet3.write(0, 0, "Security Group Name", style)
    sheet3.write(0, 1, "Security Group ID", style)
    sheet3.write(0, 2, "Security Group VPC", style)
    sheet3.write(0, 3, "Sec Gp VPC ID", style)
    sheet3.write(0, 4, "Inbound Source", style)
    sheet3.write(0, 5, "Inbound Port", style)
    sheet3.write(0, 6, "Protocol", style)
    sheet3.write(0, 7, "Egress Source", style)
    sheet3.write(0, 8, "Egress Port", style)
    sheet3.write(0, 9, "Protocol", style)

    #######Fetching EC2 Instances Data#########
    for DATA_RES in AWS_INS_DATA:
        DATA_INS = DATA_RES['Instances']
        for DATA in DATA_INS:
            INS_ID = DATA['InstanceId']
            print "ins id", INS_ID
            AWS_INS_STATE = DATA['State']
            INS_STATE = AWS_INS_STATE['Name']
            if INS_STATE == "running":
                INS_COUNTER = INS_COUNTER + 1

            try:
                INS_TAGS = DATA['Tags']
                for I in INS_TAGS:
                    X = I['Key']
                    if X == "Name":
                        INS_NAME = I['Value']
            except KeyError:
                INS_NAME = "NONE"
            try:
                INS_PRI_IP = DATA['PrivateIpAddress']
            except KeyError:
                INS_PRI_IP = "NONE"

            INS_TYPE = DATA['InstanceType']
            try:
                INS_SEC_GP = DATA['NetworkInterfaces'][0]['Groups'][0]['GroupName']
            except KeyError:
                INS_SEC_GP = "NONE"

            ##Getting VPC value for Instance##
            try:
                INS_VPC_ID  = DATA['VpcId']

                for DATA_VPC in AWS_VPC_DATA:
                    AWS_VPC_ID = DATA_VPC['VpcId']
                    if AWS_VPC_ID == INS_VPC_ID:
                        VPC_TAGS = DATA_VPC['Tags']
                        for I in VPC_TAGS:
                            X = I['Key']
                            if X == 'Name':
                                INS_VPC_NAME = I['Value']
            except KeyError:
                INS_VPC_ID = "NONE"
            ##Getting Subnet value for Instance##
            try:
                INS_SUBNET_ID = DATA['SubnetId']
                print "INS_SUBNET ID", INS_SUBNET_ID
                for DATA in AWS_SUBNET_DATA:
                    AWS_SUBNET_ID = DATA['SubnetId']
                    if AWS_SUBNET_ID.rstrip() == INS_SUBNET_ID.rstrip():

                        try:
                            SUBNET_TAGS = DATA['Tags']
                            for I in SUBNET_TAGS:
                                    X = I['Key']
                                    if X == 'Name':
                                        INS_SUBNET_NAME = I['Value']
                        except KeyError:
                            INS_SUBNET_NAME = "NONE"

            except KeyError:

                INS_SUBNET_NAME = "NONE-Notfind"
            print "subnet name", INS_SUBNET_NAME
            #####Elatic IP for Instance#####
            INS_EIP = '  '
            m = 0
            for EIP_INS_ID in EIP_INS_ID_DATA:
                if INS_ID.rstrip() == EIP_INS_ID.rstrip():
                    EIP_DATA = subprocess.Popen(["aws", "ec2", "describe-addresses", "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
                    AWS_EIP_DATA = json.loads(EIP_DATA.stdout.read())
                    INS_EIP = AWS_EIP_DATA['Addresses'][m]['PublicIp']
                m = m + 1
            # if INS_ID.rstrip() in EIP_INS_ID_DATA:
            #     EIP_NO = EIP_INS_ID_DATA.index(INS_ID)
            #     EIP_DATA = subprocess.Popen(["aws", "ec2", "describe-addresses", "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
            #     AWS_EIP_DATA = json.loads(EIP_DATA.stdout.read())
            #     INS_EIP = AWS_EIP_DATA['Addresses'][EIP_NO]['PublicIp']



            i = i + 1
            sheet1.write(i, 0, INS_NAME)
            sheet1.write(i, 1, INS_ID)
            sheet1.write(i, 2, INS_STATE)
            sheet1.write(i, 3, INS_PRI_IP)
            sheet1.write(i, 4, INS_EIP)
            sheet1.write(i, 5, INS_TYPE)
            sheet1.write(i, 6, INS_SEC_GP)
            sheet1.write(i, 7, INS_VPC_NAME)
            sheet1.write(i, 8, INS_SUBNET_NAME)
            book.save("Bancbox_AWS_%s.xls" %AWS_PROFILE)
    print "total instance", INS_COUNTER


    print "Ec2 Data Complete"
    ###################################
    ###VPC Data Parsing####
    for DATA in AWS_VPC_DATA:
            # VPC_DATA = subprocess.Popen(["aws", "ec2", "describe-vpcs", "--vpc-ids", VPC_ID.rstrip(), "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
            # AWS_VPC_DATA = json.loads(VPC_DATA.stdout.read())
            VPC_TAGS = DATA['Tags']
            VPC_ID = DATA['VpcId']
            for I in VPC_TAGS:
                X = I['Key']
                if X == 'Name':
                    VPC_NAME = I['Value']
            VPC_CIDR = DATA['CidrBlock']
            j = j + 1
            sheet2.write(j, 0, VPC_NAME)
            sheet2.write(j, 1, VPC_ID)
            sheet2.write(j, 2, VPC_CIDR)
            J = j
            for DATA in AWS_SUBNET_DATA:
                # SUBNET_DATA = subprocess.Popen(["aws", "ec2", "describe-subnets", "--subnet-ids", SUBNET_ID.rstrip(), "--output", "json", "--profile", AWS_PROFILE], stdout=subprocess.PIPE)
                # AWS_SUBNET_DATA = json.loads(SUBNET_DATA.stdout.read())
                SUBNET_VPC_ID = DATA['VpcId']
                if VPC_ID.rstrip() == SUBNET_VPC_ID.rstrip():
                    try:
                        SUBNET_TAGS = DATA['Tags']
                        for I in SUBNET_TAGS:
                            X = I['Key']
                            if X == 'Name':
                                SUBNET_NAME = I['Value']
                    except KeyError:
                        INS_SUBNET_NAME = "NONE"
                    SUBNET_ID = DATA['SubnetId']
                    SUBNET_CIDR_BLOCK = DATA['CidrBlock']
                    SUBNET_AZ = DATA['AvailabilityZone']

                    sheet2.write(J, 3, SUBNET_NAME)
                    sheet2.write(J, 4, SUBNET_ID)
                    sheet2.write(J, 5, SUBNET_CIDR_BLOCK)
                    sheet2.write(J, 6, SUBNET_AZ)
                    J = J + 1
                    book.save("Bancbox_AWS_%s.xls" %AWS_PROFILE)
            j = J

    #######Security Group Data#########
    for K in SECURITY_GROUPS:
        SEC_GP_NAME = K['GroupName']
        SEC_GP_ID = K['GroupId']
        a = ['AWS', 'default']
        if any(x in SEC_GP_NAME for x in a):
            continue
        else:
              SEC_VPC_ID = K['VpcId']
              for DATA in AWS_VPC_DATA:
                AWS_VPC_ID = DATA['VpcId']
                if AWS_VPC_ID == SEC_VPC_ID:
                    VPC_TAGS = DATA['Tags']
                    for I in VPC_TAGS:
                        X = I['Key']
                        if X == 'Name':
                            SEC_VPC_NAME = I['Value']
                   # print "Sec gp name: ", SEC_GP_NAME
              k = k+1
              sheet3.write(k, 0, SEC_GP_NAME)
              sheet3.write(k, 1, SEC_GP_ID)
              sheet3.write(k, 2, SEC_VPC_NAME)
              sheet3.write(k, 3, SEC_VPC_ID)
              l = k
              m = k
              SEC_IN = K['IpPermissions']
              SEC_OUT = K['IpPermissionsEgress']
              for L in SEC_IN:
                  SEC_IN_PORT = L.get('ToPort')
                  SEC_IN_PROTOCOL = L['IpProtocol']
                  IP_RANGE = L['IpRanges']
                  for O in IP_RANGE:
                      SEC_IN_CIDRIP = O['CidrIp']
                      sheet3.write(l, 4, SEC_IN_CIDRIP)
                      sheet3.write(l, 5, SEC_IN_PORT)
                      sheet3.write(l, 6, SEC_IN_PROTOCOL)
                      l = l + 1
                      book.save("Bancbox_AWS_%s.xls" %AWS_PROFILE)
              for M in SEC_OUT:
                  SEC_OUT_PORT = M.get('ToPort')
                  SEC_OUT_PROTOCOL = M['IpProtocol']
                  IP_RANGE = M['IpRanges']
                  for O in IP_RANGE:
                      SEC_OUT_CIDRIP = O['CidrIp']
                      sheet3.write(m, 7, SEC_OUT_CIDRIP)
                      sheet3.write(m, 8, SEC_OUT_PORT)
                      sheet3.write(m, 9, SEC_OUT_PROTOCOL)
                      m = m + 1
                      book.save("Bancbox_AWS_%s.xls" %AWS_PROFILE)
              if m > l:
                  k = m
              else:
                  k = l

###############################
import smtplib
import base64
# Found most ofthis at http://ryrobes.com/python/python-snippet-sending-html-email-with-an-attachment-via-google-apps-smtp-or-gmail/
# Adapted to accept a list of files for multiple file attachments
# From other stuff I googled, a little more elegant way of converting html to plain text
# This works in 2.7 and my brain gets it.

######### Setup your stuff here #######################################

attachments = ['Bancbox_AWS_PROD.xls', 'Bancbox_AWS_PREPROD.xls', 'Bancbox_AWS_QADEV.xls']

# username = 'joe@gmail.com'
# password = 'j0ej0e'
host = 'localhost' # specify port, if required, using this notations

fromaddr = 'NetOps@localhost' # must be a vaild 'from' address in your GApps account
toaddr  = 'netops-team@finxera.com'
replyto = fromaddr # unless you want a different reply-to

msgsubject = 'Finxera AWS Accounts Inventory'

htmlmsgtext = """<h2>Hey!!! Finxerians</h2>
                <p>\
                 This is an automated generated report of Finxera AWS Accounts Inventory.\
                 Please find the detailed inventory in the files Attached.\n

                 </p>

                """
# """ %(INS_COUNT[0],INS_COUNT[1],INS_COUNT[2])

######### In normal use nothing changes below this line ###############

import smtplib, os, sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from HTMLParser import HTMLParser

# A snippet - class to strip HTML tags for the text version of the email

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

########################################################################

try:
    # Make text version from HTML - First convert tags that produce a line break to carriage returns
    msgtext = htmlmsgtext.replace('</br>',"\r").replace('<br />',"\r").replace('</p>',"\r")
    # Then strip all the other tags out
    msgtext = strip_tags(msgtext)

    # necessary mimey stuff
    msg = MIMEMultipart()
    msg.preamble = 'This is a multi-part message in MIME format.\n'
    msg.epilogue = ''

    body = MIMEMultipart('alternative')
    body.attach(MIMEText(msgtext))
    body.attach(MIMEText(htmlmsgtext, 'html'))
    msg.attach(body)

    if 'attachments' in globals() and len('attachments') > 0: # are there attachments?
        for filename in attachments:
            f = filename
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

    msg.add_header('From', fromaddr)
    msg.add_header('To', toaddr)
    msg.add_header('Subject', msgsubject)
    msg.add_header('Reply-To', replyto)

    # The actual email sendy bits
    server = smtplib.SMTP(host)
    server.set_debuglevel(False) # set to True for verbose output
    try:
        # gmail expect tls
        # server.starttls()
        # server.login(username,password)
        # server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server = smtplib.SMTP('localhost')
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print 'Email sent'
        server.quit() # bye bye
    except:
        # if tls is set for non-tls servers you would have raised an exception, so....
        server.login(username,password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print 'Email sent'
        server.quit() # sbye bye
except:
    print ('Email NOT sent to %s successfully. %s ERR: %s %s %s ', str(toaddr), 'tete', str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2]) )
    #just in case