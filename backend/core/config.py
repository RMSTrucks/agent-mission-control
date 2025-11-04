"""
Configuration Management for Agent Mission Control

Loads configuration from YAML file and environment variables.
Provides type-safe configuration objects using Pydantic.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class SystemConfig(BaseModel):
    """System-level configuration"""
    name: str = "Agent Mission Control"
    version: str = "0.1.0"
    environment: str = "development"


class APIConfig(BaseModel):
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"


class DatabaseConfig(BaseModel):
    """Database configuration"""
    type: str = "sqlite"
    path: str = "data/database.db"
    url: Optional[str] = None


class SuperOptiXConfig(BaseModel):
    """SuperOptiX integration configuration"""
    enabled: bool = True
    default_optimizer: str = "GEPA"
    default_auto_level: str = "medium"
    agents_path: str = "agents/"
    pipelines_path: str = "pipelines/"


class VAPIConfig(BaseModel):
    """VAPI integration configuration"""
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: str = "https://api.vapi.ai"


class CloseConfig(BaseModel):
    """Close CRM integration configuration"""
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: str = "https://api.close.com/api/v1"


class MemoryConfig(BaseModel):
    """Memory systems configuration"""
    temporal_enabled: bool = True
    temporal_mcp_server: str = "temporal-memory"
    temporal_tiers: List[str] = ["fact", "preference", "context"]
    hybrid_enabled: bool = True
    hybrid_mcp_server: str = "hybrid-intelligence-mcp"


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    path: str = "data/logs/"
    rotation: str = "1 day"
    retention: str = "30 days"


class Settings(BaseModel):
    """Main application settings"""
    system: SystemConfig
    api: APIConfig
    database: DatabaseConfig
    superoptix: SuperOptiXConfig
    vapi: VAPIConfig
    close: CloseConfig
    memory: MemoryConfig
    logging: LoggingConfig

    @classmethod
    def load_from_yaml(cls, config_path: str = "config/settings.yaml") -> "Settings":
        """
        Load settings from YAML file with environment variable substitution.

        Args:
            config_path: Path to settings.yaml file

        Returns:
            Settings object with loaded configuration
        """
        # Get project root (parent of backend directory)
        if os.path.exists("/home/user/agent-mission-control"):
            project_root = Path("/home/user/agent-mission-control")
        else:
            project_root = Path(__file__).parent.parent.parent

        yaml_path = project_root / config_path

        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        # Load YAML
        with open(yaml_path, 'r') as f:
            raw_config = yaml.safe_load(f)

        # Process environment variable substitutions
        processed_config = cls._substitute_env_vars(raw_config)

        # Parse nested configuration
        return cls(
            system=SystemConfig(**processed_config.get("system", {})),
            api=APIConfig(**processed_config.get("api", {})),
            database=DatabaseConfig(**processed_config.get("database", {})),
            superoptix=SuperOptiXConfig(**processed_config.get("superoptix", {})),
            vapi=VAPIConfig(
                enabled=processed_config.get("vapi", {}).get("enabled", True),
                api_key=processed_config.get("vapi", {}).get("api_key"),
                base_url=processed_config.get("vapi", {}).get("base_url", "https://api.vapi.ai")
            ),
            close=CloseConfig(
                enabled=processed_config.get("close", {}).get("enabled", True),
                api_key=processed_config.get("close", {}).get("api_key"),
                base_url=processed_config.get("close", {}).get("base_url", "https://api.close.com/api/v1")
            ),
            memory=MemoryConfig(
                temporal_enabled=processed_config.get("memory", {}).get("temporal", {}).get("enabled", True),
                temporal_mcp_server=processed_config.get("memory", {}).get("temporal", {}).get("mcp_server", "temporal-memory"),
                temporal_tiers=processed_config.get("memory", {}).get("temporal", {}).get("tiers", ["fact", "preference", "context"]),
                hybrid_enabled=processed_config.get("memory", {}).get("hybrid", {}).get("enabled", True),
                hybrid_mcp_server=processed_config.get("memory", {}).get("hybrid", {}).get("mcp_server", "hybrid-intelligence-mcp")
            ),
            logging=LoggingConfig(**processed_config.get("logging", {}))
        )

    @staticmethod
    def _substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively substitute environment variables in config.

        Variables in format ${VAR_NAME} will be replaced with os.environ.get("VAR_NAME")
        """
        if isinstance(config, dict):
            return {k: Settings._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [Settings._substitute_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]  # Remove ${ and }
            return os.environ.get(env_var, None)
        else:
            return config


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create global settings instance.

    Returns:
        Settings object with loaded configuration
    """
    global _settings
    if _settings is None:
        _settings = Settings.load_from_yaml()
    return _settings


def reload_settings() -> Settings:
    """
    Force reload settings from file.

    Returns:
        Newly loaded Settings object
    """
    global _settings
    _settings = Settings.load_from_yaml()
    return _settings


# Module-level test
if __name__ == "__main__":
    print("Testing configuration loading...")
    try:
        settings = get_settings()
        print(f"SUCCESS: Loaded settings for {settings.system.name} v{settings.system.version}")
        print(f"API will run on {settings.api.host}:{settings.api.port}")
        print(f"SuperOptiX enabled: {settings.superoptix.enabled}")
        print(f"VAPI enabled: {settings.vapi.enabled}")
    except Exception as e:
        print(f"ERROR: {e}")
