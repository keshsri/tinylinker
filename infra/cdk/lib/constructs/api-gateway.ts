import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export interface ApiGatewayProps {
    handler: lambda.DockerImageFunction;
}

export class ApiGateway extends Construct {
    public readonly api: apigateway.RestApi;

    constructor(scope: Construct, id: string, props: ApiGatewayProps) {
        super(scope, id);

        this.api = new apigateway.RestApi(this, 'TinyLinkerApi', {
            restApiName: 'TinyLinker API',
            description: 'URL shortener with analytics',
            deployOptions: {
                stageName: 'dev',
                throttlingRateLimit: 50,      // Requests per second
                throttlingBurstLimit: 100,     // Burst capacity
            },
            defaultCorsPreflightOptions: {
                allowOrigins: apigateway.Cors.ALL_ORIGINS,
                allowMethods: apigateway.Cors.ALL_METHODS,
                allowHeaders: [
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                    'X-Amz-Security-Token',
                    'X-Amz-User-Agent',
                ],
                allowCredentials: true,
            },
        });

        const integration = new apigateway.LambdaIntegration(props.handler, {
            proxy: true,
        });

        this.api.root.addProxy({
            defaultIntegration: integration,
            anyMethod: true,
        });
    }
}