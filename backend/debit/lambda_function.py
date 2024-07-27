import json
import boto3

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/905418059026/test'

def lambda_handler(event, context):
    print(event)
    try:
        body = json.loads(event['body'])
        account_id = body['accountId']
        amount = body['amount']
        description = body['description']
        message = {
            'accountId': account_id,
            'amount': amount,
            'description': description,
            'op': 'debit'
        }
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'messageId': response['MessageId']})
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
            'body': json.dumps({'error': str(e)})
        }