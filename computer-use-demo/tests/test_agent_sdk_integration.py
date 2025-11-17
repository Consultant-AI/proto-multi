"""
Integration tests for Agent SDK components.

Tests the core Agent SDK functionality integrated with computer-use-demo.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from computer_use_demo.agent_sdk import (
    AgentOrchestrator,
    SessionManager,
    ContextManager,
    SubagentCoordinator,
)
from computer_use_demo.agent_sdk.subagents import SubagentTask, SubagentType
from computer_use_demo.verification import (
    ScreenshotAnalyzer,
    StructuralChecker,
    FeedbackLoop,
    Action,
    ActionType,
)


class TestSessionManager:
    """Test session persistence functionality"""

    def setup_method(self):
        """Create temporary claude home for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_home = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_session_creation(self):
        """Test that sessions are created with proper structure"""
        session = SessionManager(
            session_id="test-session",
            claude_home=self.claude_home,
        )

        # Verify session directory created
        assert session.session_dir.exists()
        assert session.session_dir.is_dir()

        # Verify metadata file created
        assert session.metadata_file.exists()

        # Check metadata content
        stats = session.get_session_stats()
        assert stats["session_id"] == "test-session"
        assert stats["message_count"] == 0
        assert stats["tool_executions"] == 0

    @pytest.mark.asyncio
    async def test_session_save_load(self):
        """Test saving and loading session messages"""
        session = SessionManager(
            session_id="test-session",
            claude_home=self.claude_home,
        )

        # Create test messages
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        # Save session
        await session.save_session(messages)

        # Verify transcript file exists
        assert session.transcript_file.exists()

        # Load session
        loaded_messages = session.load_session()

        # Verify messages match
        assert len(loaded_messages) == len(messages)
        assert loaded_messages[0]["role"] == "user"
        assert loaded_messages[1]["role"] == "assistant"

    def test_conventions_storage(self):
        """Test CLAUDE.md conventions storage"""
        session = SessionManager(
            session_id="test-session",
            claude_home=self.claude_home,
        )

        # Save conventions
        conventions = "# Test Conventions\n\n## Pattern\nUse this pattern"
        session.save_conventions(conventions)

        # Load conventions
        loaded = session.load_conventions()
        assert loaded == conventions

        # Append convention
        session.append_convention("New Section", "New content here")

        # Verify appended
        loaded = session.load_conventions()
        assert "# Test Conventions" in loaded
        assert "## New Section" in loaded
        assert "New content here" in loaded

    def test_tool_execution_tracking(self):
        """Test tool execution statistics"""
        session = SessionManager(
            session_id="test-session",
            claude_home=self.claude_home,
        )

        # Record some tool executions
        session.record_tool_execution("computer", success=True)
        session.record_tool_execution("computer", success=True)
        session.record_tool_execution("bash", success=True)
        session.record_tool_execution("bash", success=False)

        # Get stats
        stats = session.get_session_stats()

        assert stats["tool_executions"] == 4
        assert stats["tools"]["computer"]["executions"] == 2
        assert stats["tools"]["computer"]["successes"] == 2
        assert stats["tools"]["bash"]["executions"] == 2
        assert stats["tools"]["bash"]["successes"] == 1
        assert stats["tools"]["bash"]["failures"] == 1


class TestContextManager:
    """Test context management functionality"""

    @pytest.mark.asyncio
    async def test_context_compaction(self):
        """Test that context compaction removes old images"""
        context_mgr = ContextManager(max_images=2, min_removal_threshold=1)

        # Create messages with multiple images
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": [
                            {"type": "text", "text": "result 1"},
                            {"type": "image", "source": {"data": "img1"}},
                        ],
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": [
                            {"type": "text", "text": "result 2"},
                            {"type": "image", "source": {"data": "img2"}},
                        ],
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": [
                            {"type": "text", "text": "result 3"},
                            {"type": "image", "source": {"data": "img3"}},
                        ],
                    }
                ],
            },
        ]

        # Compact context
        await context_mgr.maybe_compact_context(messages, only_n_most_recent_images=2)

        # Count remaining images
        image_count = 0
        for message in messages:
            if isinstance(message["content"], list):
                for item in message["content"]:
                    if isinstance(item, dict) and item.get("type") == "tool_result":
                        for content in item.get("content", []):
                            if isinstance(content, dict) and content.get("type") == "image":
                                image_count += 1

        assert image_count == 2  # Only 2 most recent images kept

    def test_context_stats(self):
        """Test context statistics calculation"""
        context_mgr = ContextManager()

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": [
                            {"type": "text", "text": "result"},
                            {"type": "image", "source": {"data": "img"}},
                        ],
                    }
                ],
            },
        ]

        stats = context_mgr.get_context_stats(messages)

        assert stats["total_messages"] == 3
        assert stats["user_messages"] == 2
        assert stats["assistant_messages"] == 1
        assert stats["screenshots"] == 1


