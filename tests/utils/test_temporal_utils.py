"""Tests for Temporal utilities"""

import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch, AsyncMock
from temporalio.api.common.v1 import Payload

from atlas_shared_app.utils.temporal_utils import (
    EncryptionCodec,
    default_key,
    default_key_id,
    setup_workflow,
    get_sandboxed_workflow_runner,
    get_workflow_client,
    DEFAULT_PASSTHROUGH_MODULES,
)
from atlas_shared_app.settings.atlas_settings import AtlasSettings, AtlasWorkflowSettings
from atlas_shared_app.settings.atlas_logging_settings import AtlasLoggingSettings


@pytest.mark.asyncio
async def test_encryption_codec_default():
    """Test EncryptionCodec with default parameters"""
    codec = EncryptionCodec()

    # Create a test payload
    original = Payload(data=b"test data", metadata={"test": b"value"})

    # Encode
    encoded = await codec.encode([original])
    assert len(encoded) == 1
    assert encoded[0].metadata.get("encoding") == b"binary/encrypted"
    assert encoded[0].metadata.get("encryption-key-id") == default_key_id.encode()

    # Decode
    decoded = await codec.decode(encoded)
    assert len(decoded) == 1
    assert decoded[0].data == original.data
    assert decoded[0].metadata.get("test") == b"value"


@pytest.mark.asyncio
async def test_encryption_codec_custom_key():
    """Test EncryptionCodec with custom key"""
    custom_key = b"custom-key-custom-key-custom-32b"
    custom_key_id = "custom-key-id"

    codec = EncryptionCodec(key_id=custom_key_id, key=custom_key)

    # Create a test payload
    original = Payload(data=b"secret data")

    # Encode and decode
    encoded = await codec.encode([original])
    decoded = await codec.decode(encoded)

    assert decoded[0].data == original.data
    assert encoded[0].metadata.get("encryption-key-id") == custom_key_id.encode()


@pytest.mark.asyncio
async def test_encryption_codec_wrong_key():
    """Test that decoding with wrong key ID raises error"""
    codec1 = EncryptionCodec(key_id="key1", key=b"key11111111111111111111111111111")
    codec2 = EncryptionCodec(key_id="key2", key=b"key22222222222222222222222222222")

    original = Payload(data=b"test data")

    # Encode with codec1
    encoded = await codec1.encode([original])

    # Try to decode with codec2 (different key ID)
    with pytest.raises(ValueError, match="Unrecognized key ID"):
        await codec2.decode(encoded)


@pytest.mark.asyncio
async def test_encryption_codec_skip_unencrypted():
    """Test that codec skips payloads without encryption"""
    codec = EncryptionCodec()

    # Unencrypted payload
    unencrypted = Payload(data=b"plain data", metadata={"encoding": b"json/plain"})

    # Decode should return it unchanged
    decoded = await codec.decode([unencrypted])
    assert len(decoded) == 1
    assert decoded[0].data == unencrypted.data
    assert decoded[0].metadata.get("encoding") == b"json/plain"


def test_default_passthrough_modules():
    """Test DEFAULT_PASSTHROUGH_MODULES contains expected modules"""
    assert "atlas_shared_app" in DEFAULT_PASSTHROUGH_MODULES
    assert "pydantic" in DEFAULT_PASSTHROUGH_MODULES
    assert "sqlmodel" in DEFAULT_PASSTHROUGH_MODULES
    assert "sqlalchemy" in DEFAULT_PASSTHROUGH_MODULES


def test_get_sandboxed_workflow_runner_default():
    """Test get_sandboxed_workflow_runner with default modules"""
    runner = get_sandboxed_workflow_runner()
    assert runner is not None


def test_get_sandboxed_workflow_runner_custom():
    """Test get_sandboxed_workflow_runner with custom modules"""
    custom_modules = ("custom_module", "another_module")
    runner = get_sandboxed_workflow_runner(custom_modules)
    assert runner is not None


@patch('atlas_shared_app.utils.temporal_utils.setup.Runtime')
@patch('atlas_shared_app.utils.temporal_utils.setup.RotatingFileHandler')
@patch('atlas_shared_app.utils.temporal_utils.setup.os.makedirs')
def test_setup_workflow(mock_makedirs, mock_handler, mock_runtime):
    """Test setup_workflow configures logging and runtime"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "logs", "workflow.log")

        mock_settings = MagicMock(spec=AtlasSettings)
        mock_settings.logging_settings = MagicMock(spec=AtlasLoggingSettings)
        mock_settings.logging_settings.workflow_log_file = log_file
        mock_settings.logging_settings.workflow_log_max_bytes = 10485760
        mock_settings.logging_settings.workflow_log_backup_count = 5
        mock_settings.logging_settings.workflow_log_format = "%(message)s"
        mock_settings.logging_settings.workflow_log_level = "INFO"

        setup_workflow(mock_settings)

        mock_makedirs.assert_called_once()
        mock_runtime.assert_called_once()
        mock_runtime.set_default.assert_called_once()


@pytest.mark.asyncio
@patch('atlas_shared_app.utils.temporal_utils.setup.Client')
async def test_get_workflow_client(mock_client_class):
    """Test get_workflow_client connects to Temporal"""
    mock_client = AsyncMock()
    mock_client_class.connect = AsyncMock(return_value=mock_client)

    settings = MagicMock()
    settings.temporal_address = "localhost:7233"
    settings.secret_temporal_api_key.get_secret_value.return_value = "test-key"
    settings.temporal_namespace = "test-namespace"

    result = await get_workflow_client(settings)

    mock_client_class.connect.assert_called_once()
    assert result == mock_client
