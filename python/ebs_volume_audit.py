import json
from library.ebs_unencrypted_volumes_analyzer import ebs_unencrypted_volumes_analyzer
from library.ebs_gp2_analyzer import ebs_gp2_analyzer

def lambda_handler(event, context):
    regions_list = ['eu-west-1', 'ap-northeast-3']

    ebs_unecrypted_volumes = ebs_unencrypted_volumes_analyzer()
    ebs_unecrypted_volumes.analyze(regions_list)

    ebs_gp2_volumes = ebs_gp2_analyzer()
    ebs_gp2_volumes.analyze(regions_list)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
