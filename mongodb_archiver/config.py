"""
Configuration module for MongoDB Order Archiver
Handles environment variables and settings
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration class for the archiver"""
    
    # MongoDB connection
    mongodb_uri: str
    database_name: str = "Ubereats"
    
    # Collection names
    collection_commande: str = "Commande"
    collection_historique: str = "Historique"
    collection_client: str = "Client"
    collection_livreur: str = "Livreur"
    collection_restaurants: str = "Restaurants"
    collection_menu: str = "Menu"
    
    # Archiving settings
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: int = 2  # seconds
    
    # Change Stream settings
    watch_enabled: bool = True
    watch_resume_token_file: str = ".resume_token.json"
    
    # Script metadata
    script_name: str = "archive_commandes.py"
    script_version: str = "2.0.0"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            raise ValueError(
                "MONGODB_URI environment variable is required. "
                "Set it in your environment or create a .env file."
            )
        
        return cls(
            mongodb_uri=mongodb_uri,
            database_name=os.getenv('MONGODB_DATABASE', 'Ubereats'),
            batch_size=int(os.getenv('BATCH_SIZE', '100')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            retry_delay=int(os.getenv('RETRY_DELAY', '2')),
            watch_enabled=os.getenv('WATCH_ENABLED', 'true').lower() == 'true'
        )
    
    @classmethod
    def for_simulation(cls, local_uri: str = "mongodb://localhost:27017/") -> 'Config':
        """Create config for local simulation/testing"""
        return cls(
            mongodb_uri=local_uri,
            database_name="Ubereats_Test"
        )
    
    def get_archived_by_tag(self) -> str:
        """Returns the archived_by tag"""
        return f"{self.script_name} v{self.script_version}"
