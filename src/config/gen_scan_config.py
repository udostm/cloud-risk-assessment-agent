#!/usr/bin/env python3
import yaml
import os
from prompt_toolkit import prompt

CONFIG_FILE_PATH = "/tmp/tmcybertron/agent.yaml"

def get_input(prompt_text, default_value=None):
    """
    Prompt the user for input.
    
    If a default value is provided, use prompt_toolkit's prompt to show the default.
    Otherwise, fall back to the standard input() function.
    """
    if default_value:
        return prompt(f"{prompt_text} [{default_value}]: ", default=default_value).strip()
    return input(prompt_text).strip()

def find_default_folder(parent_dir):
    try:
        # find the first directory in the parent_dir
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isdir(item_path):
                return item_path
    except FileNotFoundError:
        pass
    return ""

def find_default_file(parent_dir, file_ext):
    try:
        # find the first file with the specified extension in the parent_dir
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isfile(item_path) and item.endswith(file_ext):
                return item_path
    except FileNotFoundError:
        pass
    return ""

def main():
    print("""
=============================================
         Scan Configuration Setup
=============================================

This script will guide you through setting up your scan configuration.
Before proceeding, please ensure you have completed the following:

1. Code Repository:
   - Clone or copy your code folder to: /tmp/tmcybertron/repo/
   - Example: /tmp/tmcybertron/repo/your_project_folder

2. Docker Image:
   - Use the 'docker save' command to export your image as a tar file.
   - Place the tar file in: /tmp/tmcybertron/image_file/
   - Example command: docker save -o /tmp/tmcybertron/image_file/your_image.tar <image_name>

3. Kubernetes:
   - Copy your Kubernetes configuration file to: /tmp/tmcybertron/.kube/config

4. AWS:
   - Place your AWS credentials in a .env file

Please provide the required information as prompted below.
""")

    config_data = {}

    # 1. Code folder scanning
    if input("1) Do you need to scan a code folder? (y/n): ").strip().lower() == "y":
        default_code_folder = find_default_folder("/tmp/tmcybertron/repo/")
        if default_code_folder == "":
            default_code_folder = "/tmp/tmcybertron/repo/your_project_folder"
        code_folder = get_input("   Enter the full path of the code folder to scan", default_code_folder)
        config_data["code"] = {"folder": code_folder}

    # 2. Kubernetes configuration scanning
    if input("2) Do you need to scan a Kubernetes cluster? (y/n): ").strip().lower() == "y":
        default_config_path = "/tmp/tmcybertron/.kube/config"
        k8s_config_path = get_input("   Enter the full path to your Kubernetes config file", default_config_path)
        config_data["kubernetes"] = {"config_path": k8s_config_path}

    # 3. Docker image scanning
    if input("3) Do you need to scan a Docker image? (y/n): ").strip().lower() == "y":
        default_image_tar_path = find_default_file("/tmp/tmcybertron/image_file/", ".tar")
        if default_image_tar_path == "":
            default_image_tar_path = "/tmp/tmcybertron/image_file/your_image.tar"
        image_tar_path = get_input("   Enter the full path of the Docker image tar file", default_image_tar_path)
        config_data["container"] = {"image_path": image_tar_path}

    # 4. AWS resources scanning
    if input("4) Do you need to scan AWS resources? (y/n): ").strip().lower() == "y":
        default_aws_region = "us-west-2"
        aws_region = get_input("   Enter the AWS region to scan", default_aws_region)
        config_data["aws"] = {"region": aws_region}

    # Write the configuration to a YAML file
    with open(CONFIG_FILE_PATH, "w") as file:
        yaml.safe_dump(config_data, file, sort_keys=False)

    print(f"\nConfiguration file has been written to: {CONFIG_FILE_PATH}\n")
    print("Generated YAML configuration:")
    print("-" * 40)
    print(yaml.safe_dump(config_data, sort_keys=False))
    print("-" * 40)

if __name__ == "__main__":
    main()
