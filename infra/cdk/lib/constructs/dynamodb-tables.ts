import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export interface DynamoDBTableProps {
    removalPolicy?: cdk.RemovalPolicy;
}

export class DynamoDBTables extends Construct {
    public readonly urlsTable: dynamodb.Table;
    public readonly analyticsTable: dynamodb.Table;
    public readonly rateLimitsTable: dynamodb.Table;

    constructor(scope: Construct, id: string, props?: DynamoDBTableProps) {
        super(scope, id);

        const removalPolicy = props?.removalPolicy ?? cdk.RemovalPolicy.DESTROY
        
        this.urlsTable = new dynamodb.Table(this, 'UrlsTable', {
            tableName: 'tinylinker-urls',
            partitionKey: {
                name: 'shortCode',
                type: dynamodb.AttributeType.STRING
            },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: removalPolicy,
            pointInTimeRecoverySpecification: {
                pointInTimeRecoveryEnabled: false,
            },
            timeToLiveAttribute: 'expiresAt',
        });

        this.urlsTable.addGlobalSecondaryIndex({
            indexName: 'userId-createdAt-index',
            partitionKey: {
                name: 'userId',
                type: dynamodb.AttributeType.STRING,
            },
            sortKey: {
                name: 'createdAt',
                type: dynamodb.AttributeType.NUMBER
            },
            projectionType: dynamodb.ProjectionType.ALL
        });

        this.analyticsTable = new dynamodb.Table(this, 'AnalyticsTable', {
            tableName: 'tinylinker-analytics',
            partitionKey: {
                name: 'shortCode',
                type: dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: 'timestamp',
                type: dynamodb.AttributeType.NUMBER
            },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: removalPolicy,
            pointInTimeRecoverySpecification: {
                pointInTimeRecoveryEnabled: false,
            },
            timeToLiveAttribute: 'expiresAt',
            stream: dynamodb.StreamViewType.NEW_IMAGE
        });

        this.analyticsTable.addGlobalSecondaryIndex({
            indexName: 'shortCode-country-index',
            partitionKey: {
                name: 'shortCode',
                type: dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: 'country',
                type: dynamodb.AttributeType.STRING
            },
            projectionType: dynamodb.ProjectionType.KEYS_ONLY,
        });

        this.rateLimitsTable = new dynamodb.Table(this, 'RateLimitsTable', {
            tableName: 'tinylinker-rate-limits',
            partitionKey: {
                name: 'identifier',
                type: dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: 'windowStart',
                type: dynamodb.AttributeType.NUMBER
            },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: removalPolicy,
            pointInTimeRecoverySpecification: {
                pointInTimeRecoveryEnabled: false,
            },
            timeToLiveAttribute: 'expiresAt',
        });
    }
}