class TestSubagentCoordinator:
    """Test subagent coordination"""

    def test_subagent_config_loading(self):
        """Test that subagent configs are loaded correctly"""
        coordinator = SubagentCoordinator(max_concurrent=3)

        # Verify configs exist for all subagent types
        assert SubagentType.EXECUTION in coordinator.subagent_configs
        assert SubagentType.VERIFICATION in coordinator.subagent_configs
        assert SubagentType.FILE_OPERATIONS in coordinator.subagent_configs

        # Verify configs have required fields
        exec_config = coordinator.subagent_configs[SubagentType.EXECUTION]
        assert "system_prompt_suffix" in exec_config
        assert "tools" in exec_config
        assert "max_iterations" in exec_config

    @pytest.mark.asyncio
    async def test_task_submission(self):
        """Test task submission to queue"""
        coordinator = SubagentCoordinator()

        task = SubagentTask(
            task_id="test-task",
            subagent_type=SubagentType.EXECUTION,
            prompt="Test prompt",
        )

        task_id = await coordinator.submit_task(task)
        assert task_id == "test-task"

    def test_coordinator_stats(self):
        """Test coordinator statistics"""
        coordinator = SubagentCoordinator(max_concurrent=5)

        stats = coordinator.get_stats()
        assert stats["max_concurrent"] == 5
        assert stats["total_tasks"] == 0


class TestVerificationSystem:
    """Test verification system components"""

    @pytest.mark.asyncio
    async def test_screenshot_analyzer(self):
        """Test screenshot analysis"""
        analyzer = ScreenshotAnalyzer()

        # Test with dummy base64
        result = await analyzer.analyze_screenshot(
            screenshot_base64="dGVzdA==",  # base64 for "test"
            expected_state="application window visible",
            action_taken="launched application",
        )

        assert result.success is True
        assert len(result.findings) > 0

        # Test verification stats
        stats = analyzer.get_verification_stats()
        assert stats["total_verifications"] == 1

    @pytest.mark.asyncio
    async def test_structural_checker_file_exists(self):
        """Test file existence checking"""
        checker = StructuralChecker()

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = Path(f.name)
            f.write(b"test content")

        try:
            # Check file exists
            result = await checker.check_file_exists(temp_file)
            assert result.success is True
            assert result.check_type == "file_exists"

            # Check file content
            result = await checker.check_file_exists(
                temp_file,
                expected_content="test content",
            )
            assert result.success is True

        finally:
            temp_file.unlink()

    @pytest.mark.asyncio
    async def test_structural_checker_command_output(self):
        """Test command output verification"""
        checker = StructuralChecker()

        # Test successful command
        result = await checker.check_command_output(
            command="echo 'hello'",
            expected_output="hello",
            expected_exit_code=0,
        )

        assert result.success is True
        assert result.check_type == "command_output"

        # Test command with wrong exit code
        result = await checker.check_command_output(
            command="false",  # Returns exit code 1
            expected_exit_code=0,
        )

        assert result.success is False

    @pytest.mark.asyncio
    async def test_feedback_loop(self):
        """Test feedback loop execution"""
        loop = FeedbackLoop(
            enable_visual_verification=False,  # Skip visual for unit test
            enable_structural_verification=True,
            auto_retry=True,
        )

        # Create test action
        action = Action(
            action_type=ActionType.COMMAND_EXECUTION,
            description="Test command",
            verification_criteria={
                "command_checks": [
                    {
                        "command": "echo 'test'",
                        "expected_output": "test",
                        "expected_exit_code": 0,
                    }
                ]
            },
            retry_on_failure=False,
        )

        # Define executor that succeeds
        async def executor():
            pass  # No-op for test

        # Execute with verification
        result = await loop.execute_with_verification(
            action=action,
            executor_callback=executor,
        )

        assert result.success is True
        assert len(result.structural_checks) > 0

        # Get stats
        stats = loop.get_feedback_stats()
        assert stats["total_actions"] == 1
        assert stats["successful_actions"] == 1


class TestAgentOrchestrator:
    """Test main orchestrator"""

    def setup_method(self):
        """Create temporary claude home"""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_home = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        orchestrator = AgentOrchestrator(
            session_id="test-orchestrator",
            claude_home=self.claude_home,
            enable_subagents=True,
            enable_verification=True,
        )

        assert orchestrator.session_manager is not None
        assert orchestrator.context_manager is not None
        assert orchestrator.subagent_coordinator is not None
        assert orchestrator.enable_subagents is True
        assert orchestrator.enable_verification is True

    def test_orchestrator_without_subagents(self):
        """Test orchestrator with subagents disabled"""
        orchestrator = AgentOrchestrator(
            session_id="test-no-subagents",
            claude_home=self.claude_home,
            enable_subagents=False,
        )

        assert orchestrator.subagent_coordinator is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
