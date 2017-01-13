import boto3
import xlwt
import boto3.session

acc_list = ["default","qadev"];
for acc in acc_list:
    aws_profile = acc

    #####################
    sheet_name = ["EC2","VPC","Sec_GP"]
    
    sheet_list = [["Instance Name","Instance ID","Instance State","Private IP","Elastic IP","Instance Type","Instance Security GP","Instance VPC NAME","Instance Subnet NAME"], ["VPC Name","VPC ID","VPC CIDR Block","Subnet Name","Subnet ID","Subnet CIDR Block","Subnet A-Z"], ["Security Group Name","Security Group ID","Security Group VPC","Sec Gp VPC ID","Inbound Source","Inbound Port","Protocol","Egress Source","Egress Port Protocol"]]
    
######Creating Initial WorkBooks####
    book = xlwt.Workbook(encoding="utf-8")
    style = xlwt.easyxf('font: bold 1')
    for name in sheet_name:
        book.add_sheet(name)
    for i, value in enumerate(sheet_list):
        sheet = book.get_sheet(i)
        for j, name in enumerate(value):
            row_counter = 0
            sheet.col(j).width = 256 * len(name)
            sheet.write(row_counter, j, name, style)
        session = boto3.session.Session(profile_name=aws_profile)
        ec2 = session.resource('ec2')
        for instance in ec2.instances.all():
            
            for i in instance.tags:
                data_list = []
                if i['Key'] == 'Name':
                    INS_NAME = i['Value']
                    data_list.append(INS_NAME)
            INS_ID = instance.id
            data_list.append(INS_ID)
            INS_STATE = instance.state['Name']
            data_list.append(INS_STATE)
            INS_PRI_IP = instance.private_ip_address
            data_list.append(INS_PRI_IP)
            INS_EIP = instance.public_ip_address
            data_list.append(INS_EIP)
            INS_TYPE = instance.instance_type
            data_list.append(INS_TYPE)
            security_group = ec2.SecurityGroup(instance.security_groups[0]['GroupId'])
            for i in security_group.tags:
                if i['Key'] == 'Name':
                    INS_SEC_GP = i['Value']
            vpc = ec2.Vpc(instance.vpc_id)
            for i in vpc.tags:
                if i['Key'] == "Name":
                    INS_VPC_NAME = i['Value']
            subnet = ec2.Subnet(instance.subnet_id)
            for i in subnet.tags:
                if i['Key'] == "Name":
                    INS_SUBNET_NAME = i['Value']
            row_counter = row_counter + 1
            for j, name in enumerate(data_list):
                sheet.write(row_counter, j, name)
            book.save("Inventory_AWS_%s.xls" %aws_profile)
        
            
            print INS_NAME
            print INS_ID
            print INS_STATE
            print INS_PRI_IP 
            print INS_EIP
            print INS_TYPE
            print INS_SEC_GP
            print INS_VPC_NAME
            print INS_SUBNET_NAME
