import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import { DynamoDBTables } from './constructs/dynamodb-tables';
import { ApiLambda } from './constructs/api-lambda';
import { ApiGateway } from './constructs/api-gateway';
import { CustomDomain } from './constructs/dns';

export interface TinyLinkerStackProps extends cdk.StackProps {
  domainName: string;
}

export class TinyLinkerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: TinyLinkerStackProps) {
    super(scope, id, props);

    const domainName = props.domainName

    const tables = new DynamoDBTables(this, 'Tables');

    const lambda = new ApiLambda(this, 'Lambda', {
      urlsTable: tables.urlsTable,
      analyticsTable: tables.analyticsTable,
      rateLimitsTable: tables.rateLimitsTable,
      baseUrl: `https://${domainName}`,
    });

    const api = new ApiGateway(this, 'Api', {
      handler: lambda.handler,
    });

    const customDomain = new CustomDomain(this, 'CustomDomain', {
      domainName: domainName,
      api: api.api,
    });

    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.api.url,
      description: 'TinyLinker Stack',
    });

    new cdk.CfnOutput(this, 'CustomDomainUrl', {
      value: `https://${domainName}`,
      description: 'Custom Domain URL',
    });

    new cdk.CfnOutput(this, 'NameServers', {
      value: cdk.Fn.join(', ', customDomain.hostedZone.hostedZoneNameServers || []),
      description: 'Route53 Name Servers'
    });
  }
}
