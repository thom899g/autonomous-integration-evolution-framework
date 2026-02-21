"""
Configuration management for the Autonomous Integration Evolution Framework.
Centralizes all configuration to ensure consistency and easy maintenance.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation."""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url: str = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk.iam.gserviceaccount.com"
    
    @classmethod
    def from_env(cls) -> Optional['FirebaseConfig']:
        """Load Firebase config from environment variables."""
        try:
            return cls(
                project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
                private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                private_key=os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                client_email=os.getenv('FIREBASE_CLIENT_EMAIL', ''),
                client_id=os.getenv('FIREBASE_CLIENT_ID', ''),
                client_x509_cert_url=os.getenv('FIREBASE_CLIENT_CERT_URL', '')
            )
        except Exception as e:
            print(f"Error loading Firebase config: {e}")
            return None

@dataclass
class FrameworkConfig:
    """Main framework configuration."""
    # Learning parameters
    learning_rate: float = 0.01
    exploration_rate: float = 0.1
    memory_size: int = 10000
    batch_size: int = 32
    
    # Integration parameters
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: int = 30
    
    # Evolution parameters
    strategy_evaluation_interval: int = 3600  # seconds
    performance_threshold: float = 0.8
    adaptation_threshold: float = 0.15
    
    # Firebase collections
    firebase_collections: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default collections."""
        if self.firebase_collections is None:
            self.firebase_collections = {
                'integration_logs': 'integration_logs',
                'strategies': 'strategies',
                'performance_metrics': 'performance_metrics',
                'adaptation_history': 'adaptation_history',
                'platform_configs': 'platform_configs'
            }

class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or Path.home() / '.aief_config.json'
        self.framework_config = FrameworkConfig()
        self.firebase_config = FirebaseConfig.from_env()
        
    def validate(self) -> bool:
        """Validate all configurations."""
        if not self.firebase_config:
            print("Firebase configuration is missing")
            return False
            
        if not self.firebase_config.project_id:
            print("Firebase project ID is required")
            return False
            
        return True
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            config_data = {
                'framework': self.framework_config.__dict__,
                'firebase': self.firebase_config.__dict__ if self.firebase_config else {}
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load(self) -> bool:
        """Load configuration from file."""
        try:
            if not os.path.exists(self.config_path):
                return False
                
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
                
            if 'framework' in config_data:
                self.framework_config = FrameworkConfig(**config_data['framework'])
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False