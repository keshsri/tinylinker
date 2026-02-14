import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as cdk from 'aws-cdk-lib';
import * as path from 'path';
import { Construct } from 'constructs';

export interface ApiLambdaProps {
    urlsTable: dynamodb.Table;
    analyticsTable: dynamodb.Table;
    rateLimitsTable: dynamodb.Table;
    baseUrl: string;
}

export class ApiLambda extends Construct {
    public readonly handler: lambda.DockerImageFunction;

    constructor(scope: Construct, id: string, props: ApiLambdaProps) {
        super(scope, id);

        this.handler = new lambda.DockerImageFunction(this, 'ApiHandler', {
            code: lambda.DockerImageCode.fromImageAsset(
                path.join(__dirname, '../../../../services/api')
            ),
            memorySize: 512,
            timeout: cdk.Duration.seconds(30),
            environment: {
                URLS_TABLE_NAME: props.urlsTable.tableName,
                ANALYTICS_TABLE_NAME: props.analyticsTable.tableName,
                RATE_LIMITS_TABLE_NAME: props.rateLimitsTable.tableName,
                BASE_URL: props.baseUrl,
                API_GATEWAY_STAGE: 'dev',
            },
        });

        props.urlsTable.grantReadWriteData(this.handler);
        props.analyticsTable.grantReadWriteData(this.handler);
        props.rateLimitsTable.grantReadWriteData(this.handler);
    }
}