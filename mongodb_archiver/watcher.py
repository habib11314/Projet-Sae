"""
MongoDB Change Stream Watcher - Real-time order archiving
Watches for status changes and archives orders automatically
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime
import json
import time
from pathlib import Path
from typing import Optional, Dict

from config import Config
from logger import setup_logger
from archiver import OrderArchiver


class OrderWatcher:
    """Watch for order status changes using MongoDB Change Streams"""
    
    def __init__(self, config: Config, logger=None):
        self.config = config
        self.logger = logger or setup_logger(__name__)
        self.archiver = OrderArchiver(config, logger)
        self.resume_token = None
        self.resume_token_file = Path(config.watch_resume_token_file)
        
    def load_resume_token(self) -> Optional[Dict]:
        """Load resume token from file for fault tolerance"""
        try:
            if self.resume_token_file.exists():
                with open(self.resume_token_file, 'r') as f:
                    token_data = json.load(f)
                    self.logger.info("📋 Loaded resume token from file")
                    return token_data
        except Exception as e:
            self.logger.warning(f"⚠️  Could not load resume token: {e}")
        return None
    
    def save_resume_token(self, token: Dict):
        """Save resume token to file for fault tolerance"""
        try:
            self.resume_token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.resume_token_file, 'w') as f:
                json.dump(token, f)
            self.logger.debug("💾 Saved resume token")
        except Exception as e:
            self.logger.warning(f"⚠️  Could not save resume token: {e}")
    
    def should_archive(self, change: Dict) -> bool:
        """
        Determine if a change event should trigger archiving
        
        Args:
            change: Change stream event
            
        Returns:
            True if order should be archived
        """
        operation_type = change.get('operationType')
        
        # Archive on insert or update
        if operation_type not in ['insert', 'update', 'replace']:
            return False
        
        # Get the full document
        full_document = change.get('fullDocument', {})
        status = full_document.get('status', '')
        
        # Archive if status is "livrée"
        if status == 'livrée':
            self.logger.debug(f"✅ Status is 'livrée', will archive")
            return True
        
        # For updates, also check if status changed TO "livrée"
        if operation_type == 'update':
            updated_fields = change.get('updateDescription', {}).get('updatedFields', {})
            if 'status' in updated_fields and updated_fields['status'] == 'livrée':
                self.logger.debug(f"✅ Status changed to 'livrée', will archive")
                return True
        
        return False
    
    def process_change(self, change: Dict):
        """
        Process a change stream event
        
        Args:
            change: Change stream event
        """
        try:
            operation_type = change.get('operationType')
            full_document = change.get('fullDocument', {})
            numero_commande = full_document.get('numero_commande', 'N/A')
            
            self.logger.info(
                f"🔔 Change detected: {operation_type} on order {numero_commande}"
            )
            
            if self.should_archive(change):
                # Enrich and archive the order
                enriched = self.archiver.enrich_order(numero_commande)
                
                if enriched:
                    archived = self.archiver.archive_orders_batch([enriched])
                    
                    if archived > 0:
                        self.logger.info(
                            f"✅ Successfully archived order {numero_commande} in real-time"
                        )
                        self.archiver.stats['archived'] += 1
                    else:
                        self.logger.debug(
                            f"⚠️  Order {numero_commande} already archived (duplicate)"
                        )
                        self.archiver.stats['duplicates'] += 1
                else:
                    self.logger.error(
                        f"❌ Failed to enrich order {numero_commande}"
                    )
                    self.archiver.stats['errors'] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error processing change: {e}")
            self.archiver.stats['errors'] += 1
    
    def watch(self, resume: bool = True):
        """
        Start watching for changes using Change Streams
        
        Args:
            resume: If True, attempt to resume from last position
        """
        if not self.archiver.connect():
            self.logger.error("❌ Cannot start watcher: connection failed")
            return
        
        self.archiver.ensure_indexes()
        
        # Load resume token if requested
        if resume:
            self.resume_token = self.load_resume_token()
        
        self.logger.info("👀 Starting Change Stream watcher...")
        self.logger.info(f"📡 Watching collection: {self.config.collection_commande}")
        self.logger.info("💡 Press Ctrl+C to stop")
        
        # Pipeline to filter only relevant changes
        pipeline = [
            {
                '$match': {
                    'operationType': {'$in': ['insert', 'update', 'replace']},
                    '$or': [
                        {'fullDocument.status': 'livrée'},
                        {'updateDescription.updatedFields.status': 'livrée'}
                    ]
                }
            }
        ]
        
        retry_delay = 1
        max_retry_delay = 60
        
        while True:
            try:
                # Open change stream with resume token
                watch_options = {
                    'pipeline': pipeline,
                    'full_document': 'updateLookup'
                }
                
                if self.resume_token:
                    watch_options['resume_after'] = self.resume_token
                    self.logger.info("🔄 Resuming from saved position")
                
                with self.archiver.db[self.config.collection_commande].watch(**watch_options) as stream:
                    self.logger.info("✅ Change Stream opened successfully")
                    retry_delay = 1  # Reset retry delay on success
                    
                    for change in stream:
                        # Process the change
                        self.process_change(change)
                        
                        # Save resume token periodically
                        self.resume_token = stream.resume_token
                        self.save_resume_token(self.resume_token)
                
            except KeyboardInterrupt:
                self.logger.info("\n⏹️  Stopping watcher (user interrupted)")
                break
                
            except PyMongoError as e:
                self.logger.error(f"❌ Change Stream error: {e}")
                self.logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
                # Exponential backoff
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                self.logger.error(f"❌ Unexpected error: {e}")
                self.logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        # Print final stats
        self.logger.info(self.archiver.get_stats_summary())
        self.archiver.close()
    
    def watch_simple(self):
        """
        Simple watch mode without resume token (for testing)
        Watches all operations on the collection
        """
        if not self.archiver.connect():
            self.logger.error("❌ Cannot start watcher: connection failed")
            return
        
        self.logger.info("👀 Starting simple watch mode...")
        self.logger.info(f"📡 Watching collection: {self.config.collection_commande}")
        self.logger.info("💡 Press Ctrl+C to stop")
        
        try:
            with self.archiver.db[self.config.collection_commande].watch(
                full_document='updateLookup'
            ) as stream:
                for change in stream:
                    operation = change.get('operationType')
                    doc = change.get('fullDocument', {})
                    numero = doc.get('numero_commande', 'N/A')
                    status = doc.get('status', 'N/A')
                    
                    self.logger.info(
                        f"🔔 {operation}: order {numero} - status: {status}"
                    )
                    
                    if self.should_archive(change):
                        self.process_change(change)
        
        except KeyboardInterrupt:
            self.logger.info("\n⏹️  Stopping watcher")
        
        finally:
            self.archiver.close()
