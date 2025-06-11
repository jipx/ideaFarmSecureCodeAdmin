# Cognito WAF Toggle CDK Stack

This AWS CDK project provisions:
- Amazon Cognito User Pool for authentication
- Lambda function to toggle WAF ACL between full block and normal
- API Gateway with Cognito authorizer to expose a secure `/toggle` endpoint

## Deploy

```bash
cdk bootstrap
cdk deploy
```

## Test

POST to your deployed API Gateway endpoint:

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/toggle \
  -H "Authorization: Bearer <id_token>" \
  -H "Content-Type: application/json" \
  -d '{ "mode": "block" }'
```

- `mode: "block"` blocks all traffic via WAF.
- `mode: "normal"` restores original rules.
