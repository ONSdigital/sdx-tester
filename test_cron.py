import os

os.system("kubectl create job --from=cronjob/sdx-collate test-collate")

# Function to check bucket for comments and validate
# def check_bucket()
