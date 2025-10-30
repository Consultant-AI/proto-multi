#!/bin/bash
# Quick deploy script - uses CURRENT hetzner_manager.py which builds from YOUR repo

# Set these environment variables before running this script
# export HETZNER_API_TOKEN=your_token_here
# export ANTHROPIC_API_KEY=your_key_here

python3 -c "
from hetzner_manager import HetznerManager, generate_cloud_init_script

# Delete the nginx-proxy instance (wrong image)
m = HetznerManager()
print('Deleting nginx-proxy instance (wrong image)...')
try:
    m.delete_instance(111814619)
    print('✅ Deleted')
except:
    print('Already deleted or not found')

print()
print('Creating instance with YOUR custom Ubuntu + Chrome...')
print('Build will happen on Hetzner (takes 15-20 min but uses correct image)')
print()

# This uses generate_cloud_init_script which builds from Consultant-AI/proto-multi
user_data = generate_cloud_init_script('$ANTHROPIC_API_KEY', '$HETZNER_API_TOKEN')

server = m.create_instance(
    name='computer-use-custom',
    user_data=user_data,
    labels={'app': 'computer-use-demo'}
)

print()
print(f'✅ Instance created: {server[\"public_net\"][\"ipv4\"][\"ip\"]}')
print(f'   ID: {server[\"id\"]}')
print()
print('Services will be ready in 15-20 minutes')
print('Dashboard at http://localhost:5500 will show when ready')
print()
print('This instance has:')
print('  ✅ YOUR custom Ubuntu with Chrome')
print('  ✅ Fixed index.html (port 8080 works)')
print('  ✅ Mutter window manager')
print('  ✅ Systemd auto-start')
"
