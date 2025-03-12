import argparse
from scan_result import ScanResult,  get_scan_config

SR = ScanResult()
def arg_parse():
    parser = argparse.ArgumentParser(description="Scan all resource from scan config yaml")
    parser.add_argument(
        "--scan-config-path",
        type=str,
        default="/tmp/tmcybertron/agent.yaml",
        help="Path to the scan configuration file."
    )

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = arg_parse()
    scan_config = get_scan_config(args.scan_config_path)
    for scan_type, _ in scan_config.items():
        SR.scan(resource_type=scan_type, config_path=args.scan_config_path)

