#!/usr/bin/env python3
"""
Configuration management for Dependency Analyzer MCP Server.

This module provides a unified configuration system that supports:
1. YAML configuration files
2. Environment variables as fallback
3. Command-line argument overrides
"""

import os
import sys
import yaml
import argparse
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Default configuration paths in order of preference
DEFAULT_CONFIG_PATHS = [
    "/app/config/config.yaml",  # Docker container path
    "./config.yaml",            # Current directory
    "./config/config.yaml",     # Config subdirectory
]

# Default configuration values
DEFAULT_CONFIG = {
    "server": {
        "port": 8000,
        "host": "0.0.0.0",
        "mode": "http",  # "http" or "stdio"
    },
    "projects": {
        "projects_dir": "/app/projects",
        "analysis_dir": "/app/analysis",
    },
    "logging": {
        "level": "INFO",
        "format": "json",
    },
    "auth": {
        "enabled": False,
        "username": None,
        "password": None,
    }
}

class Config:
    """Configuration manager for the MCP server."""
    
    def __init__(self):
        """Initialize the configuration with default values."""
        self._config = DEFAULT_CONFIG.copy()
        self._config_file_path = None
        self._args = None
    
    def load(self, config_path: Optional[str] = None, parse_args: bool = True) -> None:
        """
        Load configuration from a YAML file, environment variables, and command-line args.
        
        Args:
            config_path: Optional path to a YAML configuration file
            parse_args: Whether to parse command-line arguments
        """
        # First load from YAML file
        self._load_from_yaml(config_path)
        
        # Then override with environment variables
        self._load_from_env()
        
        # Finally override with command-line arguments
        if parse_args:
            self._load_from_args()
    
    def _load_from_yaml(self, config_path: Optional[str] = None) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to a YAML configuration file. If None, will try default paths.
        """
        paths_to_try = []
        
        # Add specified path first if provided
        if config_path:
            paths_to_try.append(config_path)
        
        # Add default paths
        paths_to_try.extend(DEFAULT_CONFIG_PATHS)
        
        # Try each path in order
        for path in paths_to_try:
            try:
                with open(path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self._merge_config(yaml_config)
                        self._config_file_path = path
                        return
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error loading config from {path}: {e}", file=sys.stderr)
                continue
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Server configuration
        if os.environ.get("PORT"):
            self._config["server"]["port"] = int(os.environ.get("PORT"))
        
        if os.environ.get("HOST"):
            self._config["server"]["host"] = os.environ.get("HOST")
        
        if os.environ.get("MCP_MODE"):
            self._config["server"]["mode"] = os.environ.get("MCP_MODE").lower()
        
        # Project directories
        if os.environ.get("PROJECTS_DIR"):
            self._config["projects"]["projects_dir"] = os.environ.get("PROJECTS_DIR")
        
        if os.environ.get("ANALYSIS_DIR"):
            self._config["projects"]["analysis_dir"] = os.environ.get("ANALYSIS_DIR")
        
        # Logging configuration
        if os.environ.get("LOG_LEVEL"):
            self._config["logging"]["level"] = os.environ.get("LOG_LEVEL").upper()
        
        # Authentication (if implemented)
        if os.environ.get("ENABLE_AUTH"):
            self._config["auth"]["enabled"] = os.environ.get("ENABLE_AUTH").lower() == "true"
        
        if os.environ.get("AUTH_USERNAME"):
            self._config["auth"]["username"] = os.environ.get("AUTH_USERNAME")
        
        if os.environ.get("AUTH_PASSWORD"):
            self._config["auth"]["password"] = os.environ.get("AUTH_PASSWORD")
    
    def _load_from_args(self) -> None:
        """Load configuration from command-line arguments."""
        parser = argparse.ArgumentParser(description="Dependency Analyzer MCP Server")
        
        # Server configuration
        parser.add_argument("--port", type=int, help="Server port")
        parser.add_argument("--host", help="Server host")
        parser.add_argument("--mode", choices=["http", "stdio"], help="MCP server mode")
        
        # Project directories
        parser.add_argument("--projects-dir", help="Projects directory")
        parser.add_argument("--analysis-dir", help="Analysis results directory")
        
        # Logging configuration
        parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                           help="Logging level")
        
        # Config file path
        parser.add_argument("--config", help="Path to YAML configuration file")
        
        # Parse arguments
        args, _ = parser.parse_known_args()
        self._args = args
        
        # Reload from config file if specified
        if args.config:
            self._load_from_yaml(args.config)
        
        # Apply other command-line arguments
        if args.port:
            self._config["server"]["port"] = args.port
        
        if args.host:
            self._config["server"]["host"] = args.host
        
        if args.mode:
            self._config["server"]["mode"] = args.mode
        
        if args.projects_dir:
            self._config["projects"]["projects_dir"] = args.projects_dir
        
        if args.analysis_dir:
            self._config["projects"]["analysis_dir"] = args.analysis_dir
        
        if args.log_level:
            self._config["logging"]["level"] = args.log_level
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge a new configuration dictionary into the existing configuration.
        
        Args:
            new_config: New configuration to merge in
        """
        def _merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
            """Deep merge two dictionaries."""
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    _merge_dicts(base[key], value)
                else:
                    base[key] = value
            return base
        
        _merge_dicts(self._config, new_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., "server.port")
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to configuration."""
        return self.get(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the entire configuration as a dictionary."""
        return self._config.copy()
    
    def get_config_file_path(self) -> Optional[str]:
        """Get the path of the loaded configuration file."""
        return self._config_file_path

# Create a global configuration instance
config = Config()

def initialize_config(config_path: Optional[str] = None, parse_args: bool = True) -> Config:
    """
    Initialize the global configuration.
    
    Args:
        config_path: Optional path to a YAML configuration file
        parse_args: Whether to parse command-line arguments
        
    Returns:
        The initialized configuration object
    """
    config.load(config_path, parse_args)
    return config 