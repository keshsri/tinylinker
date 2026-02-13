import os
import boto3
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from .logger import logger

dynamodb = boto3.resource('dynamodb')

URLS_TABLE = dynamodb.Table(os.environ.get('URLS_TABLE_NAME', 'tinylinker-urls'))
ANALYTICS_TABLE = dynamodb.Table(os.environ.get('ANALYTICS_TABLE_NAME', 'tinylinker-analytics'))
RATE_LIMITS_TABLE = dynamodb.Table(os.environ.get('RATE_LIMITS_TABLE_NAME', 'tinylinker-rate-limits'))

def put_item(table, item: Dict[str, Any]) -> bool:
    try:
        table.put_item(Item=item)
        logger.info(f"Item added successfully")
        return True
    except ClientError as e:
        logger.error(f"Error putting item: {e}")
        return False
    
def get_item(table, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        response = table.get_item(Key=key)
        logger.info(f"Item retrieved successfully")
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting item: {e}")
        return None

def update_item(
    table, key: Dict[str, Any], update_expression: str,
    expression_values: Dict[str, Any]
) -> bool:
    try:
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        logger.info(f"Item updated successfully")
        return True
    except ClientError as e:
        logger.error(f"Error updating item: {e}")
        return False

def increment_counter(
    table, key: Dict[str, Any], attribute: str,
    increment_by: int = 1
) -> Optional[int]:
    try:
        response = table.update_item(
            Key=key,
            UpdateExpression=f"ADD {attribute} :inc",
            ExpressionAttributeValues={':inc': increment_by},
            ReturnValues='UPDATED_NEW'
        )
        logger.info(f"Successfully incremented counter")
        return response['Attributes'].get(attribute)
    except ClientError as e:
        logger.error(f"Error incrementing counter: {e}")
        return None

def query_items(
    table, key_condition_expression: str,
    expression_values: Dict[str, Any],
    index_name: Optional[str] = None
) -> List[Dict[str,Any]]:
    try:
        kwargs = {
            'KeyConditionExpression': key_condition_expression,
            'ExpressionAttributeValues': expression_values
        }
        if index_name:
            kwargs['IndexName'] = index_name

        response = table.query(**kwargs)
        logger.info(f"Successfully queried items")
        return response.get('Items', [])
    except ClientError as e:
        logger.error(f"Error querying items: {e}")
        return []
