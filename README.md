[![New Relic Experimental header](https://github.com/newrelic/opensource-website/raw/master/src/images/categories/Experimental.png)](https://opensource.newrelic.com/oss-category/#new-relic-experimental)

# AWS Control Tower Customization for Integration with New Relic

> This project helps you setup Control Tower customizations in your AWS Control Tower landing zone, so that any new accounts you enroll in your organizations are automatically integrated with New Relic's Telemetry Data Platform.

## Installation

> No installation is necessary. The repo includes a couple of CloudFormation templates that you are free to download or directly reference when trying to create CloudFormation stacks using them.

## Getting Started
> [AWS Control Tower](https://aws.amazon.com/controltower/) landing zone is required to be setup on your AWS account (usually the master payer account) in a home region of your preference. For information about setting up an AWS Control Tower landing zone, see [Getting Started with AWS Control Tower](https://docs.aws.amazon.com/controltower/latest/userguide/getting-started-with-control-tower.html) in the AWS Control Tower User Guide.

> New Relic Integrations requires use of an active New Relic account.  If you don’t have one already, you can [sign up](https://newrelic.com/signup/) today for free.

## Usage
> This solution includes a couple of AWS CloudFormation templates (`yml` files) you deploy in your AWS account that launches all the components necessary to integrate New Relic with your AWS accounts that you enroll or create using the Account Factory in your AWS Control Tower landing zone.

> The solution must be deployed in the same region and account where your AWS Control Tower landing zone is deployed.

> First, create a Stack Set (not Stack) from [newrelic-stack-set.yml](templates/newrelic-stack-set.yml) template using `AWSControlTowerStackSetRole` IAM Role that should be already provisioned by Control Tower landing zone. This Stack Set includes the IAM Role and Managed Policy needed for integrating your aws account with New Relic. You will need to supply your New Relic Account Id in the `NewRelicAccountNumber` parameter. This Role and Policy is supposed to be deployed to a single region in your aws account, and you can choose by providing a suitable home region code in the `PolicyRegion` parameter. Make sure to name the  Stack Set as `NewRelic-Integration`.

```
aws cloudformation create-stack-set \
    --stack-set-name NewRelic-Integration \
    --template-body https://github.com/newrelic-experimental/newrelic-control-tower-customization/blob/master/templates/newrelic-stack-set.yml \
    --description "Adds in New Relic integration to your aws accounts" \
    --parameters ParameterKey=NewRelicAccountNumber,ParameterValue=<YOUR_NEW_RELIC_ACCOUNT_ID> ParameterKey=PolicyRegion,ParameterValue=<REGION_WHERE_YOU_WANT_POLICIES_DEPLOYED> \
    --capabilities CAPABILITY_NAMED_IAM \
    --administration-role-arn arn:aws:iam::<YOUR_LANZING_ZONE_ACCOUNT_ID>:role/service-role/AWSControlTowerStackSetRole \
    --execution-role-name AWSControlTowerExecution \
    --permission-model SELF_MANAGED
```

> Next, create a Stack from [control-tower-customization.yml](templates/control-tower-customization.yml) template. This template does not accept any parameters. Every time a new account is enrolled using the Account Factory from the Control Tower landing zone account, it will be integrated with New Relic automatically.

```
aws cloudformation create-stack \
    --stack-name New-Relic-Control-Tower-Customization 
    --template-body https://github.com/newrelic-experimental/newrelic-control-tower-customization/blob/master/templates/control-tower-customization.yml \
    --capabilities CAPABILITY_NAMED_IAM
```

## Support

New Relic hosts and moderates an online forum where customers can interact with New Relic employees as well as other customers to get help and share best practices. Like all official New Relic open source projects, there's a related Community topic in the New Relic Explorers Hub.

## Contributing
We encourage your contributions to improve [project name]! Keep in mind when you submit your pull request, you'll need to sign the CLA via the click-through using CLA-Assistant. You only have to sign the CLA one time per project.
If you have any questions, or to execute our corporate CLA, required if your contribution is on behalf of a company,  please drop us an email at opensource@newrelic.com.

## License
[Project Name] is licensed under the [Apache 2.0](http://apache.org/licenses/LICENSE-2.0.txt) License.
>[If applicable: The [project name] also uses source code from third-party libraries. You can find full details on which libraries are used and the terms under which they are licensed in the third-party notices document.]
