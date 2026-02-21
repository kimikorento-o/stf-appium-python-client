import logging
import os
import sys
import urllib
import pytest
import urllib3.exceptions
from mock import patch
from stf_appium_client.cli import main


class TestAdbServer:

    def test_help(self):
        testargs = ["prog", "--help"]
        with pytest.raises(SystemExit) as cm:
            with patch.object(sys, 'argv', testargs):
                main()
        assert cm.value.code == 0

    def test_host_invalid_requirements(self):
        testargs = ["prog", "--token", "123", "--host",
                    "http://test", "--requirements", "asdf"]
        with pytest.raises(SystemExit) as cm:
            with patch.object(sys, 'argv', testargs):
                main()
        assert cm.value.code == 1

    @patch('shutil.which')
    def test_host_not_found(self, mock_which):
        testargs = ["prog", "--token", "123", "--host", "http://test"]
        with pytest.raises(urllib3.exceptions.MaxRetryError):
            with patch.object(sys, 'argv', testargs):
                main()

    @patch.dict(os.environ, {'CI': '1'})
    @patch('stf_appium_client.cli.StfClient')
    def test_avoid_devices_forwarded_to_allocation_context(self, mock_stf):
        avoid_devices = ['AAA', 'BBB']
        # Stop execution after allocation_context is called to avoid mocking AdbServer/AppiumServer
        mock_stf.return_value.allocation_context.side_effect = SystemExit('test_stop')
        with patch.object(sys, 'argv', ["prog", "--token", "123", "--avoid-devices", ",".join(avoid_devices)]):
            with pytest.raises(SystemExit) as cm:
                main()
        assert cm.value.code == 'test_stop'
        _, kwargs = mock_stf.return_value.allocation_context.call_args
        assert kwargs.get('avoid_list') == avoid_devices
