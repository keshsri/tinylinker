import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import { DynamoDBTables } from './constructs/dynamodb-tables';
import { ApiLambda } from './constructs/api-lambda';
import { ApiGateway } from './constructs/api-gateway';

export class TinyLinkerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const tables = new DynamoDBTables(this, 'Tables');

    const lambda = new ApiLambda(this, 'Lambda', {
      urlsTable: tables.urlsTable,
      analyticsTable: tables.analyticsTable,
      rateLimitsTable: tables.rateLimitsTable,
    });

    const api = new ApiGateway(this, 'Api', {
      handler: lambda.handler,
    });

    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.api.url,
      description: 'TinyLinker Stack',
    });
  }
}
