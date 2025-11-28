"""
Test data generator - Creates random orders for testing
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict
from bson import ObjectId
from faker import Faker

from config import Config
from logger import setup_logger


class DataGenerator:
    """Generate realistic test data for MongoDB"""
    
    def __init__(self, config: Config, seed: int = None, logger=None):
        self.config = config
        self.logger = logger or setup_logger(__name__)
        self.fake = Faker(['fr_FR'])
        
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
            self.logger.info(f"🎲 Random seed set to: {seed}")
        
        self.client = None
        self.db = None
    
    def connect(self):
        """Connect to MongoDB"""
        from pymongo import MongoClient
        
        self.logger.info("Connecting to MongoDB...")
        self.client = MongoClient(self.config.mongodb_uri)
        self.db = self.client[self.config.database_name]
        self.logger.info(f"✅ Connected to: {self.config.database_name}")
    
    def generate_clients(self, count: int) -> List[Dict]:
        """Generate random clients"""
        clients = []
        for i in range(count):
            client = {
                "id_client": f"CLI-{i+1:05d}",
                "Nom": self.fake.last_name(),
                "Prénom": self.fake.first_name(),
                "Email": self.fake.email(),
                "Téléphone": self.fake.phone_number(),
                "Adresse": self.fake.address().replace('\n', ', '),
                "date_inscription": self.fake.date_time_between(
                    start_date='-2y',
                    end_date='now'
                )
            }
            clients.append(client)
        return clients
    
    def generate_livreurs(self, count: int) -> List[Dict]:
        """Generate random delivery drivers"""
        livreurs = []
        vehicules = ['Vélo', 'Scooter', 'Voiture', 'Moto']
        
        for i in range(count):
            livreur = {
                "id_livreur": f"LIV-{i+1:05d}",
                "Nom": self.fake.last_name(),
                "Prénom": self.fake.first_name(),
                "Téléphone": self.fake.phone_number(),
                "Email": self.fake.email(),
                "vehicule": random.choice(vehicules),
                "statut": random.choice(['disponible', 'en_course', 'hors_ligne']),
                "note_moyenne": round(random.uniform(3.5, 5.0), 1),
                "date_embauche": self.fake.date_time_between(
                    start_date='-1y',
                    end_date='now'
                )
            }
            livreurs.append(livreur)
        return livreurs
    
    def generate_restaurants(self, count: int) -> List[Dict]:
        """Generate random restaurants"""
        restaurants = []
        cuisines = [
            'Française', 'Italienne', 'Japonaise', 'Chinoise', 
            'Indienne', 'Mexicaine', 'Burger', 'Pizza', 'Sushi', 'Kebab'
        ]
        
        for i in range(count):
            restaurant = {
                "id_restaurant": f"RES-{i+1:05d}",
                "name": f"{self.fake.company()} Restaurant",
                "address": self.fake.address().replace('\n', ', '),
                "cuisine": random.choice(cuisines),
                "note_moyenne": round(random.uniform(3.0, 5.0), 1),
                "temps_preparation_moyen": random.randint(15, 45),
                "telephone": self.fake.phone_number(),
                "horaires": "11:00-23:00"
            }
            restaurants.append(restaurant)
        return restaurants
    
    def generate_menus(self, count: int) -> List[Dict]:
        """Generate random menu items"""
        menus = []
        categories = ['Entrée', 'Plat', 'Dessert', 'Boisson', 'Menu']
        plats = [
            'Salade César', 'Pizza Margherita', 'Burger Classic', 
            'Sushi Mix', 'Pad Thai', 'Couscous', 'Tacos', 
            'Pasta Carbonara', 'Poke Bowl', 'Ramen'
        ]
        
        for i in range(count):
            menu = {
                "id_menu": f"MEN-{i+1:05d}",
                "name": random.choice(plats) if random.random() > 0.3 else self.fake.catch_phrase(),
                "category": random.choice(categories),
                "price": round(random.uniform(5.0, 35.0), 2),
                "description": self.fake.sentence(),
                "disponible": random.choice([True, True, True, False]),
                "temps_preparation": random.randint(10, 40)
            }
            menus.append(menu)
        return menus
    
    def generate_commandes(
        self,
        count: int,
        client_ids: List[str],
        livreur_ids: List[str],
        restaurant_ids: List[str],
        menu_ids: List[str],
        p_delivered: float = 0.3,
        p_null_ids: float = 0.05,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Generate random orders
        
        Args:
            count: Number of orders to generate
            client_ids: List of client IDs
            livreur_ids: List of delivery driver IDs
            restaurant_ids: List of restaurant IDs
            menu_ids: List of menu IDs
            p_delivered: Probability of status being "livrée" (0-1)
            p_null_ids: Probability of missing related IDs (0-1)
            days_back: Number of days to spread orders over
        """
        commandes = []
        statuses = ['en_attente', 'en_preparation', 'en_cours', 'livrée', 'annulée']
        moyens_paiement = ['CB', 'Espèces', 'Paypal', 'Apple Pay', 'Google Pay']
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        for i in range(count):
            # Determine status with weighted probability
            if random.random() < p_delivered:
                status = 'livrée'
            else:
                status = random.choice(statuses)
            
            # Randomly assign or null IDs based on p_null_ids
            id_client = None if random.random() < p_null_ids else random.choice(client_ids)
            id_livreur = None if random.random() < p_null_ids else random.choice(livreur_ids)
            id_restaurant = None if random.random() < p_null_ids else random.choice(restaurant_ids)
            id_menu = None if random.random() < p_null_ids else random.choice(menu_ids)
            
            # Generate dates
            date_commande = start_date + timedelta(
                seconds=random.randint(0, days_back * 24 * 3600)
            )
            
            prix_menu = round(random.uniform(8.0, 40.0), 2)
            frais_livraison = round(random.uniform(1.5, 5.0), 2)
            cout_total = round(prix_menu + frais_livraison, 2)
            remuneration = round(frais_livraison * 0.7, 2)
            
            commande = {
                "numero_commande": f"CMD-2025-{i+1:06d}",
                "id_commande": str(ObjectId()),
                "id_client": id_client,
                "id_livreur": id_livreur,
                "id_restaurant": id_restaurant,
                "id_menu": id_menu,
                "Nom": self.fake.name() if not id_client else None,  # Fallback name
                "Produit": self.fake.word() if not id_menu else None,  # Fallback product
                "adresse_livraison": self.fake.address().replace('\n', ', '),
                "adresse_commande": self.fake.address().replace('\n', ', '),
                "coût_commande": cout_total,
                "rémunération_livreur": remuneration,
                "moyen_de_payement": random.choice(moyens_paiement),
                "status": status,
                "date_commande": date_commande,
                "temps_estimee": random.randint(20, 60)
            }
            
            commandes.append(commande)
        
        return commandes
    
    def populate_database(
        self,
        n_clients: int = 100,
        n_livreurs: int = 50,
        n_restaurants: int = 30,
        n_menus: int = 200,
        n_commandes: int = 1000,
        p_delivered: float = 0.3,
        p_null_ids: float = 0.05,
        clear_existing: bool = False
    ):
        """
        Populate database with test data
        
        Args:
            n_clients: Number of clients to generate
            n_livreurs: Number of delivery drivers
            n_restaurants: Number of restaurants
            n_menus: Number of menu items
            n_commandes: Number of orders
            p_delivered: Probability of order being delivered
            p_null_ids: Probability of missing related IDs
            clear_existing: If True, clear existing data first
        """
        if not self.client:
            self.connect()
        
        self.logger.info("🏗️  Starting database population...")
        
        # Clear existing data if requested
        if clear_existing:
            self.logger.warning("⚠️  Clearing existing data...")
            for collection in [
                self.config.collection_client,
                self.config.collection_livreur,
                self.config.collection_restaurants,
                self.config.collection_menu,
                self.config.collection_commande
            ]:
                self.db[collection].delete_many({})
            self.logger.info("✅ Existing data cleared")
        
        # Generate and insert clients
        self.logger.info(f"👥 Generating {n_clients} clients...")
        clients = self.generate_clients(n_clients)
        self.db[self.config.collection_client].insert_many(clients)
        client_ids = [c['id_client'] for c in clients]
        
        # Generate and insert delivery drivers
        self.logger.info(f"🚗 Generating {n_livreurs} delivery drivers...")
        livreurs = self.generate_livreurs(n_livreurs)
        self.db[self.config.collection_livreur].insert_many(livreurs)
        livreur_ids = [l['id_livreur'] for l in livreurs]
        
        # Generate and insert restaurants
        self.logger.info(f"🍽️  Generating {n_restaurants} restaurants...")
        restaurants = self.generate_restaurants(n_restaurants)
        self.db[self.config.collection_restaurants].insert_many(restaurants)
        restaurant_ids = [r['id_restaurant'] for r in restaurants]
        
        # Generate and insert menus
        self.logger.info(f"📋 Generating {n_menus} menu items...")
        menus = self.generate_menus(n_menus)
        self.db[self.config.collection_menu].insert_many(menus)
        menu_ids = [m['id_menu'] for m in menus]
        
        # Generate and insert orders
        self.logger.info(f"📦 Generating {n_commandes} orders...")
        commandes = self.generate_commandes(
            n_commandes,
            client_ids,
            livreur_ids,
            restaurant_ids,
            menu_ids,
            p_delivered,
            p_null_ids
        )
        self.db[self.config.collection_commande].insert_many(commandes)
        
        # Count delivered orders
        n_delivered = sum(1 for c in commandes if c['status'] == 'livrée')
        
        self.logger.info("✅ Database population complete!")
        self.logger.info(f"""
{'='*70}
📊 GENERATED DATA SUMMARY
{'='*70}
Clients:         {n_clients}
Delivery Drivers: {n_livreurs}
Restaurants:     {n_restaurants}
Menu Items:      {n_menus}
Orders:          {n_commandes}
  - Delivered:   {n_delivered} ({n_delivered/n_commandes*100:.1f}%)
  - Other:       {n_commandes - n_delivered}
{'='*70}
""")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("🔌 Connection closed")
