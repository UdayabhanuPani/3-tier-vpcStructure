
import boto3


class ClientLocator:
    def __init__(self, client):
        self._client = boto3.client(client, region_name="us-east-1")

    def get_client(self):
        return self._client


class EC2Client(ClientLocator):
    def __init__(self):
        super().__init__('ec2')



class VPC:
    def __init__(self, client):
        self._client = client
        """ :type : pyboto3.ec2 """


    def create_vpc(self):
        print('Creating a VPC...')
        return self._client.create_vpc(
            CidrBlock='10.0.0.0/16'
        )

    def add_name_tag(self, resource_id, resource_name):
        print('Adding ' + resource_name + ' tag to the ' + resource_id)
        return self._client.create_tags(
            Resources=[resource_id],
            Tags=[{
                'Key': 'Name',
                'Value': resource_name
            }]
        )

    def create_internet_gateway(self):
        print('Creating and Internet gateway')
        return self._client.create_internet_gateway()


    def attach_igw_to_vpc(self, vpc_id , igw_id):
        print('Attaching Internet Gateway' + igw_id + 'To VPC' + vpc_id)
        return self._client.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id

        )

    def create_subnet(self, vpc_id, cidr_block, region_name):
        print('Creating a Subnet for VPC'+ vpc_id + 'with Cidr block' + cidr_block)
        return self._client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr_block,
            AvailabilityZone=region_name

        )


    def create_public_route_table(self, vpc_id):
        print('Creating public Route Table for VPC ' + vpc_id)
        return self._client.create_route_table(VpcId=vpc_id)


    def create_igw_route_to_public_route_table(self, rtb_id, igw_id):
        print('Adding route for IGW ' + igw_id + ' to Route Table ' + rtb_id)
        return self._client.create_route(
            RouteTableId=rtb_id,
            GatewayId=igw_id,
            DestinationCidrBlock='0.0.0.0/0'
        )

    def associate_subnet_with_route_table(self, subnet_id, rtb_id):
        print('Associating subnet ' + subnet_id + ' with Route Table ' + rtb_id)
        return self._client.associate_route_table(
            SubnetId=subnet_id,
            RouteTableId=rtb_id
        )

    def allow_auto_assign_ip_addresses_for_subnet(self, subnet_id):
        return self._client.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )

    def create_nat_gateway(self, subnet_id, allocation_id):
        return self._client.create_nat_gateway(
            AllocationId=allocation_id,
            SubnetId=subnet_id
        )


def main():
    # Create a VPC
    ec2_client = EC2Client().get_client()
    vpc = VPC(ec2_client)

    vpc_response = vpc.create_vpc()

    print('VPC created:' + str(vpc_response))

    vpc_name = 'Boto3-VPC'
    vpc_id = vpc_response['Vpc']['VpcId']
    vpc.add_name_tag(vpc_id, vpc_name)

    igw_response = vpc.create_internet_gateway()


    igw_id = igw_response['InternetGateway']['InternetGatewayId']

    vpc.attach_igw_to_vpc(vpc_id, igw_id)

    public_subnet_response1 = vpc.create_subnet(vpc_id, '10.0.1.0/24', 'us-east-1a')

    public_subnet_id1 = public_subnet_response1['Subnet']['SubnetId']

    print('Subnet created for VPC ' + vpc_id + ':' + str(public_subnet_response1))

    public_subnet_response2 = vpc.create_subnet(vpc_id, '10.0.2.0/24', 'us-east-1b')

    public_subnet_id2 = public_subnet_response2['Subnet']['SubnetId']

    print('Subnet created for VPC ' + vpc_id + ':' + str(public_subnet_response2))

    private_subnet_response3 = vpc.create_subnet(vpc_id, '10.0.3.0/24', 'us-east-1a')
    private_subnet_id3 = private_subnet_response3['Subnet']['SubnetId']

    private_subnet_response4 = vpc.create_subnet(vpc_id, '10.0.4.0/24', 'us-east-1a')
    private_subnet_id4 = private_subnet_response4['Subnet']['SubnetId']

    vpc.add_name_tag(public_subnet_id1, 'Boto-3-Public-Subnet-1')
    vpc.add_name_tag(public_subnet_id2, 'Boto-3-Public-Subnet-2')
    vpc.add_name_tag(private_subnet_id3, 'Boto-3-Private-Subnet-3')
    vpc.add_name_tag(private_subnet_id4, 'Boto-3-Private-Subnet-3')

    # Create a public route table
    public_route_table_response = vpc.create_public_route_table(vpc_id)

    rtb_id = public_route_table_response['RouteTable']['RouteTableId']
    vpc.add_name_tag(rtb_id, 'public route table')

    #Create a private route table

    private_route_table_response = vpc.create_public_route_table(vpc_id)
    rtb_id1 = private_route_table_response['RouteTable']['RouteTableId']
    vpc.add_name_tag(rtb_id1, 'private route table')

    # Adding the IGW to public route table
    vpc.create_igw_route_to_public_route_table(rtb_id, igw_id)

    # Adding the IGW to private route table

    vpc.create_igw_route_to_public_route_table(rtb_id1, igw_id)

    # Associate Public Subnet with Route Table
    vpc.associate_subnet_with_route_table(public_subnet_id1, rtb_id)
    vpc.associate_subnet_with_route_table(public_subnet_id2, rtb_id)

    # Associate Private Subnet with Route Table

    vpc.associate_subnet_with_route_table(private_subnet_id3, rtb_id1)
    vpc.associate_subnet_with_route_table(private_subnet_id4, rtb_id1)

    # Allow auto-assign public ip addresses for subnet
    vpc.allow_auto_assign_ip_addresses_for_subnet(public_subnet_id1)
    vpc.allow_auto_assign_ip_addresses_for_subnet(public_subnet_id2)


    #Creating Nat Gateway

    vpc.create_nat_gateway(public_subnet_id2, 'eipalloc-05183f537008a5d02')





    #Creating an Elastic LoadBalancer

    









if __name__ == '__main__':
    main()
 
