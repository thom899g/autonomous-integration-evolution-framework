"""
Firebase manager for state management and real-time data streaming.
Handles all Firebase operations with robust error handling and connection management.
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
from firebase_admin.exceptions import FirebaseError
from typing import Dict, Any, List, Optional, Callable
import json
import time
from datetime import datetime
import threading
from loguru import logger

class FirebaseManager:
    """Manages Firebase connections and operations."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.app = None
            self.firestore_client = None
            self.realtime_db = None
            self._listeners = {}
            self._initialized = True
    
    def initialize(self, firebase_config: Dict[str, Any]) -> bool:
        """
        Initialize Firebase connection.
        
        Args:
            firebase_config: Firebase configuration dictionary
            
        Returns:
            bool: True if initialization successful
            
        Raises:
            ValueError: If configuration is invalid
            FirebaseError: If Firebase initialization fails
        """
        try:
            # Validate configuration
            required_keys = ['project_id', 'private_key', 'client_email']
            for key in required_keys:
                if key not in firebase_config:
                    raise ValueError(f"Missing required Firebase config key: {key}")
            
            # Create credentials
            cred_dict = {
                "type": "service_account",
                "project_id": firebase_config['project_id'],
                "private_key_id": firebase_config.get('private_key_id', ''),
                "private_key": firebase_config['private_key'],
                "client_email": firebase_config['client_email'],
                "client_id": firebase_config.get('client_id', ''),
                "auth_uri": firebase_config.get('auth_uri', "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": firebase_config.get('token_uri', "https://oauth2.googleapis.com/token"),
                "auth_provider_x509_cert_url": firebase_config.get('auth_provider_x509_cert_url', 
                    "https://www.googleapis.com/oauth2/v1/certs"),
                "client_x509_cert_url": firebase_config.get('client_x509_cert_url', 
                    "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk.iam.gserviceaccount.com")
            }
            
            cred = credentials.Certificate(cred_dict)
            
            # Initialize Firebase app
            if not firebase_admin._apps:
                self.app = firebase_admin.initialize_app(
                    cred,
                    {
                        'projectId': firebase_config['project_id'],
                        'databaseURL': f"https://{firebase_config['project_id']}.firebaseio.com"
                    }
                )
            else:
                self.app = firebase_admin.get_app()
            
            # Initialize clients
            self.firestore_client = firestore.client()
            self.realtime_db = db.reference()
            
            logger.info(f"Firebase initialized successfully for project: {firebase_config['project_id']}")
            return True
            
        except ValueError as ve:
            logger.error(f"Configuration validation failed: {ve}")
            raise
        except FirebaseError as fe:
            logger.error(f"Firebase initialization failed: {fe}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Firebase initialization: {e}")
            raise
    
    def save_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """
        Save document to Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            data: Document data
            
        Returns:
            bool: True if successful
            
        Raises