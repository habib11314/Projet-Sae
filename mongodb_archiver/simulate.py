"""
CLI for test data generation
"""
import argparse
import sys
import logging

from config import Config
from logger import setup_logger, get_log_filename
from generator import DataGenerator


def main():
    """Main entry point for data generator"""
    parser = argparse.ArgumentParser(
        description='MongoDB Test Data Generator - Create realistic test orders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 1000 orders with default settings
  python simulate.py --count 1000
  
  # Generate with specific seed for reproducibility
  python simulate.py --count 500 --seed 42
  
  # Generate with 50% delivered orders
  python simulate.py --count 1000 --p-delivered 0.5
  
  # Clear existing data and generate fresh dataset
  python simulate.py --count 2000 --clear
  
  # Custom numbers of entities
  python simulate.py --count 1000 --clients 200 --restaurants 50
  
  # Use local MongoDB for testing
  python simulate.py --simulation --count 100

Environment Variables:
  MONGODB_URI       MongoDB connection string (required in production)
  MONGODB_DATABASE  Database name (default: Ubereats)
        """
    )
    
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of orders to generate (default: 1000)')
    parser.add_argument('--clients', type=int, default=100,
                       help='Number of clients (default: 100)')
    parser.add_argument('--livreurs', type=int, default=50,
                       help='Number of delivery drivers (default: 50)')
    parser.add_argument('--restaurants', type=int, default=30,
                       help='Number of restaurants (default: 30)')
    parser.add_argument('--menus', type=int, default=200,
                       help='Number of menu items (default: 200)')
    parser.add_argument('--p-delivered', type=float, default=0.3,
                       help='Probability of order being delivered (0-1, default: 0.3)')
    parser.add_argument('--p-null', type=float, default=0.05,
                       help='Probability of missing related IDs (0-1, default: 0.05)')
    parser.add_argument('--seed', type=int,
                       help='Random seed for reproducibility')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing data before generating')
    parser.add_argument('--simulation', action='store_true',
                       help='Use local MongoDB for testing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Validate probabilities
    if not 0 <= args.p_delivered <= 1:
        print("❌ Error: --p-delivered must be between 0 and 1")
        sys.exit(1)
    
    if not 0 <= args.p_null <= 1:
        print("❌ Error: --p-null must be between 0 and 1")
        sys.exit(1)
    
    try:
        # Setup config and logger
        if args.simulation:
            config = Config.for_simulation()
            print("🧪 Running in SIMULATION mode (local database)")
        else:
            config = Config.from_env()
        
        log_level = logging.DEBUG if args.verbose else logging.INFO
        log_file = get_log_filename('generator') if not args.simulation else None
        logger = setup_logger('generator', log_file, log_level)
        
        # Create generator
        generator = DataGenerator(config, seed=args.seed, logger=logger)
        
        # Warn if clearing data
        if args.clear:
            response = input("⚠️  This will DELETE all existing data. Continue? [y/N]: ")
            if response.lower() != 'y':
                print("❌ Cancelled by user")
                sys.exit(0)
        
        # Populate database
        generator.populate_database(
            n_clients=args.clients,
            n_livreurs=args.livreurs,
            n_restaurants=args.restaurants,
            n_menus=args.menus,
            n_commandes=args.count,
            p_delivered=args.p_delivered,
            p_null_ids=args.p_null,
            clear_existing=args.clear
        )
        
        generator.close()
        print("✅ Data generation complete!")
    
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
