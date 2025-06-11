# Lambda + API Gateway Testing Guide (Secured by Cognito)

## ✅ Prerequisites

Ensure you have these from your CDK deployment:
- ✅ **API Gateway URL**: `https://82tmqa6o96.execute-api.ap-northeast-1.amazonaws.com/prod/toggle`
- ✅ **Cognito User Pool ID**: `ap-northeast-1_LHLfCym7i`
- ✅ **Cognito App Client ID**: `r54r5gl922l46r2s2ea6nh84b`
- ✅ **Deployed Lambda function**
- ✅ AWS Console access or AWS CLI (PowerShell or Bash)

---

## 🧪 Step 1: Create a Test Cognito User

### Option A: AWS Console
1. Go to **Amazon Cognito > User Pools > YourUserPool**
2. Select **Users and groups**
3. Click **Create user**
4. Enter:
   - Username: `test@example.com`
   - Temporary password: `TestPassword123!`
   - Email: `test@example.com`
   - ✅ Mark email as verified
5. Save the user

### Option B: AWS CLI (Bash or PowerShell)

```bash
aws cognito-idp sign-up \
  --client-id r54r5gl922l46r2s2ea6nh84b \
  --username test@example.com \
  --password 'TestPassword123!' \
  --user-attributes Name=email,Value=test@example.com

aws cognito-idp admin-confirm-sign-up \
  --user-pool-id ap-northeast-1_LHLfCym7i \
  --username test@example.com
```

---

## 🔐 Step 2: Login and Get JWT Token

### Bash:
```bash
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id r54r5gl922l46r2s2ea6nh84b \
  --auth-parameters USERNAME=test@example.com,PASSWORD=TestPassword123!
```

### PowerShell:
```powershell
aws cognito-idp initiate-auth `
  --auth-flow USER_PASSWORD_AUTH `
  --client-id r54r5gl922l46r2s2ea6nh84b `
  --auth-parameters USERNAME=test@example.com,PASSWORD=TestPassword123!
```

> If you get `NEW_PASSWORD_REQUIRED`, complete the challenge:

```powershell
aws cognito-idp respond-to-auth-challenge `
  --client-id r54r5gl922l46r2s2ea6nh84b `
  --challenge-name NEW_PASSWORD_REQUIRED `
  --session "<Session string from previous output>" `
  --challenge-responses USERNAME=test@example.com,NEW_PASSWORD=NewSecurePassword123!
```

---

## 🌐 Step 3: Call API Gateway

### Bash:
```bash
curl -X POST https://82tmqa6o96.execute-api.ap-northeast-1.amazonaws.com/prod/toggle \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 🧪 Step 4: Use Postman

1. Import the collection: `toggle_waf_postman_with_login_auto_token.json`
2. Run the **Login** request
3. The `IdToken` is auto-stored in `{IdToken}`
4. Run the **POST /toggle** request (uses `{IdToken}`)

---

## 🧪 Step 5: Test via AWS Console (API Gateway)

1. Go to **Amazon API Gateway > APIs > YourAPI**
2. Click on **/toggle → POST**
3. Click **Test**
4. Add Header:
   ```
   Authorization: Bearer <JWT_TOKEN>
   ```
5. Body: `{}` (raw JSON)
6. Click **Test**

---

## ✅ Expected Results

| HTTP Code | Meaning |
|-----------|---------|
| `200 OK` | Lambda executed successfully |
| `403 Forbidden` | Missing/invalid/expired JWT |
| `500 Internal Server Error` | Lambda execution or logic failure |