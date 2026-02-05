#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DecisionLedgerStack } from '../lib/decision-ledger-stack';

const app = new cdk.App();

// Get environment from context (default to 'dev')
const envName = app.node.tryGetContext('env') || 'dev';

// Environment-specific configuration
const envConfig: Record<string, { account?: string; region: string }> = {
  dev: {
    region: 'us-east-1',
  },
  prod: {
    region: 'us-east-1',
  },
};

const config = envConfig[envName] || envConfig.dev;

new DecisionLedgerStack(app, `DecisionLedger-${envName}`, {
  env: {
    account: config.account || process.env.CDK_DEFAULT_ACCOUNT,
    region: config.region || process.env.CDK_DEFAULT_REGION,
  },
  envName,
  description: `Decision Ledger infrastructure (${envName})`,
  tags: {
    Project: 'DecisionLedger',
    Environment: envName,
    ManagedBy: 'CDK',
  },
});
