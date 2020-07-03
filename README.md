[![New Relic Experimental header](https://github.com/newrelic/opensource-website/raw/master/src/images/categories/Experimental.png)](https://opensource.newrelic.com/oss-category/#new-relic-experimental)

# AWS Control Tower Customization for Integration with New Relic

> This project helps you setup Control Tower customizations in your AWS Control Tower master account, so that any new accounts you enroll in your organizations are automatically integrated with New Relic's Telemetry Data Platform.

## Installation

> No installation is necessary. The repo includes a couple of CloudFormation templates that you are free to download or directly reference when trying to create CloudFormation stacks using them, as described in [Getting Started](#Getting-Started)

## Getting Started
> [AWS Control Tower](https://aws.amazon.com/controltower/) landing zone is required to be setup on your AWS account (usually the master payer account) in a home region of your preference. Your AWS Control Tower master account is the account that you created specifically for your landing zone. For information about setting up an AWS Control Tower landing zone, see [Getting Started with AWS Control Tower](https://docs.aws.amazon.com/controltower/latest/userguide/getting-started-with-control-tower.html) in the AWS Control Tower User Guide.

> New Relic Integrations requires use of an active New Relic account with [Infrastructure Pro](https://newrelic.com/products/infrastructure/pricing) enabled.  If you don’t have one already, you can [sign up](https://newrelic.com/signup/?trial=infrastructure) for free. After you’ve signed up for a free New Relic account, you can navigate to `INFRASTRUCTURE` link on the top menu bar. You will be taken to the Infrastructure page, where you can click the `Amazon Web Services` tile to get started.

## Usage
> This solution includes a couple of AWS CloudFormation templates (`yml` files) you deploy in your AWS account that launches all the components necessary to integrate New Relic with your AWS accounts that you enroll or create using the Account Factory in your AWS Control Tower master account.

> The solution must be deployed in your AWS Control Tower master account.

> First, create a Stack Set (not Stack) from [newrelic-stack-set.yml](templates/newrelic-stack-set.yml) template using `AWSControlTowerStackSetRole` IAM Role that should be already provisioned by Control Tower landing zone. This Stack Set includes the IAM Role and Managed Policy needed for integrating your AWS account with New Relic. You will need to supply your New Relic Account Id in the `NewRelicAccountNumber` parameter. This Role and Policy is supposed to be deployed to a single region in your AWS account, and it is the same as the home region of your Control Tower master account. Make sure to name the  Stack Set as `NewRelic-Integration`.

```
aws cloudformation create-stack-set \
    --stack-set-name NewRelic-Integration \
    --template-body https://raw.githubusercontent.com/newrelic-experimental/newrelic-control-tower-customization/master/templates/newrelic-stack-set.yml \
    --description "Adds in New Relic Integration to your AWS accounts" \
    --parameters ParameterKey=NewRelicAccountNumber,ParameterValue=<YOUR_NEW_RELIC_ACCOUNT_ID> \
    --capabilities CAPABILITY_NAMED_IAM \
    --administration-role-arn arn:aws:iam::<YOUR_AWS_CONTROL_TOWER_MASTER_ACCOUNT_ID>:role/service-role/AWSControlTowerStackSetRole \
    --execution-role-name AWSControlTowerExecution \
    --permission-model SELF_MANAGED
```

> Next, create a Stack from [control-tower-customization.yml](templates/control-tower-customization.yml) template. This template does not accept any parameters. Every time a new account is enrolled using the Account Factory from the Control Tower master account, it will be integrated with New Relic automatically.

```
aws cloudformation create-stack \
    --stack-name New-Relic-Control-Tower-Customization 
    --template-body https://raw.githubusercontent.com/newrelic-experimental/newrelic-control-tower-customization/master/templates/control-tower-customization.yml \
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
