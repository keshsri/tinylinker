#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib/core';
import { TinyLinkerStack } from '../lib/tiny-linker-stack';

const app = new cdk.App();

new TinyLinkerStack(app, 'TinyLinkerStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  },
});
