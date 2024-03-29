from datetime import datetime


# Taken from
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_instances.html
DESCRIBE_DB_INSTANCES_RESPONSE = {
    "DBInstanceIdentifier": "string",
    "DBInstanceClass": "string",
    "Engine": "string",
    "DBInstanceStatus": "string",
    "AutomaticRestartTime": datetime(2015, 1, 1),
    "MasterUsername": "string",
    "DBName": "string",
    "Endpoint": {"Address": "string", "Port": 123, "HostedZoneId": "string"},
    "AllocatedStorage": 123,
    "InstanceCreateTime": datetime(2015, 1, 1),
    "PreferredBackupWindow": "string",
    "BackupRetentionPeriod": 123,
    "DBSecurityGroups": [
        {"DBSecurityGroupName": "string", "Status": "string"},
    ],
    "VpcSecurityGroups": [
        {"VpcSecurityGroupId": "vpcsg1", "Status": "string"},
        {"VpcSecurityGroupId": "vpcsg2", "Status": "string"},
    ],
    "DBParameterGroups": [
        {"DBParameterGroupName": "string", "ParameterApplyStatus": "string"},
    ],
    "AvailabilityZone": "string",
    "DBSubnetGroup": {
        "DBSubnetGroupName": "string",
        "DBSubnetGroupDescription": "string",
        "VpcId": "string",
        "SubnetGroupStatus": "string",
        "Subnets": [
            {
                "SubnetIdentifier": "string",
                "SubnetAvailabilityZone": {"Name": "string"},
                "SubnetOutpost": {"Arn": "string"},
                "SubnetStatus": "string",
            },
        ],
        "DBSubnetGroupArn": "string",
        "SupportedNetworkTypes": [
            "string",
        ],
    },
    "PreferredMaintenanceWindow": "string",
    "PendingModifiedValues": {
        "DBInstanceClass": "string",
        "AllocatedStorage": 123,
        "MasterUserPassword": "string",
        "Port": 123,
        "BackupRetentionPeriod": 123,
        "MultiAZ": False,
        "EngineVersion": "string",
        "LicenseModel": "string",
        "Iops": 123,
        "DBInstanceIdentifier": "string",
        "StorageType": "string",
        "CACertificateIdentifier": "string",
        "DBSubnetGroupName": "string",
        "PendingCloudwatchLogsExports": {
            "LogTypesToEnable": [
                "string",
            ],
            "LogTypesToDisable": [
                "string",
            ],
        },
        "ProcessorFeatures": [
            {"Name": "string", "Value": "string"},
        ],
        "IAMDatabaseAuthenticationEnabled": False,
        "AutomationMode": "full",
        "ResumeFullAutomationModeTime": datetime(2015, 1, 1),
        "StorageThroughput": 123,
    },
    "LatestRestorableTime": datetime(2015, 1, 1),
    "MultiAZ": False,
    "EngineVersion": "string",
    "AutoMinorVersionUpgrade": False,
    "ReadReplicaSourceDBInstanceIdentifier": "string",
    "ReadReplicaDBInstanceIdentifiers": [
        "string",
    ],
    "ReadReplicaDBClusterIdentifiers": [
        "string",
    ],
    "ReplicaMode": "open-read-only",
    "LicenseModel": "string",
    "Iops": 123,
    "OptionGroupMemberships": [
        {"OptionGroupName": "string", "Status": "string"},
    ],
    "CharacterSetName": "string",
    "NcharCharacterSetName": "string",
    "SecondaryAvailabilityZone": "string",
    "PubliclyAccessible": False,
    "StatusInfos": [
        {
            "StatusType": "string",
            "Normal": True,
            "Status": "string",
            "Message": "string",
        },
    ],
    "StorageType": "string",
    "TdeCredentialArn": "string",
    "DbInstancePort": 123,
    "DBClusterIdentifier": "string",
    "StorageEncrypted": True,
    "KmsKeyId": "string",
    "DbiResourceId": "string",
    "CACertificateIdentifier": "string",
    "DomainMemberships": [
        {
            "Domain": "string",
            "Status": "string",
            "FQDN": "string",
            "IAMRoleName": "string",
        },
    ],
    "CopyTagsToSnapshot": True,
    "MonitoringInterval": 123,
    "EnhancedMonitoringResourceArn": "string",
    "MonitoringRoleArn": "string",
    "PromotionTier": 123,
    "DBInstanceArn": "string",
    "Timezone": "string",
    "IAMDatabaseAuthenticationEnabled": True,
    "PerformanceInsightsEnabled": True,
    "PerformanceInsightsKMSKeyId": "string",
    "PerformanceInsightsRetentionPeriod": 123,
    "EnabledCloudwatchLogsExports": [
        "string",
    ],
    "ProcessorFeatures": [
        {"Name": "string", "Value": "string"},
    ],
    "DeletionProtection": True,
    "AssociatedRoles": [
        {"RoleArn": "string", "FeatureName": "string", "Status": "string"},
    ],
    "ListenerEndpoint": {"Address": "string", "Port": 123, "HostedZoneId": "string"},
    "MaxAllocatedStorage": 123,
    "TagList": [
        {"Key": "string", "Value": "string"},
    ],
    "DBInstanceAutomatedBackupsReplications": [
        {"DBInstanceAutomatedBackupsArn": "string"},
    ],
    "CustomerOwnedIpEnabled": True,
    "AwsBackupRecoveryPointArn": "string",
    "ActivityStreamStatus": "stopped",
    "ActivityStreamKmsKeyId": "string",
    "ActivityStreamKinesisStreamName": "string",
    "ActivityStreamMode": "sync",
    "ActivityStreamEngineNativeAuditFieldsIncluded": True,
    "AutomationMode": "full",
    "ResumeFullAutomationModeTime": datetime(2015, 1, 1),
    "CustomIamInstanceProfile": "string",
    "BackupTarget": "string",
    "NetworkType": "string",
    "ActivityStreamPolicyStatus": "locked",
    "StorageThroughput": 123,
    "DBSystemId": "string",
    "MasterUserSecret": {
        "SecretArn": "string",
        "SecretStatus": "string",
        "KmsKeyId": "string",
    },
    "CertificateDetails": {"CAIdentifier": "string", "ValidTill": datetime(2015, 1, 1)},
    "ReadReplicaSourceDBClusterIdentifier": "string",
}
