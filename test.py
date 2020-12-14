from app.tester import run_test
def run_tests():
    payload = '''{
    "collection": {
        "exercise_sid": "XxsteeWv",
        "instrument_id": "0167",
        "period": "1704"
    },
    "data": {
        "46": "123",
        "47": "456",
        "50": "789",
        "51": "111",
        "52": "222",
        "53": "333",
        "54": "444",
        "146": "No",
        "d12": "Yes",
        "d40": "Yes"
    },
    "flushed": false,
    "metadata": {
        "ref_period_end_date": "2016-05-31",
        "ref_period_start_date": "2016-05-01",
        "ru_ref": "49900108249D",
        "user_id": "UNKNOWN"
    },
    "origin": "uk.gov.ons.edc.eq",
    "started_at": "2017-07-05T10:54:11.548611+00:00",
    "submitted_at": "2017-07-05T14:49:33.448608+00:00",
    "type": "uk.gov.ons.edc.eq:surveyresponse",
    "version": "0.0.1",
    "survey_id": "009",
    "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3",
    "tx_id": "b93d5852-359d-4e37-8338-c949bcb98617"
}'''
    tx_id = "b93d5852-359d-4e37-8338-c949bcb98617"
    # with open("./keys.yml") as file:
    #     secrets_from_file = yaml.safe_load(file)
    #
    # key_store = KeyStore(secrets_from_file)
    # payload = encrypt(submission, key_store, 'submission')
    #
    passed = run_test(payload, tx_id)
    if passed:
        return True

if __name__ == '__main__':
    run_tests()
