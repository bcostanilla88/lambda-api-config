import json
from typing import Optional

import boto3 # type: ignore
import os
import urllib.request
import urllib.error

s3 = boto3.client("s3")
bucket_name = os.environ['S3_BUCKET']
key = os.environ['S3_KEY']

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class ApiConfig:
    def __init__(self, endpoint: str, method: str, target_uri: str, allowed: bool):
        self.endpoint = endpoint
        self.method = method
        self.target_uri = target_uri
        self.allowed = allowed

def load_endpoint_config(target_endpoint: str, http_method: str) -> Optional[ApiConfig]:
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        json_content = json.loads(content)

        matched = next(
            (item for item in json_content 
            if item.get("endpoint") == target_endpoint and item.get("method") == http_method), 
            None
        )

        if matched:
            return ApiConfig(**matched)
        return None
    except Exception as e:
        raise RuntimeError(f"Error loading config: {e}")

def build_response(status_code: int, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json"
        }
    }

def handle_json_request(event, target_endpoint: str, http_method: str):
    try:
        endpoint_obj = load_endpoint_config(target_endpoint, http_method)
        if endpoint_obj:
            if endpoint_obj.allowed:
                req = urllib.request.Request(endpoint_obj.target_uri, headers=headers, method=endpoint_obj.method)
                try:
                    with urllib.request.urlopen(req) as response:
                        status_code = response.getcode()
                        response_data = response.read().decode("utf-8")
                        data = json.loads(response_data)
                        
                        return {
                            "statusCode": status_code,
                            "body": json.dumps(data)
                        }
                
                except urllib.error.HTTPError as e:
                    return {
                        "statusCode": e.code,
                        "body": f"HTTPError: {e.reason}"
                    }
                except urllib.error.URLError as e:
                    return {
                        "statusCode": 500,
                        "body": f"URLError: {e.reason}"
                    }
                except Exception as e:
                    return {
                        "statusCode": 500,
                        "body": f"Unexpected error: {str(e)}"
                    }
                # return build_response(200, {
                #     "endpoint": endpoint_obj.endpoint,
                #     "method": endpoint_obj.method,
                #     "target_uri": endpoint_obj.target_uri
                # })
            else:
                return build_response(403, {"error": "Access not allowed"})
        return build_response(404, {"error": "API Config not found"})
    except Exception as e:
        return build_response(500, {"error": str(e)})


def main_handler(event, context):
    stage = event["requestContext"].get("stage")
    path = event["path"]
    http_method = event.get("httpMethod")
    return handle_json_request(event, stage + path, http_method)
