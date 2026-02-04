"""AWS EC2 instance orchestration"""
import boto3
from botocore.exceptions import ClientError
from app.config import settings
import logging
from typing import Optional, Dict, Any
import base64
import gzip

logger = logging.getLogger(__name__)


class EC2Orchestrator:
    # Required ports for CloudBot instances
    REQUIRED_PORTS = [
        (5900, 'VNC Server'),
        (18789, 'CloudBot Gateway'),
    ]

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
            # Ensure security group has required ports
            self._ensure_security_group_rules()

    def _ensure_security_group_rules(self):
        """Ensure the security group has rules for required ports"""
        if not settings.ec2_security_group_id:
            logger.warning("No security group ID configured")
            return

        try:
            # Get current security group rules
            response = self.ec2_client.describe_security_groups(
                GroupIds=[settings.ec2_security_group_id]
            )

            if not response['SecurityGroups']:
                logger.error(f"Security group {settings.ec2_security_group_id} not found")
                return

            sg = response['SecurityGroups'][0]
            existing_ports = set()

            # Check existing inbound rules
            for rule in sg.get('IpPermissions', []):
                if rule.get('IpProtocol') == 'tcp':
                    from_port = rule.get('FromPort')
                    to_port = rule.get('ToPort')
                    if from_port == to_port:
                        existing_ports.add(from_port)

            # Add missing rules
            for port, description in self.REQUIRED_PORTS:
                if port not in existing_ports:
                    logger.info(f"Adding security group rule for port {port} ({description})")
                    try:
                        self.ec2_client.authorize_security_group_ingress(
                            GroupId=settings.ec2_security_group_id,
                            IpPermissions=[{
                                'IpProtocol': 'tcp',
                                'FromPort': port,
                                'ToPort': port,
                                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': description}]
                            }]
                        )
                        logger.info(f"Added rule for port {port}")
                    except ClientError as e:
                        if 'InvalidPermission.Duplicate' in str(e):
                            logger.info(f"Rule for port {port} already exists")
                        else:
                            logger.error(f"Failed to add rule for port {port}: {e}")
                else:
                    logger.info(f"Port {port} ({description}) already allowed")

        except ClientError as e:
            logger.error(f"Failed to check/update security group: {e}")

    def _read_user_data_script(self, api_keys: dict = None) -> str:
        """Read the user data bash script, inject API keys, and compress if needed"""
        try:
            with open('app/orchestrator/user_data.sh', 'r') as f:
                script = f.read()
        except FileNotFoundError:
            logger.error("user_data.sh not found")
            # Return minimal script
            return """#!/bin/bash
echo "CloudBot instance starting..."
# TODO: Install CloudBot and VNC
"""

        # Inject environment variables at the beginning of the script
        env_exports = []

        # Add control plane URL if configured
        logger.info(f"CONTROL_PLANE_URL setting: {settings.control_plane_url}")
        if settings.control_plane_url:
            env_exports.append(f"export CONTROL_PLANE_URL='{settings.control_plane_url}'")
            logger.info(f"Added CONTROL_PLANE_URL to user_data: {settings.control_plane_url}")
        else:
            logger.error("CONTROL_PLANE_URL is NOT SET - EC2 instances will fail to download OpenClaw!")

        # Add moltbot tarball URL if configured
        if settings.moltbot_tarball_url:
            env_exports.append(f"export MOLTBOT_TARBALL_URL='{settings.moltbot_tarball_url}'")

        # Add API keys
        if api_keys:
            logger.info(f"Injecting API keys for providers: {list(api_keys.keys())}")
            for provider, key in api_keys.items():
                # Map provider names to environment variables
                # Handle both formats: 'ANTHROPIC_API_KEY' or 'ANTHROPIC'
                env_var = provider.upper()
                if not env_var.endswith('_API_KEY'):
                    env_var = f"{env_var}_API_KEY"
                # Escape any special characters in the key
                escaped_key = key.replace("'", "'\"'\"'")
                env_exports.append(f"export {env_var}='{escaped_key}'")
                logger.info(f"  - Added {env_var} (length: {len(key)})")
        else:
            logger.warning("No API keys provided for user_data script")

        if env_exports:
            # Insert after the shebang line
            env_block = "\n# Environment from CloudBot Platform\n" + "\n".join(env_exports) + "\n"
            script = script.replace("#!/bin/bash\n", "#!/bin/bash\n" + env_block, 1)
            logger.info(f"Injected {len(env_exports)} environment variables into user_data script")

        # Check if script exceeds 16KB limit - compress if needed
        script_bytes = script.encode('utf-8')
        if len(script_bytes) > 15000:  # Leave some margin
            logger.info(f"Script size {len(script_bytes)} bytes exceeds limit, compressing...")
            compressed = gzip.compress(script_bytes)
            encoded = base64.b64encode(compressed).decode('ascii')

            # Create a bootstrap script that decompresses and runs the main script
            bootstrap = f"""#!/bin/bash
# Bootstrap loader - decompresses and runs the main setup script
echo "Decompressing setup script..."
echo '{encoded}' | base64 -d | gunzip > /tmp/cloudbot-setup.sh
chmod +x /tmp/cloudbot-setup.sh
exec /tmp/cloudbot-setup.sh
"""
            logger.info(f"Compressed from {len(script_bytes)} to {len(bootstrap.encode('utf-8'))} bytes")
            return bootstrap

        return script

    async def create_instance(
        self,
        user_id: str,
        instance_name: Optional[str] = None,
        instance_type: str = 't3.large',
        api_keys: Dict[str, str] = None
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
            # Read user data script with API keys injected
            user_data = self._read_user_data_script(api_keys)

            # Launch EC2 instance with 20GB root volume
            # Validate instance type
            # Launch EC2 instance with 20GB root volume

            response = self.ec2_client.run_instances(
                ImageId=settings.ubuntu_ami_id,
                InstanceType=instance_type,
                MinCount=1,
                MaxCount=1,
                KeyName=settings.ec2_key_pair_name,
                SecurityGroupIds=[settings.ec2_security_group_id],
                SubnetId=settings.ec2_subnet_id,
                UserData=user_data,
                BlockDeviceMappings=[
                    {
                        'DeviceName': '/dev/sda1',
                        'Ebs': {
                            'VolumeSize': 20,
                            'VolumeType': 'gp3',
                            'DeleteOnTermination': True,
                        }
                    }
                ],
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
