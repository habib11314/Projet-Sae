"""
Main CLI interface for MongoDB Order Archiver
"""
import argparse
import sys
from datetime import datetime, timedelta
import logging

from config import Config
from logger import setup_logger, get_log_filename
from archiver import OrderArchiver
from watcher import OrderWatcher


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats"""
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y',
        '%d/%m/%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or DD/MM/YYYY")


def run_batch_archive(args):
    """Run batch archiving"""
    # Setup config and logger
    if args.simulation:
        config = Config.for_simulation()
        print("🧪 Running in SIMULATION mode (local database)")
    else:
        config = Config.from_env()
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_file = get_log_filename('batch') if not args.no_log else None
    logger = setup_logger('batch_archiver', log_file, log_level)
    
    # Parse date filters
    date_from = parse_date(args.date_from) if args.date_from else None
    date_to = parse_date(args.date_to) if args.date_to else None
    
    if date_from:
        logger.info(f"📅 Date filter FROM: {date_from}")
    if date_to:
        logger.info(f"📅 Date filter TO: {date_to}")
    
    # Override batch size if provided
    if args.batch_size:
        config.batch_size = args.batch_size
        logger.info(f"📦 Batch size: {args.batch_size}")
    
    # Create archiver
    archiver = OrderArchiver(config, logger)
    
    # Connect to database
    if not archiver.connect():
        logger.error("❌ Failed to connect to database")
        sys.exit(1)
    
    # Ensure indexes
    archiver.ensure_indexes()
    
    # Run archiving
    stats = archiver.archive_all(
        dry_run=args.dry_run,
        date_from=date_from,
        date_to=date_to
    )
    
    # Print summary
    print(archiver.get_stats_summary())
    
    # Export samples if requested
    if args.export_sample:
        archiver.export_sample(args.export_sample, args.sample_count)
    
    # Close connection
    archiver.close()
    
    # Exit with error code if there were errors
    if stats['errors'] > 0:
        sys.exit(1)


def run_watch_mode(args):
    """Run watch mode with Change Streams"""
    # Setup config and logger
    if args.simulation:
        config = Config.for_simulation()
        print("🧪 Running in SIMULATION mode (local database)")
    else:
        config = Config.from_env()
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_file = get_log_filename('watcher') if not args.no_log else None
    logger = setup_logger('watcher', log_file, log_level)
    
    # Create watcher
    watcher = OrderWatcher(config, logger)
    
    # Start watching
    if args.simple:
        watcher.watch_simple()
    else:
        watcher.watch(resume=not args.no_resume)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MongoDB Order Archiver - Archive delivered orders automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Batch archive all delivered orders
  python main.py batch --run
  
  # Dry run to see what would be archived
  python main.py batch --dry-run
  
  # Archive orders from specific date range
  python main.py batch --run --date-from 2025-01-01 --date-to 2025-01-31
  
  # Export sample of archived orders
  python main.py batch --run --export-sample samples.json
  
  # Watch for changes in real-time
  python main.py watch
  
  # Watch in simple mode (no resume token)
  python main.py watch --simple
  
  # Simulation mode (uses local MongoDB)
  python main.py batch --simulation --run

Environment Variables:
  MONGODB_URI       MongoDB connection string (required in production)
  MONGODB_DATABASE  Database name (default: Ubereats)
  BATCH_SIZE        Batch size for archiving (default: 100)
  MAX_RETRIES       Max retries on error (default: 3)
        """
    )
    
    # Common arguments
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging (DEBUG level)')
    parser.add_argument('--no-log', action='store_true',
                       help='Disable file logging (stdout only)')
    parser.add_argument('--simulation', action='store_true',
                       help='Use local MongoDB for testing')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Batch archiving command
    batch_parser = subparsers.add_parser('batch', help='Batch archive delivered orders')
    batch_parser.add_argument('--run', action='store_true',
                             help='Actually perform archiving (required if not --dry-run)')
    batch_parser.add_argument('--dry-run', action='store_true',
                             help='Simulate archiving without making changes')
    batch_parser.add_argument('--date-from', type=str,
                             help='Start date filter (YYYY-MM-DD or DD/MM/YYYY)')
    batch_parser.add_argument('--date-to', type=str,
                             help='End date filter (YYYY-MM-DD or DD/MM/YYYY)')
    batch_parser.add_argument('--batch-size', type=int,
                             help='Number of orders to process in each batch')
    batch_parser.add_argument('--export-sample', type=str,
                             help='Export sample archived orders to JSON file')
    batch_parser.add_argument('--sample-count', type=int, default=5,
                             help='Number of samples to export (default: 5)')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', 
                                         help='Watch for changes in real-time')
    watch_parser.add_argument('--simple', action='store_true',
                             help='Simple watch mode without resume token')
    watch_parser.add_argument('--no-resume', action='store_true',
                             help='Do not resume from saved position')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Validate batch command
    if args.command == 'batch':
        if not args.run and not args.dry_run:
            print("❌ Error: Must specify either --run or --dry-run")
            sys.exit(1)
    
    try:
        if args.command == 'batch':
            run_batch_archive(args)
        elif args.command == 'watch':
            run_watch_mode(args)
    
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
