from typing import TypedDict, NotRequired

SurveyData = dict | list


class SurveyMetadata(TypedDict):
	"""
	Business Survey Metadata
	"""
	ru_name: str
	user_id: str
	period_id: str
	form_type: str
	ru_ref: str
	survey_id: str

	case_ref: NotRequired[str]
	case_type: NotRequired[str]
	display_address: NotRequired[str]
	employment_date: NotRequired[str]  # ISO_8601 date
	period_str: NotRequired[str]
	ref_p_start_date: NotRequired[str]  # ISO_8601 date
	ref_p_end_date: NotRequired[str]  # ISO_8601 date
	trad_as: NotRequired[str]
	sds_dataset_id: NotRequired[str]


class SurveySubmission(TypedDict):
	tx_id: str
	type: str
	version: str
	data_version: str
	origin: str
	flushed: bool
	submitted_at: str
	launch_language_code: str
	collection_exercise_sid: str
	case_id: str
	survey_metadata: SurveyMetadata
	data: SurveyData

	channel: NotRequired[str]
	region_code: NotRequired[str]
	schema_name: NotRequired[str]
	schema_url: NotRequired[str]
	started_at: NotRequired[str]
	submission_language_code: NotRequired[str]


class SeftMetadata(TypedDict):
	filename: str
	tx_id: str
	survey_id: str
	period: str
	ru_ref: str
	md5sum: str
	sizeBytes: int
	seft: bool


AbstractSubmission = SurveySubmission | SeftMetadata
