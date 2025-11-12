#!/usr/bin/env python3
"""
Web-based control panel for managing Hetzner instances
Access at http://localhost:5500
Requires authentication: admin / anthropic2024
"""

import os
import socket
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from hetzner_manager import HetznerManager, generate_cloud_init_script
from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()
manager = None

# Authentication credentials
users = {
    "admin": generate_password_hash("anthropic2024")
}

@auth.verify_password
def verify_password(username, password):
    """Verify username and password"""
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


def get_manager():
    """Get or create HetznerManager instance"""
    global manager
    if manager is None:
        manager = HetznerManager()
    return manager


def check_port(host, port, timeout=2):
    """Check if a port is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_app_health(host, timeout=3):
    """Check if the application is actually working (not just nginx)"""
    try:
        import requests
        from requests.auth import HTTPBasicAuth

        url = f"http://{host}/"
        response = requests.get(
            url,
            auth=HTTPBasicAuth('admin', 'anthropic2024'),
            timeout=timeout,
            allow_redirects=True
        )

        # Check if we get a real response (not 502)
        if response.status_code == 200 and 'Computer Use Demo' in response.text:
            return 'ready'
        elif response.status_code == 502:
            return 'starting'
        else:
            return 'unknown'
    except Exception:
        return 'offline'


@app.route('/')
@auth.login_required
def index():
    """Serve control panel UI"""
    return render_template('control_panel.html')


@app.route('/api/instances', methods=['GET'])
@auth.login_required
def list_instances():
    """List all instances"""
    try:
        m = get_manager()
        instances = m.list_instances()  # Show ALL instances, not just labeled ones

        # Format instance data
        formatted = []
        for inst in instances:
            ip = inst['public_net']['ipv4']['ip']

            # Check actual application health if instance is running
            app_status = 'offline'
            services_ready = False
            if inst['status'] == 'running':
                app_status = check_app_health(ip, timeout=2)
                services_ready = (app_status == 'ready')

            formatted.append({
                'id': inst['id'],
                'name': inst['name'],
                'status': inst['status'],
                'services_ready': services_ready,
                'app_status': app_status,  # ready, starting, offline, unknown
                'ip': ip,
                'created': inst['created'],
                'server_type': inst['server_type']['name'],
                'cost_per_hour': 0.0096,  # CPX22 pricing
                'urls': {
                    'chat': f"http://{ip}/",
                    'desktop': f"http://{ip}/"
                }
            })

        return jsonify({'instances': formatted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshots', methods=['GET'])
@auth.login_required
def list_snapshots():
    """List all snapshots"""
    try:
        m = get_manager()
        snapshots = m.list_snapshots(label_selector="created_by=computer-use-demo")

        formatted = []
        for snap in snapshots:
            size_gb = snap.get('image_size') or 0
            formatted.append({
                'id': snap['id'],
                'description': snap['description'],
                'created': snap['created'],
                'size_gb': size_gb,
                'cost_per_month': round(size_gb * 0.01, 2)
            })

        return jsonify({'snapshots': formatted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/create', methods=['POST'])
@auth.login_required
def create_instance():
    """Create new instance"""
    try:
        data = request.json
        name = data.get('name', f"computer-use-{int(datetime.now().timestamp())}")
        snapshot_id = data.get('snapshot_id')

        m = get_manager()

        if snapshot_id:
            # Clone from snapshot
            print(f"Cloning from snapshot ID: {snapshot_id} (type: {type(snapshot_id)})")
            server = m.clone_from_snapshot(
                snapshot_id=int(snapshot_id),
                name=name
            )
        else:
            # Create fresh instance
            anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                return jsonify({'error': 'ANTHROPIC_API_KEY not set'}), 400

            user_data = generate_cloud_init_script(anthropic_api_key, m.api_token)
            server = m.create_instance(
                name=name,
                user_data=user_data,
                labels={"app": "computer-use-demo"}
            )

        return jsonify({
            'success': True,
            'instance': {
                'id': server['id'],
                'name': server['name'],
                'ip': server['public_net']['ipv4']['ip']
            }
        })
    except Exception as e:
        print(f"ERROR in create_instance: {e}")
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        # Make server limit error more user-friendly
        if 'server_limit' in error_msg or 'resource_limit_exceeded' in error_msg:
            error_msg = "Server limit reached! Delete an existing instance first."
        return jsonify({'error': error_msg}), 500


@app.route('/api/instance/<int:instance_id>/start', methods=['POST'])
@auth.login_required
def start_instance(instance_id):
    """Start a stopped instance"""
    try:
        m = get_manager()
        server = m.start_instance(instance_id)

        return jsonify({
            'success': True,
            'ip': server['public_net']['ipv4']['ip']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/<int:instance_id>/stop', methods=['POST'])
@auth.login_required
def stop_instance(instance_id):
    """Stop a running instance"""
    try:
        m = get_manager()
        m.stop_instance(instance_id)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/<int:instance_id>/delete', methods=['DELETE'])
@auth.login_required
def delete_instance(instance_id):
    """Delete an instance"""
    try:
        m = get_manager()
        m.delete_instance(instance_id)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/<int:instance_id>/snapshot', methods=['POST'])
@auth.login_required
def create_snapshot(instance_id):
    """Create snapshot of instance"""
    try:
        data = request.json
        description = data.get('description', f"snapshot-{datetime.now().strftime('%Y-%m-%d-%H%M')}")

        m = get_manager()

        # Check if instance is ready for snapshotting (services running)
        instance = m.get_instance(instance_id)
        ip = instance['public_net']['ipv4']['ip']

        # Only warn, don't block - user might know what they're doing
        services_ready = check_port(ip, 80, timeout=2)
        if not services_ready:
            print(f"⚠️  WARNING: Snapshotting instance {instance_id} but services not ready yet")
            print(f"⚠️  Docker may still be building - restored instances will be slow")

        snapshot = m.create_snapshot(instance_id, description)

        return jsonify({
            'success': True,
            'snapshot': {
                'id': snapshot['id'],
                'description': snapshot['description']
            },
            'warning': None if services_ready else 'Services not ready - snapshot may require rebuild on restore'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshot/<int:snapshot_id>/delete', methods=['DELETE'])
@auth.login_required
def delete_snapshot(snapshot_id):
    """Delete a snapshot"""
    try:
        m = get_manager()
        m._request("DELETE", f"images/{snapshot_id}")

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Check for required environment variables
    if not os.environ.get('HETZNER_API_TOKEN'):
        print("Error: HETZNER_API_TOKEN environment variable not set")
        print("Run: export HETZNER_API_TOKEN=your-token")
        exit(1)

    print("=" * 50)
    print("Hetzner Control Panel")
    print("=" * 50)
    print("")
    print("Starting control panel...")
    print("")
    print("Access at: http://localhost:5000")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5500, debug=True)
