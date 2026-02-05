import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export interface DecisionLedgerStackProps extends cdk.StackProps {
  envName: string;
}

export class DecisionLedgerStack extends cdk.Stack {
  public readonly table: dynamodb.Table;
  public readonly slackSecrets: secretsmanager.Secret;

  constructor(scope: Construct, id: string, props: DecisionLedgerStackProps) {
    super(scope, id, props);

    const { envName } = props;

    // ==========================================================================
    // DynamoDB Table
    // ==========================================================================
    // Single-table design for Decision Ledger
    // Stores: Projects, Project Members, Decisions, Decision Participants, Tags
    // ==========================================================================

    this.table = new dynamodb.Table(this, 'DecisionLedgerTable', {
      tableName: `decision-ledger-${envName}`,
      partitionKey: {
        name: 'PK',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'SK',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: envName === 'prod'
        ? cdk.RemovalPolicy.RETAIN
        : cdk.RemovalPolicy.DESTROY,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: envName === 'prod',
      },

      // Enable DynamoDB Streams for future OpenSearch integration
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });

    // -------------------------------------------------------------------------
    // GSI1: User Projects
    // Query pattern: List all projects a user is a member of
    // PK: user_id, SK: PK (to get PROJECT#<id>)
    // -------------------------------------------------------------------------
    this.table.addGlobalSecondaryIndex({
      indexName: 'GSI1-UserProjects',
      partitionKey: {
        name: 'user_id',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'PK',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // -------------------------------------------------------------------------
    // GSI2: Project Decisions
    // Query pattern: List all decisions for a project, sorted by created_at
    // PK: project_id, SK: created_at
    // -------------------------------------------------------------------------
    this.table.addGlobalSecondaryIndex({
      indexName: 'GSI2-ProjectDecisions',
      partitionKey: {
        name: 'project_id',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'created_at',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // -------------------------------------------------------------------------
    // GSI3: Status Filter
    // Query pattern: Filter decisions by status within a project
    // PK: gsi3_pk (format: "status#project_id"), SK: created_at
    // Example: "confirmed#PROJECT#123" or "open#PROJECT#123"
    // -------------------------------------------------------------------------
    this.table.addGlobalSecondaryIndex({
      indexName: 'GSI3-StatusFilter',
      partitionKey: {
        name: 'gsi3_pk',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'created_at',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // -------------------------------------------------------------------------
    // GSI4: Supersedes Lookup
    // Query pattern: Find the decision that supersedes a given decision
    // PK: supersedes_id
    // -------------------------------------------------------------------------
    this.table.addGlobalSecondaryIndex({
      indexName: 'GSI4-Supersedes',
      partitionKey: {
        name: 'supersedes_id',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.KEYS_ONLY,
    });

    // ==========================================================================
    // Secrets Manager - Slack Credentials
    // ==========================================================================
    // Stores Slack bot token and signing secret
    // ==========================================================================

    this.slackSecrets = new secretsmanager.Secret(this, 'SlackSecrets', {
      secretName: `decision-ledger/${envName}/slack`,
      description: 'Slack bot credentials for Decision Ledger',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          bot_token: 'PLACEHOLDER_BOT_TOKEN',
          signing_secret: 'PLACEHOLDER_SIGNING_SECRET',
          app_token: 'PLACEHOLDER_APP_TOKEN',
        }),
        generateStringKey: 'dummy', // We'll update these manually
      },
    });

    // ==========================================================================
    // Outputs
    // ==========================================================================

    new cdk.CfnOutput(this, 'TableName', {
      value: this.table.tableName,
      description: 'DynamoDB table name',
      exportName: `DecisionLedger-${envName}-TableName`,
    });

    new cdk.CfnOutput(this, 'TableArn', {
      value: this.table.tableArn,
      description: 'DynamoDB table ARN',
      exportName: `DecisionLedger-${envName}-TableArn`,
    });

    new cdk.CfnOutput(this, 'TableStreamArn', {
      value: this.table.tableStreamArn || '',
      description: 'DynamoDB table stream ARN (for OpenSearch integration)',
      exportName: `DecisionLedger-${envName}-TableStreamArn`,
    });

    new cdk.CfnOutput(this, 'SlackSecretsArn', {
      value: this.slackSecrets.secretArn,
      description: 'Slack secrets ARN',
      exportName: `DecisionLedger-${envName}-SlackSecretsArn`,
    });
  }
}
