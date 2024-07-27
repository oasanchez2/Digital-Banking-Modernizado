import json
import boto3
from boto3.dynamodb.conditions import Key
import decimal

# Clase para serializar decimal a JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
accounts_table = dynamodb.Table('accounts')
movements_table = dynamodb.Table('movements')

def lambda_handler(event, context):
    account_id = event['pathParameters']['accountId']
    try:
        # Consultar la tabla de cuentas
        response = accounts_table.query(KeyConditionExpression=Key('id').eq(account_id))
        account_items = response.get('Items', [])
        
        if not account_items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Account not found'})
            }
        
        acc = account_items[0]
        
        # Consultar la tabla de movimientos
        movements_response = movements_table.query(IndexName='accountId-index', KeyConditionExpression=Key('accountId').eq(account_id))
        movement_items = movements_response.get('Items', [])
        
        account_operations = [
            {
                "id": movement['id'],
                "operationDate": movement['operationDate'],
                "amount": float(movement['amount']),
                "type": movement['type'],
                "description": movement['description']
            }
            for movement in movement_items
        ]
        
        data = {
            "accountId": acc.get('id', ""),
            "balance": float(acc.get('balance', 0)),
            "currentPage": 0,
            "totalPages": 4,
            "pageSize": 5,
            "accountOperationDTOS": account_operations
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(data, cls=DecimalEncoder)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)}, cls=DecimalEncoder)
        }