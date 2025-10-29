#!/usr/bin/env python3
"""
Web-based control panel for managing Hetzner instances
Access at http://localhost:5000
"""

import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from hetzner_manager import HetznerManager, generate_cloud_init_script
from datetime import datetime

app = Flask(__name__)
manager = None


def get_manager():
    """Get or create HetznerManager instance"""
    global manager
    if manager is None:
        manager = HetznerManager()
    return manager


@app.route('/')
def index():
    """Serve control panel UI"""
    return render_template('control_panel.html')


@app.route('/api/instances', methods=['GET'])
def list_instances():
    """List all instances"""
    try:
        m = get_manager()
        instances = m.list_instances(label_selector="app=computer-use-demo")

        # Format instance data
        formatted = []
        for inst in instances:
            formatted.append({
                'id': inst['id'],
                'name': inst['name'],
                'status': inst['status'],
                'ip': inst['public_net']['ipv4']['ip'],
                'created': inst['created'],
                'server_type': inst['server_type']['name'],
                'cost_per_hour': 0.007,  # CX22 pricing
                'urls': {
                    'chat': f"http://{inst['public_net']['ipv4']['ip']}:8501",
                    'desktop': f"http://{inst['public_net']['ipv4']['ip']}:8080"
                }
            })

        return jsonify({'instances': formatted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshots', methods=['GET'])
def list_snapshots():
    """List all snapshots"""
    try:
        m = get_manager()
        snapshots = m.list_snapshots(label_selector="created_by=computer-use-demo")

        formatted = []
        for snap in snapshots:
            formatted.append({
                'id': snap['id'],
                'description': snap['description'],
                'created': snap['created'],
                'size_gb': snap['image_size'],
                'cost_per_month': round(snap['image_size'] * 0.0119, 2)
            })

        return jsonify({'snapshots': formatted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/create', methods=['POST'])
def create_instance():
    """Create new instance"""
    try:
        data = request.json
        name = data.get('name', f"computer-use-{int(datetime.now().timestamp())}")
        snapshot_id = data.get('snapshot_id')

        m = get_manager()

        if snapshot_id:
            # Clone from snapshot
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
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/<int:instance_id>/start', methods=['POST'])
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
def stop_instance(instance_id):
    """Stop a running instance"""
    try:
        m = get_manager()
        m.stop_instance(instance_id)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/<int:instance_id>/delete', methods=['DELETE'])
def delete_instance(instance_id):
    """Delete an instance"""
    try:
        m = get_manager()
        m.delete_instance(instance_id)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instance/<int:instance_id>/snapshot', methods=['POST'])
def create_snapshot(instance_id):
    """Create snapshot of instance"""
    try:
        data = request.json
        description = data.get('description', f"snapshot-{datetime.now().strftime('%Y-%m-%d-%H%M')}")

        m = get_manager()
        snapshot = m.create_snapshot(instance_id, description)

        return jsonify({
            'success': True,
            'snapshot': {
                'id': snapshot['id'],
                'description': snapshot['description']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshot/<int:snapshot_id>/delete', methods=['DELETE'])
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

    app.run(host='0.0.0.0', port=5000, debug=True)
