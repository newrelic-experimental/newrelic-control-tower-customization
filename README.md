[![New Relic Experimental header](https://github.com/newrelic/opensource-website/raw/master/src/images/categories/Experimental.png)](https://opensource.newrelic.com/oss-category/#new-relic-experimental)

# AWS Control Tower Customization for Integration with New Relic

> This solution helps you automate setup of [New Relic's AWS integration](https://newrelic.com/aws) in your [AWS Control Tower](https://aws.amazon.com/controltower/) managed multi-account environment (landing zone). Once the solution is deployed to your [AWS Control Tower management account](https://docs.aws.amazon.com/controltower/latest/userguide/how-control-tower-works.html#what-is-master), any new accounts you enroll in your landing zone are automatically integrated with New Relic.

## Installation

> The repo includes a couple of [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates that you are free to download or directly reference their public GitHub URL when trying to create CloudFormation stacks using them, as described in [Usage](#Usage)

## Prerequisites
> Fully deployed AWS Control Tower is required for this solution. You will need administrator privileges in the AWS Control Tower management account to deploy the solution. For information about setting up an AWS Control Tower landing zone, see [Getting Started with AWS Control Tower](https://docs.aws.amazon.com/controltower/latest/userguide/getting-started-with-control-tower.html) in the AWS Control Tower User Guide.

> You are required to have an active New Relic account with Standard or higher pricing tier subscription, when using the new [New Relic One pricing plan](https://docs.newrelic.com/docs/accounts/accounts-billing/new-relic-one-pricing-users/pricing-billing). Don’t have an account yet? [Sign up](https://aws.amazon.com/marketplace/pp/B08L5FQMTG) for a perpetually free access to New Relic, which includes 100 GB of ingest per month and one Standard User license. You can also contact [New Relic Sales](https://newrelic.com/about/contact-us) for more details.

## Usage
> This solution includes a couple of AWS CloudFormation templates (`yml` files) you deploy in your AWS account that launches all the components necessary to integrate New Relic with your AWS accounts that you enroll or vend using the [Account Factory](https://aws.amazon.com/controltower/features/#Account_Factory) in your AWS Control Tower management account.

> The solution must be deployed in your AWS Control Tower management account, in the home [Region](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/#Regions) of your Control Tower management account. This is the Region where your AWS Control Tower landing zone was set up.

> First, create a StackSet (not Stack) from [newrelic-stack-set.yml](templates/newrelic-stack-set.yml) template using `AWSControlTowerStackSetRole` IAM Role that should be already provisioned by Control Tower. This StackSet includes the IAM Role and Managed Policy needed for integrating your AWS account with New Relic. You will need to supply your New Relic account ID in the `NewRelicAccountNumber` parameter. 

>1. Make sure to name the StackSet as `NewRelic-Integration`.
>2. Replace `YOUR_NEW_RELIC_ACCOUNT_ID` with your New Relic account ID. For more information about how to get this information, see [Account ID](https://docs.newrelic.com/docs/accounts/accounts-billing/account-setup/account-id) in the New Relic documentation.
>3. Replace `YOUR_CONTROL_TOWER_MANAGEMENT_ACCOUNT_ID` with your AWS account ID of your AWS Control Tower management account. For further details on how to get this information, see [Your AWS account identifiers](https://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html) in the AWS General Reference.


```
aws cloudformation create-stack-set \
  --stack-set-name NewRelic-Integration \
  --template-body https://raw.githubusercontent.com/newrelic-experimental/newrelic-control-tower-customization/master/templates/newrelic-stack-set.yml \
  --description "Adds in New Relic integration to your AWS accounts" \
  --parameters ParameterKey=NewRelicAccountNumber,ParameterValue=<YOUR_NEW_RELIC_ACCOUNT_ID> \
  --capabilities CAPABILITY_NAMED_IAM \
  --administration-role-arn arn:aws:iam::<YOUR_CONTROL_TOWER_MANAGEMENT_ACCOUNT_ID>:role/service-role/AWSControlTowerStackSetRole \
  --execution-role-name AWSControlTowerExecution
```

> Next, create a Stack from [control-tower-customization.yml](templates/control-tower-customization.yml) template. This template does not accept any parameters.

```
aws cloudformation create-stack \
  --stack-name New-Relic-Control-Tower-Customization 
  --template-body https://raw.githubusercontent.com/newrelic-experimental/newrelic-control-tower-customization/master/templates/control-tower-customization.yml \
  --capabilities CAPABILITY_NAMED_IAM
```
For more details, see the solution [implementation guide](https://d1.awsstatic.com/Marketplace/solutions-center/downloads/New-Relic-AWS-Control-Tower-Implementation-Guide.pdf) posted in [Solutions for AWS Control Tower in AWS Marketplace](https://aws.amazon.com/marketplace/solutions/control-tower/operational-intelligence#New_Relic).

## Verifying the New Relic integration
> After you've deployed the solution, you will need to register (activate) the AWS accounts that you want to monitor with New Relic. 

>1. Log in to your [New Relic account](https://one.newrelic.com/).
>2. Click the `Infrastructure` link on the top navigation bar. You will be taken to the `Infrastructure` page. If you happen to have access to multiple New Relic accounts, begin by choosing the New Relic account that you used for this implementation, from the dropdown list labeled `Infrastructure`, in the top left area of the screen. Otherwise, you should already see your New Relic account show up next to the label. Make sure the account ID matches the one you used in this implementation.
>3. Next, select the `AWS` tab and finally click the `+ Add an AWS account` link, in the right portion of the screen. In case you are adding an AWS account to your New Relic account for the first time, you may see a different screen. As instructed on the screen, click any service tile to get started.
If you see the `Choose an integration mode` screen, click `Use API polling` button.
>4. You will be presented with a multi-step account setup wizard. Since the solution automates the New Relic integration in your AWS accounts, you can move past the first few steps by clicking the `Next` button on each step until you get to Step 5  named `Account Details`. You are skipping the steps since the solution automates the process of setting up the “New Relic Integration” IAM Role (done in Step 1 through Step 3). Step 4 named `Budgets Policy` is optional but recommended for you to keep track of your AWS cost.
>5. While you are in the `Account Details` step, type in the preferred name for your AWS account. This can be anything that helps you identify your AWS account from your New Relic account. Since you can integrate multiple AWS accounts, choose a name that’s unique, or try matching it with the actual name of your AWS account. Enter the ARN of the “New Relic Integration” IAM role that was setup by the solution in your newly enrolled AWS account.
>6. Finally, Click `Next` button. You will be taken to Step 6, named `Select Services`. Select the AWS services you would like to monitor. 
 Once your AWS account shows up, click on `Account status dashboard` link to view the account dashboard.

## Tearing it Down
>If you intend to deploy the solution for testing and demonstration purposes and you don’t intend to use New Relic AWS integrations any longer, you can [Uninstall New Relic AWS integration](https://docs.newrelic.com/docs/infrastructure/install-infrastructure-agent/update-or-uninstall/uninstall-infrastructure-integrations#uninstall-aws).

## Support

New Relic hosts and moderates an online forum where customers can interact with New Relic employees as well as other customers to get help and share best practices. Like all official New Relic open source projects, there's a related Community topic in the New Relic Explorers Hub.

## Contributing
We encourage your contributions to improve [project name]! Keep in mind when you submit your pull request, you'll need to sign the CLA via the click-through using CLA-Assistant. You only have to sign the CLA one time per project.
If you have any questions, or to execute our corporate CLA, required if your contribution is on behalf of a company,  please drop us an email at opensource@newrelic.com.

## License
`AWS Control Tower Customization for Integration with New Relic` is licensed under the [Apache 2.0](http://apache.org/licenses/LICENSE-2.0.txt) License.
