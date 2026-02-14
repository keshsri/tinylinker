#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib/core';
import { TinyLinkerStack } from '../lib/tiny-linker-stack';

const app = new cdk.App();

const domainName = app.node.tryGetContext('domainName');

if (!domainName) {
  throw new Error('domainName context is required. Add the --context flag to the cdk commands');
}

new TinyLinkerStack(app, 'TinyLinkerStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-west-2'
  },
  domainName: domainName
});
