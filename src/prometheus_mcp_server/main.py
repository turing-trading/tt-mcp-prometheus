#!/usr/bin/env python
import sys
import signal
import threading
import dotenv
from prometheus_mcp_server.server import mcp, config
from prometheus_mcp_server.logging_config import setup_logging, get_logger

# Initialize structured logging
logger = setup_logging()

# Global shutdown event
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    """Handle SIGTERM and SIGINT signals for graceful shutdown."""
    signal_name = signal.Signals(signum).name
    logger.info("Received shutdown signal", signal=signal_name)
    shutdown_event.set()

def setup_environment():
    if dotenv.load_dotenv():
        logger.info("Environment configuration loaded", source=".env file")
    else:
        logger.info("Environment configuration loaded", source="environment variables", note="No .env file found")

    if not config.url:
        logger.error(
            "Missing required configuration",
            error="PROMETHEUS_URL environment variable is not set",
            suggestion="Please set it to your Prometheus server URL",
            example="http://your-prometheus-server:9090"
        )
        return False
    
    # Determine authentication method
    auth_method = "none"
    if config.username and config.password:
        auth_method = "basic_auth"
    elif config.token:
        auth_method = "bearer_token"
    
    logger.info(
        "Prometheus configuration validated",
        server_url=config.url,
        authentication=auth_method,
        org_id=config.org_id if config.org_id else None
    )
    
    return True

def run_server():
    """Main entry point for the Prometheus MCP Server"""
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed, exiting")
        sys.exit(1)
    
    logger.info("Starting Prometheus MCP Server", transport="stdio")
    
    # Run the server in a separate thread to allow signal handling
    server_thread = threading.Thread(target=lambda: mcp.run(transport="stdio"))
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for shutdown signal
    try:
        shutdown_event.wait()
        logger.info("Shutdown initiated, stopping server gracefully")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping server")
    finally:
        logger.info("Server shutdown complete")
        sys.exit(0)

if __name__ == "__main__":
    run_server()
