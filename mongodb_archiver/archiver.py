"""
MongoDB Archiver - Core archiving logic with Change Stream support
"""
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import time
import json
from bson import json_util, ObjectId

from config import Config
from logger import setup_logger


class OrderArchiver:
    """Main class for archiving delivered orders"""
    
    def __init__(self, config: Config, logger=None):
        self.config = config
        self.logger = logger or setup_logger(__name__)
        self.client = None
        self.db = None
        
        # Statistics
        self.stats = {
            'found': 0,
            'archived': 0,
            'duplicates': 0,
            'errors': 0,
            'incomplete': 0
        }
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Don't log the URI for security
            self.logger.info("Connecting to MongoDB...")
            self.client = MongoClient(
                self.config.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.config.database_name]
            
            self.logger.info(f"✅ Connected to database: {self.config.database_name}")
            return True
            
        except ConnectionFailure as e:
            self.logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error during connection: {e}")
            return False
    
    def ensure_indexes(self):
        """Create necessary indexes for performance"""
        try:
            self.logger.info("Ensuring indexes...")
            
            # Index on Historique for fast duplicate detection
            self.db[self.config.collection_historique].create_index(
                [("numero_commande", ASCENDING)],
                unique=True,
                name="idx_numero_commande_unique"
            )
            
            # Index on Commande for status queries
            self.db[self.config.collection_commande].create_index(
                [("status", ASCENDING)],
                name="idx_status"
            )
            
            # Index on date_commande for date range queries
            self.db[self.config.collection_commande].create_index(
                [("date_commande", ASCENDING)],
                name="idx_date_commande"
            )
            
            self.logger.info("✅ Indexes created/verified")
            
        except Exception as e:
            self.logger.warning(f"⚠️  Could not create indexes: {e}")
    
    def get_enrichment_pipeline(self, numero_commande: str) -> List[Dict]:
        """
        Build aggregation pipeline for enriching order data
        
        Args:
            numero_commande: Order number to match
            
        Returns:
            Aggregation pipeline
        """
        return [
            {"$match": {"numero_commande": numero_commande}},
            {
                "$lookup": {
                    "from": self.config.collection_client,
                    "localField": "id_client",
                    "foreignField": "id_client",
                    "as": "client"
                }
            },
            {
                "$lookup": {
                    "from": self.config.collection_livreur,
                    "localField": "id_livreur",
                    "foreignField": "id_livreur",
                    "as": "livreur"
                }
            },
            {
                "$lookup": {
                    "from": self.config.collection_restaurants,
                    "localField": "id_restaurant",
                    "foreignField": "id_restaurant",
                    "as": "restaurant"
                }
            },
            {
                "$lookup": {
                    "from": self.config.collection_menu,
                    "localField": "id_menu",
                    "foreignField": "id_menu",
                    "as": "menu"
                }
            },
            {
                "$addFields": {
                    "client": {"$arrayElemAt": ["$client", 0]},
                    "livreur": {"$arrayElemAt": ["$livreur", 0]},
                    "restaurant": {"$arrayElemAt": ["$restaurant", 0]},
                    "menu": {"$arrayElemAt": ["$menu", 0]}
                }
            },
            {
                "$project": {
                    "numero_commande": 1,
                    "id_commande": 1,
                    "nom_client": {
                        "$cond": {
                            "if": {"$ne": ["$client", None]},
                            "then": {"$concat": [
                                {"$ifNull": ["$client.Prénom", ""]},
                                " ",
                                {"$ifNull": ["$client.Nom", ""]}
                            ]},
                            "else": {"$ifNull": ["$Nom", "Client inconnu"]}
                        }
                    },
                    "email_client": "$client.Email",
                    "telephone_client": "$client.Téléphone",
                    "nom_livreur": {
                        "$cond": {
                            "if": {"$ne": ["$livreur", None]},
                            "then": {"$concat": [
                                {"$ifNull": ["$livreur.Prénom", ""]},
                                " ",
                                {"$ifNull": ["$livreur.Nom", ""]}
                            ]},
                            "else": "Livreur non assigné"
                        }
                    },
                    "nom_restaurant": {
                        "$ifNull": ["$restaurant.name", "Restaurant non spécifié"]
                    },
                    "adresse_restaurant": "$restaurant.address",
                    "nom_menu": {
                        "$cond": {
                            "if": {"$ne": ["$menu", None]},
                            "then": "$menu.name",
                            "else": {"$ifNull": ["$Produit", "Menu non spécifié"]}
                        }
                    },
                    "prix_menu": {"$ifNull": ["$menu.price", 0]},
                    "adresse_livraison": 1,
                    "adresse_commande": 1,
                    "coût_commande": 1,
                    "rémunération_livreur": 1,
                    "moyen_de_payement": 1,
                    "status": 1,
                    "date_commande": 1,
                    "temps_estimee": 1
                }
            }
        ]
    
    def check_completeness(self, order: Dict) -> Tuple[bool, List[str]]:
        """
        Check if order document is complete
        
        Args:
            order: Order document
            
        Returns:
            Tuple of (is_complete, missing_fields)
        """
        missing_fields = []
        required_fields = [
            'nom_client', 'nom_livreur', 'nom_restaurant', 
            'nom_menu', 'coût_commande'
        ]
        
        for field in required_fields:
            value = order.get(field)
            if value is None or value == "" or \
               value in ["Client inconnu", "Livreur non assigné", 
                        "Restaurant non spécifié", "Menu non spécifié"]:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    def enrich_order(self, numero_commande: str) -> Optional[Dict]:
        """
        Enrich order with related data
        
        Args:
            numero_commande: Order number
            
        Returns:
            Enriched order document or None if error
        """
        try:
            pipeline = self.get_enrichment_pipeline(numero_commande)
            result = list(self.db[self.config.collection_commande].aggregate(pipeline))
            
            if not result:
                self.logger.warning(f"⚠️  No data found for order {numero_commande}")
                return None
            
            order = result[0]
            
            # Add metadata
            order["date_archivage"] = datetime.now()
            order["archived_by"] = self.config.get_archived_by_tag()
            
            # Check completeness
            is_complete, missing = self.check_completeness(order)
            order["incomplete"] = not is_complete
            if missing:
                order["missing_fields"] = missing
                self.stats['incomplete'] += 1
                self.logger.debug(f"Order {numero_commande} is incomplete: {missing}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ Error enriching order {numero_commande}: {e}")
            self.stats['errors'] += 1
            return None
    
    def archive_orders_batch(self, orders: List[Dict], dry_run: bool = False) -> int:
        """
        Archive a batch of orders
        
        Args:
            orders: List of enriched order documents
            dry_run: If True, don't actually insert
            
        Returns:
            Number of orders archived
        """
        if not orders:
            return 0
        
        archived_count = 0
        
        try:
            if dry_run:
                self.logger.info(f"[DRY-RUN] Would archive {len(orders)} orders")
                for order in orders:
                    self.logger.debug(f"[DRY-RUN] {order['numero_commande']}")
                return len(orders)
            
            # Bulk insert with ordered=False to continue on duplicate key errors
            try:
                result = self.db[self.config.collection_historique].insert_many(
                    orders,
                    ordered=False
                )
                archived_count = len(result.inserted_ids)
                self.logger.info(f"✅ Archived {archived_count} orders")
                
            except PyMongoError as e:
                # Handle duplicate key errors
                if hasattr(e, 'details') and 'writeErrors' in e.details:
                    write_errors = e.details['writeErrors']
                    duplicates = sum(1 for err in write_errors if err['code'] == 11000)
                    archived_count = len(orders) - duplicates
                    self.stats['duplicates'] += duplicates
                    self.logger.info(
                        f"✅ Archived {archived_count} orders, "
                        f"skipped {duplicates} duplicates"
                    )
                else:
                    raise
            
            return archived_count
            
        except Exception as e:
            self.logger.error(f"❌ Error archiving batch: {e}")
            self.stats['errors'] += 1
            return 0
    
    def find_delivered_orders(
        self, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[str]:
        """
        Find all delivered orders
        
        Args:
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of order numbers
        """
        query = {"status": "livrée"}
        
        if date_from or date_to:
            query["date_commande"] = {}
            if date_from:
                query["date_commande"]["$gte"] = date_from
            if date_to:
                query["date_commande"]["$lte"] = date_to
        
        try:
            orders = self.db[self.config.collection_commande].find(
                query,
                {"numero_commande": 1, "_id": 0}
            )
            
            order_numbers = [o["numero_commande"] for o in orders if "numero_commande" in o]
            self.stats['found'] = len(order_numbers)
            
            self.logger.info(f"📦 Found {len(order_numbers)} delivered orders")
            return order_numbers
            
        except Exception as e:
            self.logger.error(f"❌ Error finding orders: {e}")
            return []
    
    def archive_all(
        self, 
        dry_run: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Archive all delivered orders
        
        Args:
            dry_run: If True, don't actually insert
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            Statistics dictionary
        """
        self.logger.info("🚀 Starting batch archiving process...")
        
        if dry_run:
            self.logger.info("🔍 DRY-RUN MODE: No changes will be made")
        
        # Find delivered orders
        order_numbers = self.find_delivered_orders(date_from, date_to)
        
        if not order_numbers:
            self.logger.info("✨ No orders to archive")
            return self.stats
        
        # Process in batches
        batch = []
        total_processed = 0
        
        for numero in order_numbers:
            # Enrich order
            enriched = self.enrich_order(numero)
            if enriched:
                batch.append(enriched)
            
            # Archive when batch is full
            if len(batch) >= self.config.batch_size:
                archived = self.archive_orders_batch(batch, dry_run)
                self.stats['archived'] += archived
                total_processed += len(batch)
                batch = []
                
                self.logger.info(
                    f"📊 Progress: {total_processed}/{len(order_numbers)} processed"
                )
        
        # Archive remaining orders
        if batch:
            archived = self.archive_orders_batch(batch, dry_run)
            self.stats['archived'] += archived
        
        self.logger.info("✅ Batch archiving completed")
        return self.stats
    
    def get_stats_summary(self) -> str:
        """Get formatted statistics summary"""
        return f"""
{'='*70}
📊 ARCHIVING STATISTICS
{'='*70}
Found:       {self.stats['found']} orders
Archived:    {self.stats['archived']} orders
Duplicates:  {self.stats['duplicates']} orders
Incomplete:  {self.stats['incomplete']} orders
Errors:      {self.stats['errors']} errors
{'='*70}
"""
    
    def export_sample(self, filename: str, count: int = 5):
        """
        Export sample archived orders to JSON file
        
        Args:
            filename: Output filename
            count: Number of samples to export
        """
        try:
            samples = list(
                self.db[self.config.collection_historique]
                .find()
                .limit(count)
            )
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(
                    samples,
                    f,
                    indent=2,
                    default=json_util.default,
                    ensure_ascii=False
                )
            
            self.logger.info(f"📄 Exported {len(samples)} samples to {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting samples: {e}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("🔌 MongoDB connection closed")
