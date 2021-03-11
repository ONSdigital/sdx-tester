# sdx-tester

The tester application mimics SDX's interaction with RASRM, EQ and DAP, allowing all the major functionality 
that the SDX project provides to be tested. It is made up of an interactive front-end, unittests and Integration tests.

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

**Diagram of flow:**

![](./images/sdx-tester.png?raw=true)

NB:
- Please refer to Key
- Note that this diagram does not show the interactions with the Quarantine Topics.
## Front-end

Tester provides a UI that allows users to select, edit and submit both JSON Surveys and SEFTs.  

## Cleanup Tests

## Comment Tests

## Integation Tests

## Performance Tests