"""
   Copyright 2026 IBM Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
"""
Tests for thread safety of provider classes
"""

import pytest
import threading
from unittest.mock import Mock, patch
from wxdi.dq_validator.provider import ProviderConfig, DQSearchProvider, IssuesProvider


class TestThreadSafety:
    """Test suite for thread safety of provider classes."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ProviderConfig(
            url="https://test-instance.com",
            auth_token="Bearer test-token"
        )
    
    def test_dq_search_provider_thread_local_sessions(self, config):
        """Test that each thread gets its own session in DQSearchProvider."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            provider = DQSearchProvider(config)
            
            # Track session instances created
            sessions_created = []
            
            def mock_session_factory():
                session = Mock()
                sessions_created.append(session)
                return session
            
            mock_session_class.side_effect = mock_session_factory
            
            # Access session from main thread
            main_session = provider.session
            assert len(sessions_created) == 1
            
            # Access session from another thread
            thread_sessions = []
            
            def access_session():
                thread_sessions.append(provider.session)
            
            thread = threading.Thread(target=access_session)
            thread.start()
            thread.join()
            
            # Should have created a second session for the new thread
            assert len(sessions_created) == 2
            assert main_session is sessions_created[0]
            assert thread_sessions[0] is sessions_created[1]
            assert main_session is not thread_sessions[0]
    
    def test_issues_provider_thread_local_sessions(self, config):
        """Test that each thread gets its own session in IssuesProvider."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            provider = IssuesProvider(config)
            
            # Track session instances created
            sessions_created = []
            
            def mock_session_factory():
                session = Mock()
                sessions_created.append(session)
                return session
            
            mock_session_class.side_effect = mock_session_factory
            
            # Access session from main thread
            main_session = provider.session
            assert len(sessions_created) == 1
            
            # Access session from another thread
            thread_sessions = []
            
            def access_session():
                thread_sessions.append(provider.session)
            
            thread = threading.Thread(target=access_session)
            thread.start()
            thread.join()
            
            # Should have created a second session for the new thread
            assert len(sessions_created) == 2
            assert main_session is sessions_created[0]
            assert thread_sessions[0] is sessions_created[1]
            assert main_session is not thread_sessions[0]
    
    def test_dq_search_provider_session_reuse_within_thread(self, config):
        """Test that session is reused within the same thread."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            provider = DQSearchProvider(config)
            
            sessions_created = []
            
            def mock_session_factory():
                session = Mock()
                sessions_created.append(session)
                return session
            
            mock_session_class.side_effect = mock_session_factory
            
            # Access session multiple times in the same thread
            session1 = provider.session
            session2 = provider.session
            session3 = provider.session
            
            # Should only create one session
            assert len(sessions_created) == 1
            assert session1 is session2
            assert session2 is session3