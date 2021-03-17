# sdx-tester

The tester application mimics SDX's interaction with RASRM, EQ and DAP, allowing all the major functionality 
that the SDX project provides to be tested. It is made up of an interactive front-end, unittests and Integration tests.

**Important:** Changes made to any SDX service require ALL tests to be run against the branch before being
merged into main. This can be achieved by deploying the feature-branch to your own kubernetes cluster via the scripts
in SDX-Concourse.

## Interactions

**SDX-Tester mimics the following interactions**

| External Interaction | Functionality                                                                                                                 |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| RAS-RM               | Puts SEFT survey submissions within `ons-sdx-{{project_id}}-sefts` GCP Bucket and publishes to `seft-topic` PubSub Topic.     |
| RAS-RM               | Acknowledges Receipt sent to RAS-RM via `receipt-topic`                                                                       |
| EQ                   | Publishes JSON survey submissions to `survey-topic` PubSub Topic                                                              |
| DAP                  | Subscribes to `dap-topic`, acknowledging processed submissions.                                                               |
| DAP                  | reads data out of `ons-sdx-{{project_id}}-outputs` GCP Bucket                                                                 |
| DAP                  | Publishes to `dap-receipt-topic`, kicking off cleanup cloud function                                                          |

**Diagram of dataflow:**

![](./images/sdx-tester.png?raw=true)

NB:
- Please refer to Key
- Note that this diagram does not show the interactions with the Quarantine Topics.

## Front-end

Tester provides a UI that allows users to select, edit and submit both JSON Surveys and SEFTs. The UI also provides functionality
to verify the data and kick off the cleanup function 

## Integration Tests

The integration tests run all JSON surveys, SEFT's and known quarantined submissions through the system and ensures we
receive the correct responses.

**run locally:**
`make integration-test`

## Cleanup Tests

This set of integration tests are used to test SDX's ability to cleanup Datastore and the GCP buckets once DAP have
confirmed the data is stored within the ONS network.

**run locally:**
`make cleanup-test`

Run order:
1. **test_setup.py** - cleans exisiting data from Datastore and puts test data in both buckets and Datastore.
2. **test_publish_receipt** - publishes corresponding messages to `dap-receipt-topic` to trigger cloud function.
3. **test_cleanup.py** - looks into Datastore and the bucket, checking if entries have been deleted.


NB:
- Please ensure the infrastructure is deployed including the cloud function
 
## Comment Tests

Set of integration tests that ensure that sdx-collate, kubernetes cronjob and sdx-deliver are working correctly to
generate and deliver the daily comments.

**run locally:**
`make comment-test`

Run order:
1. **test_setup.py** - wipes data within Datastore and the `{project_id}-outputs/comment` bucket/folder. 
2. Trigger CronJob
3. **test_comments.py** - verifies the spreadsheet that was generated using pandas and then deletes after verification
4. Remove triggered CronJob


## Performance Tests

A set of tests that measure the speed of SDX.

**run locally:**
`make performance-test:`

Run order:
1. **setup.py** - puts 500 sefts into ons-sdx-{{project_id}}-sefts GCP Bucket
2. **test_performance.py** - Runs 500 sefts and surveys through SDX, measuring time taken.

## Configuration
| Environment Variable           | Description
|--------------------------------|------------------------------------
| PROJECT_ID                     | Name of project
| OUTPUT_BUCKET_NAME             | Output bucket `{project_id}-outputs`
| INPUT_SEFT_BUCKET              | SEFT input bucket `{project_id}-sefts`
| DAP_SUBSCRIPTION               | Subscription to message going to dap
| SURVEY_QUARANTINE_SUBSCRIPTION | Quarantine queue for JSON submissions
| SEFT_QUARANTINE_SUBSCRIPTION   | Quarantine queue for SEFT submissions
| RECEIPT_SUBSCRIPTION           | Subscription to receipt going to RASRM
| DAP_RECEIPT_TOPIC              | Publishes to topic triggering cleanup cloud function
| MAX_WAIT_TIME_SECS             | Time until listener times out listening for a submission
| KEY_PURPOSE_SUBMISSION         | Purpose of encryption key

## License

Copyright © 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.