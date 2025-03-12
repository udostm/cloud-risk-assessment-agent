#!/usr/bin/env python
import argparse
import sys
import os
import asyncio
import logging
import datetime
from src.db.config import DEFAULT_DB_PATH

# Add the parent directory to sys.path to be able to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from src.db.db_util import AsyncSessionLocal, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("db_refresh")

async def refresh_database(db_path, force=False):
    """
    Refresh the database by deleting all records from the 'results' table.
    
    Args:
        db_path (str): Path to the database file
        force (bool): If True, skip confirmation prompt
        
    Returns:
        bool: True if refresh was successful, False otherwise
    """
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return False

    start_time_str = datetime.datetime.now().isoformat()
    logger.info(f"Starting database refresh at {start_time_str}")

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                delete_stmt = text("DELETE FROM results")
                await session.execute(delete_stmt)
                logger.info("Deleted all records from 'results' table.")
            await session.commit()

        end_time_str = datetime.datetime.now().isoformat()
        logger.info(f"Database refresh completed successfully at {end_time_str}")
        elapsed = datetime.datetime.fromisoformat(end_time_str) - datetime.datetime.fromisoformat(start_time_str)
        logger.info(f"Refresh operation took {elapsed.total_seconds():.2f} seconds")
        return True

    except Exception as e:
        logger.error(f"Error refreshing database: {e}")
        return False

async def async_main():
    parser = argparse.ArgumentParser(
        description="Refresh database by deleting all records in the 'results' table."
    )
    parser.add_argument(
        "db_path",
        type=str,
        nargs="?",
        default=DEFAULT_DB_PATH,
        help="Path to the database"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    if not args.force:
        ans = input(
            "WARNING: This will delete all data from the 'results' table.\n"
            "Are you sure you want to proceed? [y/N] "
        )
        if ans.lower().strip() != "y":
            logger.info("Refresh aborted by user.")
            return 0

    success = await refresh_database(args.db_path, args.force)
    if success:
        logger.info(f"Successfully cleared 'results' table at {args.db_path}")
        return 0
    else:
        logger.error(f"Failed to clear 'results' table at {args.db_path}")
        return 1

def main():
    return asyncio.run(async_main())

if __name__ == "__main__":
    sys.exit(main())
