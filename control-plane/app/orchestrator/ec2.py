"""AWS EC2 instance orchestration"""
import boto3
from botocore.exceptions import ClientError
from app.config import settings
import logging
from typing import Optional, Dict, Any
import base64

logger = logging.getLogger(__name__)


class EC2Orchestrator:
    def __init__(self):
        """Initialize EC2 client"""
        if settings.local_dev_mode:
            self.ec2_client = None
            logger.info("EC2 orchestrator in local dev mode (no AWS)")
        else:
            self.ec2_client = boto3.client(
                'ec2',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )

    def _read_user_data_script(self) -> str:
        """Read the user data bash script"""
        try:
            with open('app/orchestrator/user_data.sh', 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error("user_data.sh not found")
            # Return minimal script
            return """#!/bin/bash
echo "CloudBot instance starting..."
# TODO: Install CloudBot and VNC
"""

    async def create_instance(
        self,
        user_id: str,
        instance_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provision a new EC2 instance"""
        if settings.local_dev_mode:
            # Mock instance for local development
            import uuid
            mock_instance_id = f"i-mock-{str(uuid.uuid4())[:8]}"
            return {
                "instance_id": mock_instance_id,
                "public_ip": "127.0.0.1",
                "status": "running"
            }

        try:
            # Read user data script
            user_data = self._read_user_data_script()

            # Launch EC2 instance
            response = self.ec2_client.run_instances(
                ImageId=settings.aws.ec2.ubuntu_ami_id,
                InstanceType='t3.large',
                MinCount=1,
                MaxCount=1,
                KeyName=settings.aws.ec2.key_pair_name,
                SecurityGroupIds=[settings.aws.ec2.security_group_id],
                SubnetId=settings.aws.ec2.subnet_id,
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': instance_name or f'cloudbot-{user_id[:8]}'},
                            {'Key': 'User', 'Value': user_id},
                            {'Key': 'ManagedBy', 'Value': 'cloudbot-platform'},
                        ]
                    }
                ],
                InstanceMarketOptions={
                    'MarketType': 'spot',
                    'SpotOptions': {
                        'MaxPrice': '0.10',  # Max price per hour
                        'SpotInstanceType': 'one-time'
                    }
                }
            )

            instance = response['Instances'][0]
            instance_id = instance['InstanceId']

            logger.info(f"Created EC2 instance: {instance_id} for user {user_id}")

            return {
                "instance_id": instance_id,
                "public_ip": instance.get('PublicIpAddress'),
                "status": instance['State']['Name']
            }

        except ClientError as e:
            logger.error(f"Failed to create EC2 instance: {e}")
            raise Exception(f"Failed to provision instance: {str(e)}")

    async def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get status of an EC2 instance"""
        if settings.local_dev_mode:
            return {"status": "running", "public_ip": "127.0.0.1"}

        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            if not response['Reservations']:
                return {"status": "not_found"}

            instance = response['Reservations'][0]['Instances'][0]
            return {
                "status": instance['State']['Name'],
                "public_ip": instance.get('PublicIpAddress')
            }

        except ClientError as e:
            logger.error(f"Failed to get instance status: {e}")
            return {"status": "error", "error": str(e)}

    async def stop_instance(self, instance_id: str) -> bool:
        """Stop an EC2 instance"""
        if settings.local_dev_mode:
            return True

        try:
            self.ec2_client.stop_instances(InstanceIds=[instance_id])
            logger.info(f"Stopped EC2 instance: {instance_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to stop instance: {e}")
            return False

    async def start_instance(self, instance_id: str) -> bool:
        """Start a stopped EC2 instance"""
        if settings.local_dev_mode:
            return True

        try:
            self.ec2_client.start_instances(InstanceIds=[instance_id])
            logger.info(f"Started EC2 instance: {instance_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to start instance: {e}")
            return False

    async def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an EC2 instance"""
        if settings.local_dev_mode:
            return True

        try:
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            logger.info(f"Terminated EC2 instance: {instance_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to terminate instance: {e}")
            return False


# Global orchestrator instance
orchestrator = EC2Orchestrator()
