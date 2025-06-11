from aws_cdk import (
    App, Stack, Duration, CfnOutput,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_apigateway as apigw
)
from constructs import Construct
from pathlib import Path

class CognitoWafToggleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Get values from cdk.json context
        callback_url = self.node.try_get_context("cognitoCallbackUrl") or "http://localhost:8501"
        logout_url = self.node.try_get_context("cognitoLogoutUrl") or "http://localhost:8501"

        # Cognito User Pool
        user_pool = cognito.UserPool(self, "ToggleUserPool",
            sign_in_aliases=cognito.SignInAliases(email=True),
            self_sign_up_enabled=False
        )

        # Cognito User Pool Client with OAuth for Hosted UI
        user_pool_client = cognito.UserPoolClient(self, "ToggleUserClient",
            user_pool=user_pool,
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                callback_urls=[callback_url],
                logout_urls=[logout_url]
            )
        )

        # Cognito Domain for Hosted UI (must be globally unique)
        user_pool_domain = user_pool.add_domain("ToggleUserDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="waf-toggle-ui-demo"
            )
        )

        # Lambda Function to Toggle WAF WebACL
        waf_lambda = _lambda.Function(self, "DirectWafToggleLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset(path=str(Path(__file__).parent / "lambda")),
            timeout=Duration.seconds(30)
        )

        # Permissions for Lambda to update WAF ACL
        waf_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "wafv2:ListWebACLs",
                "wafv2:GetWebACL",
                "wafv2:UpdateWebACL"
            ],
            resources=["*"]
        ))

        # API Gateway with Cognito Authorizer
        api = apigw.RestApi(self, "ToggleWafAPI")

        authorizer = apigw.CognitoUserPoolsAuthorizer(self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        toggle_endpoint = api.root.add_resource("toggle")
        toggle_endpoint.add_method("POST",
            integration=apigw.LambdaIntegration(waf_lambda),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO
        )

        # Outputs
        CfnOutput(self, "CognitoDomainURL", value=f"https://{user_pool_domain.domain_name}.auth.{self.region}.amazoncognito.com")
        CfnOutput(self, "CognitoClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "WafToggleAPIURL", value=api.url)

        self.user_pool = user_pool
        self.user_pool_client = user_pool_client


app = App()
CognitoWafToggleStack(app, "CognitoWafToggleStack")
app.synth()
