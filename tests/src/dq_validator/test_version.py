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
Unit tests for __version__
"""
import pytest
from packaging.version import parse, Version

class TestVersions:
    test_version = Version('0.5.0')
    """ Tests versions embedded in various components """
    def test_wxdi_version(self):
        import wxdi
        assert TestVersions.test_version < parse(wxdi.__version__)
    
    def test_wxdi_dqvalidator_version(self):
        import wxdi.dq_validator
        assert TestVersions.test_version < parse(wxdi.dq_validator.__version__)

    def test_wxdi_dqvalidator_integrations_version(self):
        import wxdi.dq_validator.integrations
        assert TestVersions.test_version < parse(wxdi.dq_validator.integrations.__version__)