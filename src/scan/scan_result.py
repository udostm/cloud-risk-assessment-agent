import os
import json
from typing import Optional
from src.scan.kubernetes import scan_kubernetes, k8s_resource_misconfigure
from src.scan.filesystem import scan_filesystem
from src.scan.image import scan_image
from src.scan.aws import scan_aws
import yaml
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.db.config import DEFAULT_DB_PATH

# Create an async engine; using the "aiosqlite" dialect for SQLite.
DATABASE_URL = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}"
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session maker for async sessions.
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class ReportFormatException(Exception):
    """Exception raised when format not standard JSON."""
    def __init__(self, message="The output report is not a valid JSON"):
        self.message = message
        super().__init__(self.message)

def get_scan_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"The scan config '{config_path}' does not exist.")
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class ScanResult:
    def __init__(self, base_dir: str = "/tmp/tmcybertron/results"):
        """
        Initialize the base directory to store scan results categorized by resource type.

        :param base_dir: The base directory where results will be stored.
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_file_path(self, resource_type: str, resource_name: str) -> str:
        """
        Construct the file path for storing a specific resource's scan result.

        :param resource_type: The type of resource (e.g., 'code', 'container', 'kubernetes', 'aws').
        :param resource_name: The name of the resource.
        :return: The file path as a string.
        """
        resource_dir = os.path.join(self.base_dir, resource_type)
        os.makedirs(resource_dir, exist_ok=True)
        return os.path.join(resource_dir, f"{resource_name}.json")

    def set_scan_result(self, resource_type: str, resource_name: str, result: str, component_name: Optional[str] = None) -> None:
        """
        Set the scan result for a given resource type and name.

        :param resource_type: The type of resource (e.g., 'code', 'container', 'kubernetes', 'aws').
        :param resource_name: The name of the resource.
        :param result: The scan result to store.
        :param component_name: Optional name of a component within the resource.
        """
        file_path = self._get_file_path(resource_type, resource_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        if component_name:
            data[component_name] = result
        else:
            data["_default"] = result

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def get_scan_result(self, resource_type: str, resource_name: str = "default", component_name: Optional[str] = None) -> Optional[str]:
        """
        Get the scan result for a given resource type and name.

        :param resource_type: The type of resource (e.g., 'code', 'container', 'kubernetes', 'aws').
        :param resource_name: The name of the resource.
        :param component_name: Optional name of a component within the resource.
        :return: The scan result or None if not found.
        """
        file_path = self._get_file_path(resource_type, resource_name)
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                raise ReportFormatException()
            if component_name and resource_type == "kubernetes":
                return k8s_resource_misconfigure(data, component_name)
            return data
        return None

    def scan(self, resource_type: str, config_path: Optional[str] = "/tmp/tmcybertron/agent.yaml", bg: bool = False):
        scan_config = get_scan_config(config_path)
        if resource_type == "code" and scan_config["code"]:
            print (f'========================== Start Scan Code Path ({scan_config["code"]["folder"]})  ==========================')
            scan_filesystem(
                path=scan_config["code"]["folder"],
                report=self._get_file_path(resource_type, "default"),
                bg=bg
            )
        elif resource_type == "container" and scan_config["container"]:
            print (f'========================== Start Scan Image({scan_config["container"]["image_path"]}) ==========================')
            scan_image(
                image_path=scan_config["container"]["image_path"],
                report=self._get_file_path(resource_type, "default"),
                bg=bg
            )
        elif resource_type == "kubernetes" and scan_config["kubernetes"]:
            print (f'========================== Start Scan Kubernetes ({scan_config["kubernetes"]["config_path"]}) ==========================')
            scan_kubernetes(
                report=self._get_file_path(resource_type, "default"),
                config_path=scan_config["kubernetes"]["config_path"],
                bg=bg
            )
        elif resource_type == "aws" and scan_config["aws"]:
            print (f'========================== Start Scan AWS ({scan_config["aws"]["region"]}) ==========================')
            scan_aws(
                report=self._get_file_path(resource_type, "default"),
                region=scan_config["aws"]["region"],
                bg=bg
            )
