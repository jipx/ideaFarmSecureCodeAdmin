<!---
tags: [aws-cdk, cognito, waf, lambda, api-gateway, streamlit, authentication, deployment, best-practices, checklist, common-mistakes]
-->


# ✅ CDK Checklist for Cognito + WAF Toggle Project

## 🔧 Infrastructure Configuration
- [ ] Cognito **User Pool** and **Domain** are defined in CDK (not manually created).
- [ ] Cognito **User Pool Client** uses `authorization_code_grant=True` with:
  - [ ] Correct `callback_urls` from `cdk.json` context.
  - [ ] Correct `logout_urls` from `cdk.json` context.
- [ ] The **OAuth flow** includes `email`, `openid`, and `profile` scopes.

## 🛡️ WAF & Lambda
- [ ] Lambda has `wafv2:GetWebACL`, `ListWebACLs`, `UpdateWebACL` permissions.
- [ ] Lambda handler file is correctly referenced (e.g., `index.handler`).
- [ ] WAF is configured via CDK or is integrated with existing WebACLs.
- [ ] Timeout for Lambda is explicitly set (e.g., `Duration.seconds(30)`).

## 🌐 API Gateway
- [ ] API Gateway is protected by **Cognito Authorizer** (AuthorizationType.COGNITO).
- [ ] The `/toggle` route only accepts **POST** requests.
- [ ] Resource permissions and integrations are tested via `curl` or Postman.

## ⚙️ CDK Deployment Best Practices
- [ ] `cdk.json` includes proper `context` keys:
  ```json
  {
    "context": {
      "cognitoCallbackUrl": "http://localhost:8501",
      "cognitoLogoutUrl": "http://localhost:8501"
    }
  }
  ```
- [ ] Values like callback/logout URLs are injected using:
  ```python
  callback_urls=[self.node.try_get_context("cognitoCallbackUrl")]
  ```
- [ ] You run `cdk diff` before `cdk deploy`.
- [ ] Avoid making changes in AWS Console after deployment to prevent **configuration drift**.

## 🧪 Post-Deployment Checks
- [ ] Hosted UI login works and redirects to `main.py`.
- [ ] `toggle.py` is protected and only accessible to users in `admin` group.
- [ ] Cognito JWT token is parsed and validated (with expiry check).
- [ ] Toggle action correctly switches WAF mode (visible in `GET` status).


---

## ⚠️ Common Mistakes to Avoid

- [ ] ❌ **Hardcoding URLs** instead of using context (`cdk.json`).
- [ ] ❌ **Manual Cognito configuration** in AWS Console after CDK deploy.
- [ ] ❌ Skipping `cdk bootstrap` before first deployment.
- [ ] ❌ Forgetting `cdk diff` — leads to unintended changes.
- [ ] ❌ Not setting `removal_policy=RETAIN` for persistent data (optional here).
- [ ] ❌ Incorrect or missing IAM permissions for Lambda to access WAF.
- [ ] ❌ Not defining **unique Cognito domain prefix** (must be globally unique).
- [ ] ❌ Using outdated APIs (e.g., `st.experimental_get_query_params`).
- [ ] ❌ Not checking **token expiration** in Streamlit.
- [ ] ❌ Forgetting to protect admin-only routes like `/toggle` with group check.


---

## 🏷️ Tagging Best Practices (AWS CDK)

### 🔹 Why Tag?

| Purpose                  | Benefit                                       |
|--------------------------|-----------------------------------------------|
| **Cost allocation**      | Track usage per team, environment, or project |
| **Security auditing**    | Identify ownership, access level, or risk     |
| **Automation**           | Enable lifecycle rules, backups, alerts       |
| **Operational clarity**  | Simplifies troubleshooting and reviews        |

### 🔸 Common Tag Categories

| Key             | Example Value               | Purpose                       |
|------------------|-----------------------------|--------------------------------|
| `Project`        | `WafToggleApp`              | Associates resources to a project |
| `Owner`          | `pengxiang.ji`              | Identifies who created/owns the stack |
| `Environment`    | `dev` / `prod`              | Environment separation          |
| `Stack`          | `CognitoWafToggleStack`     | Useful for multi-stack apps     |
| `Application`    | `StreamlitToggleConsole`    | Helps link to frontend          |
| `CostCenter`     | `SP1234`                    | Enables budget tracking         |

### 🔧 How to Add Tags in CDK

**Global Tags (Applied to all resources):**

```python
from aws_cdk import Tags

app = App()
stack = CognitoWafToggleStack(app, "CognitoWafToggleStack")

Tags.of(stack).add("Project", "WafToggleApp")
Tags.of(stack).add("Owner", "pengxiang.ji")
Tags.of(stack).add("Environment", "dev")

app.synth()
```

**Per Resource:**

```python
Tags.of(user_pool).add("Component", "CognitoUserPool")
Tags.of(waf_lambda).add("Component", "WafToggleLambda")
```

### 🛑 Avoid

- ❌ Using vague tags like `"Test": "Yes"`
- ❌ Skipping tags in dev environments
- ❌ Duplicating tags with similar meanings (e.g., `Env`, `environment`)

---

## 📚 Additional Resources

- 🔗 [AWS CDK Best Practices Guide (Official)](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)  
  Covers lifecycle management, constructs, security, CI/CD integration, and more.

---

## 🛠️ Enhancements from AWS CDK Best Practices

1. **Use Modular Constructs**  
   Break your infrastructure into smaller, reusable constructs. Encapsulate related resources such as WAF, Cognito, and API Gateway into their own constructs or stacks.

2. **Manage Context Properly**  
   Use `cdk.json` or CLI `--context` to pass environment-specific configurations. Clear stale context using `cdk context --clear`.

3. **Support Multiple Environments**  
   Use CDK Pipelines or separate stacks with context-driven settings to deploy to dev, staging, and production environments consistently.

4. **Write Infrastructure Unit Tests**  
   Leverage assertions in your test framework to verify constructs, properties, and permissions during `cdk synth`.

5. **Avoid Over-Abstraction**  
   Prefer readability and maintainability over overly generic abstractions. Write explicit code for critical infrastructure.

6. **Apply Security Best Practices**  
   Use `grant*()` methods on resources instead of hardcoded policies. Consider permission boundaries or service control policies (SCPs) for CI/CD roles.

---

---

## 🛠️ Enhancements for Current Project Context

1. **Use Modular Constructs**  
   - Consider extracting the Cognito setup, WAF Lambda, and API Gateway components into separate construct classes (e.g., `CognitoStack`, `WafStack`) to improve maintainability.

2. **Manage Context Properly**  
   - Add `callback_urls` and `logout_urls` as keys in `cdk.json` under `"context"`. Access them in the CDK code using `self.node.try_get_context("callback_urls")`.

3. **Support Multiple Environments**  
   - Allow dynamic domain prefixing and URI callbacks by setting them from context values, making it easy to deploy to dev, staging, and prod.

4. **Write Infrastructure Unit Tests**  
   - Add unit tests using `assertions.Template` from `aws_cdk.assertions` to ensure the Lambda has correct WAF permissions, and that the UserPoolClient uses OAuth settings properly.

5. **Avoid Over-Abstraction**  
   - The project currently has clear CDK logic. If more features are added (e.g., user groups, CloudWatch metrics), keep abstractions understandable and aligned to domain features.

6. **Apply Security Best Practices**  
   - Use `grant_invoke()` to explicitly allow API Gateway to call Lambda if needed.
   - Avoid wildcards in WAF permissions long-term — scope to specific WebACL ARNs.
   - Apply tag-based identity controls or roles with boundaries if using CI/CD for deployment.

---
