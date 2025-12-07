#!/usr/bin/env python3
"""
Test the new folder-based task API endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"
PROJECT_NAME = "test-folder-system"


def test_get_project_data():
    """Test GET /api/dashboard/projects/{project_name}/data"""
    print("=" * 80)
    print("Testing: GET /api/dashboard/projects/{project_name}/data")
    print("=" * 80)

    url = f"{BASE_URL}/api/dashboard/projects/{PROJECT_NAME}/data"
    response = requests.get(url)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Response received")
        print(f"  - Project ID: {data.get('project_id', 'N/A')}")
        print(f"  - Project Title: {data.get('project_title', 'N/A')}")
        print(f"  - Total Tasks: {data.get('summary', {}).get('total_tasks', 'N/A')}")
        print(f"  - Task Tree: {'present' if 'task_tree' in data else 'missing'}")
        print()
        print("Sample of project_data.json:")
        print(json.dumps(data, indent=2)[:500] + "...")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200


def test_get_task_notes():
    """Test GET /api/dashboard/tasks/{task_id}/notes"""
    print("=" * 80)
    print("Testing: GET /api/dashboard/tasks/{task_id}/notes")
    print("=" * 80)

    # First get project data to get a task ID
    url = f"{BASE_URL}/api/dashboard/projects/{PROJECT_NAME}/data"
    response = requests.get(url)
    data = response.json()

    # Get the first child task (Build Frontend)
    task_tree = data.get("task_tree", {})
    children = task_tree.get("children", [])

    if not children:
        print("✗ No child tasks found")
        return False

    task_id = children[0]["id"]
    print(f"Testing with task ID: {task_id}")

    url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/notes?project_name={PROJECT_NAME}"
    response = requests.get(url)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        notes_data = response.json()
        print(f"✓ Notes retrieved")
        print(f"  Content preview: {notes_data.get('content', '')[:200]}...")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200


def test_update_task_notes():
    """Test POST /api/dashboard/tasks/{task_id}/notes"""
    print("=" * 80)
    print("Testing: POST /api/dashboard/tasks/{task_id}/notes")
    print("=" * 80)

    # First get project data to get a task ID
    url = f"{BASE_URL}/api/dashboard/projects/{PROJECT_NAME}/data"
    response = requests.get(url)
    data = response.json()

    # Get the first child task
    task_tree = data.get("task_tree", {})
    children = task_tree.get("children", [])

    if not children:
        print("✗ No child tasks found")
        return False

    task_id = children[0]["id"]
    print(f"Testing with task ID: {task_id}")

    new_notes = """# Build Frontend

## Updated Planning Notes

This is a test update from the API.

- Use React 18
- TailwindCSS for styling
- Socket.io client
- Testing API update functionality
"""

    url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/notes?project_name={PROJECT_NAME}"
    response = requests.post(url, json=new_notes)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print(f"✓ Notes updated successfully")

        # Verify update by reading back
        url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/notes?project_name={PROJECT_NAME}"
        response = requests.get(url)
        notes_data = response.json()

        if "Testing API update functionality" in notes_data.get("content", ""):
            print(f"✓ Update verified")
        else:
            print(f"✗ Update not verified")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200


def test_get_task_files():
    """Test GET /api/dashboard/tasks/{task_id}/files"""
    print("=" * 80)
    print("Testing: GET /api/dashboard/tasks/{task_id}/files")
    print("=" * 80)

    # First get project data to get a task ID
    url = f"{BASE_URL}/api/dashboard/projects/{PROJECT_NAME}/data"
    response = requests.get(url)
    data = response.json()

    task_id = data.get("project_id")
    print(f"Testing with task ID: {task_id}")

    url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/files?project_name={PROJECT_NAME}"
    response = requests.get(url)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        files = response.json()
        print(f"✓ Files list retrieved")
        print(f"  Number of files: {len(files)}")

        for file in files:
            print(f"  - {file['name']} ({file['size']} bytes)")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200


def test_upload_task_file():
    """Test POST /api/dashboard/tasks/{task_id}/files"""
    print("=" * 80)
    print("Testing: POST /api/dashboard/tasks/{task_id}/files")
    print("=" * 80)

    # First get project data to get a task ID
    url = f"{BASE_URL}/api/dashboard/projects/{PROJECT_NAME}/data"
    response = requests.get(url)
    data = response.json()

    task_id = data.get("project_id")
    print(f"Testing with task ID: {task_id}")

    # Create a test file
    test_content = b"This is a test file uploaded via API"
    files = {"file": ("test_upload.txt", test_content)}

    url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/files?project_name={PROJECT_NAME}"
    response = requests.post(url, files=files)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ File uploaded successfully")
        print(f"  Filename: {result.get('filename')}")
        print(f"  Size: {result.get('size')} bytes")

        # Verify file is in the list
        url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/files?project_name={PROJECT_NAME}"
        response = requests.get(url)
        files_list = response.json()

        if any(f['name'] == 'test_upload.txt' for f in files_list):
            print(f"✓ File verified in file list")
        else:
            print(f"✗ File not found in file list")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200


def test_download_task_file():
    """Test GET /api/dashboard/tasks/{task_id}/files/{filename}"""
    print("=" * 80)
    print("Testing: GET /api/dashboard/tasks/{task_id}/files/{filename}")
    print("=" * 80)

    # First get project data to get a task ID
    url = f"{BASE_URL}/api/dashboard/projects/{PROJECT_NAME}/data"
    response = requests.get(url)
    data = response.json()

    task_id = data.get("project_id")
    print(f"Testing with task ID: {task_id}")

    filename = "test_upload.txt"
    url = f"{BASE_URL}/api/dashboard/tasks/{task_id}/files/{filename}?project_name={PROJECT_NAME}"
    response = requests.get(url)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        content = response.content
        print(f"✓ File downloaded successfully")
        print(f"  Size: {len(content)} bytes")
        print(f"  Content: {content[:100]}")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200


def main():
    """Run all tests."""
    print("\n")
    print("=" * 80)
    print("Testing Folder-Based Task API Endpoints")
    print("=" * 80)
    print()

    results = {
        "get_project_data": test_get_project_data(),
        "get_task_notes": test_get_task_notes(),
        "update_task_notes": test_update_task_notes(),
        "get_task_files": test_get_task_files(),
        "upload_task_file": test_upload_task_file(),
        "download_task_file": test_download_task_file(),
    }

    print("=" * 80)
    print("Test Results Summary")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print()

    all_passed = all(results.values())

    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
