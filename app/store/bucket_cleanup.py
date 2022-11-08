from google.cloud import storage


def delete_files_in_bucket(bucket_name):
    storage_client = storage.Client()
    file_list = storage_client.list_blobs(bucket_name)
    bucket = storage_client.bucket(bucket_name)

    for file in file_list:
        blob = bucket.blob(file.name)
        blob.delete()
