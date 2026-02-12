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
            },
            defaultCorsPreflightOptions: {
                allowOrigins: apigateway.Cors.ALL_ORIGINS,
                allowMethods: apigateway.Cors.ALL_METHODS,
            }, 
        });

        const integration = new apigateway.LambdaIntegration(props.handler);

        const shorten = this.api.root.addResource('shorten');
        shorten.addMethod('POST', integration);

        const shortCode = this.api.root.addResource('{shortCode}');
        shortCode.addMethod('GET', integration);

        const analytics = this.api.root.addResource('analytics');
        const analyticsShortCode = analytics.addResource('{shortCode}');
        analyticsShortCode.addMethod('GET', integration);
    }
}