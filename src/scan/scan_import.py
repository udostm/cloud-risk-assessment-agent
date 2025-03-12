from src.db.db_util import init_db, batch_upsert_records, query_all_records, export_to_csv
import asyncio
from src.scan.scan_result import ScanResult
from src.db.config import DEFAULT_DB_PATH
from src.scan.kubernetes import gen_kubernetes_db_content
from src.scan.filesystem import process_code_scan
from src.scan.aws import gen_aws_db_content

async def process_and_upsert_scan_results(scan_type: str, scan_result: ScanResult, db_cols: list, process_func=None, **kwargs):
    """
    Process scan results, generate database content, and upsert records.

    Args:
        scan_type (str): The type of scan (e.g., "kubernetes", "aws").
        scan_result (ScanResult): The ScanResult object to retrieve results.
        db_cols (list): List of database columns.
        process_func (callable, optional): Custom processing function for the scan results.
        **kwargs: Additional arguments for the processing function.

    Returns:
        list: Upserted records.
    """
    report = scan_result.get_scan_result(scan_type)
    if report == None:
        return None
    try:
        if process_func:
            df = await process_func(report, **kwargs)
        else:
            print("generate db content===================")
            df = await globals()[f"gen_{scan_type}_db_content"](report, db_cols)
        rows = df.to_dict(orient="records")
        return await batch_upsert_records(rows)
    except Exception as e:
        print(e)
        return None

async def initialize_database_and_scans():
    """Initialize the database, process scan results, and export records to CSV."""
    # Use the consistent absolute path
    await init_db(DEFAULT_DB_PATH)
    
    db_cols = ['type', 'id', 'resource_name', 'service_name', 'avdid', 'title', 'description', 'resolution', 'severity', 'message', 'cvss_strings', 'risk_score', 'cause_metadata']
    scan_result = ScanResult()

    # Process different scan types
    await process_and_upsert_scan_results("kubernetes", scan_result, db_cols)
    await process_and_upsert_scan_results("aws", scan_result, db_cols)
    await process_and_upsert_scan_results("code", scan_result, db_cols, process_func=process_code_scan, type="CODE")
    await process_and_upsert_scan_results("container", scan_result, db_cols, process_func=process_code_scan, type="CONTAINER")

if __name__ == '__main__':
    asyncio.run(initialize_database_and_scans())
