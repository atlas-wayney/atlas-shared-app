
import logging
import os
from logging.handlers import RotatingFileHandler

from temporalio import workflow
from temporalio.client import Client
from temporalio.runtime import Runtime, TelemetryConfig, LoggingConfig, LogForwardingConfig, TelemetryFilter
from temporalio.worker.workflow_sandbox import (
    SandboxedWorkflowRunner,
    SandboxRestrictions,
)

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter

from atlas_shared_app.settings.atlas_settings import AtlasSettings, AtlasWorkflowSettings

def setup_workflow(settings: AtlasSettings) -> None:
   # Configure global logging with file handler using settings
    log_settings = settings.logging_settings
    os.makedirs(os.path.dirname(log_settings.workflow_log_file), exist_ok=True)
    file_handler = RotatingFileHandler(
        log_settings.workflow_log_file,
        maxBytes=log_settings.workflow_log_max_bytes,
        backupCount=log_settings.workflow_log_backup_count,
    )
    file_handler.setFormatter(logging.Formatter(log_settings.workflow_log_format))

    # Set at root logger level - applies to all loggers
    log_level = getattr(logging, log_settings.workflow_log_level.upper(), logging.INFO)
    logging.Formatter.default_msec_format = '%s.%03d' 
    logging.basicConfig(level=log_level, handlers=[file_handler], force=True)

    # Configure Temporal Runtime with log forwarding to root logger
    runtime = Runtime(
        telemetry=TelemetryConfig(
            logging=LoggingConfig(
                filter=TelemetryFilter(core_level=log_settings.workflow_log_level.upper(), other_level=log_settings.workflow_log_level.upper()),
                forwarding=LogForwardingConfig(logger=logging.getLogger()),
            )
        )
    )
    Runtime.set_default(runtime)

DEFAULT_PASSTHROUGH_MODULES = (
    "app",
    "atlas_shared_app",
    "pydantic",
    "pydantic_core",
    "pydantic_core._pydantic_core",
    "pydantic_core.core_schema",
    "sqlmodel",
    "sqlalchemy",
    "annotated_types",
)

def get_sandboxed_workflow_runner(passthrough_modules: tuple[str, ...] = DEFAULT_PASSTHROUGH_MODULES):
    return SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules(*passthrough_modules)
    )

async def get_workflow_client(workflow_settings: AtlasWorkflowSettings) -> Client:
    return await Client.connect(
        workflow_settings.temporal_address,
        api_key=workflow_settings.secret_temporal_api_key.get_secret_value(),
        namespace=workflow_settings.temporal_namespace,
        tls=True,
        data_converter=pydantic_data_converter,
        # data_converter=dataclasses.replace(
        #     temporalio.converter.default(), payload_codec=EncryptionCodec()
        # ),
    )
