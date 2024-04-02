cp template-staging.yml template.yml 
# Todo: figure out permission stuff for IAM list policies
# sam validate
sam build --use-container --debug
sam package --s3-bucket api-staging-prijslijst-info --output-template-file out.yml --region eu-central-1
sam deploy --template-file out.yml --stack-name api-staging-prijslijst-info --region eu-central-1 --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
