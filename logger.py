import os
import sys
import logging
import warnings
from pathlib import Path

# Attempt to load dotenv, but don't fail if the package is missing
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import structlog

# Fetch configuration from environment variables with fallbacks
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_SHOW_CALLSITE = os.getenv('LOG_SHOW_CALLSITE', 'false').lower() == 'true'

def setup_logging(output_path: Path) -> None:
    """
    Setup structured logging configuration for dual-output:
    - Console: Human-readable, colored output
    - File: Machine-readable JSON format
    """
    warnings.filterwarnings("ignore")

    # Force UTF-8 encoding for Windows console to prevent charmap errors with Delta (Δ)
    if sys.platform == 'win32':
        os.system('')  # Enables ANSI escape sequences in Windows terminal
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')

    # 1. Base structlog processors (These run before formatting)
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
    ]
    
    if LOG_SHOW_CALLSITE:
        shared_processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            )
        )

    shared_processors.extend([
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # Key step: Prepare the event dict to be passed to standard logging formatters
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter, 
    ])

    # Configure structlog base
    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 2. Set up formatters for the standard logging handlers
    
    # Human-readable formatter for the console
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
    )
    
    # Machine-readable JSON formatter for the file
    json_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
    )

    # 3. Configure the standard library handlers
    output_path.mkdir(parents=True, exist_ok=True)
    
    # File Handler (Gets JSON, forced to utf-8)
    log_file = output_path / 'processing.log'
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(json_formatter)
    
    # Stream Handler (Gets Colored Console Output)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(console_formatter)

    # 4. Attach to root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance. 
    Use this in your scripts to fetch the logger.
    """
    return structlog.get_logger(name)   