import json
import boto3
import uuid
import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = 'movements'
table = dynamodb.Table(table_name)
accounts_table = dynamodb.Table("accounts")
def lambda_handler(event, context):
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            account_id = message_body['accountId']
            amount = float(message_body['amount'])
            description = message_body['description']
            op_type = message_body['op']
            new_id = str(uuid.uuid4())
            item = {
                'id': new_id,
                'operationDate': datetime.datetime.utcnow().isoformat() + 'Z',
                'amount': amount,
                'type': op_type.upper(),
                'description': description,
                'accountId': account_id
            }
            item = json.loads(json.dumps(item), parse_float=Decimal)
            table.put_item(Item=item)
            
            if op_type.upper() == 'DEBIT':
                update_expression = "SET balance = balance - :val"
            elif op_type.upper() == 'CREDIT':
                update_expression = "SET balance = balance + :val"
            else:
                raise ValueError(f"Unknown operation type: {op_type}")

            response = accounts_table.update_item(
                Key={'id': account_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues={':val': Decimal(str(amount))},
                ReturnValues="UPDATED_NEW"
            )
            
            print(f"Transaction saved: {transaction_item}")
            print(f"Account updated: {response['Attributes']}")
            print(f"Item saved: {item}")
            
        except Exception as e:
            print(f"Error processing record: {record}")
            print(e)
            continue
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete.')
    }