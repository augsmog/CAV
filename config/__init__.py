"""
Configuration management for CAV Model
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration loader and manager"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / 'config.yaml'
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.template.yaml to config.yaml and add your API keys."
            )
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    @property
    def cfb_api_key(self) -> str:
        """Get College Football Data API key"""
        return self.get('collegefootballdata.api_key', '')
    
    @property
    def cfb_base_url(self) -> str:
        """Get College Football Data API base URL"""
        return self.get('collegefootballdata.base_url')
    
    @property
    def db_type(self) -> str:
        """Get database type"""
        return self.get('database.type', 'sqlite')
    
    @property
    def db_path(self) -> str:
        """Get SQLite database path"""
        return self.get('database.sqlite.path', 'database/cav_data.db')
    
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()


# Global config instance
_config = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

