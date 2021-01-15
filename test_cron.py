import os
os.system("kubectl create job --from=cronjob/sdx-collate test-collate")
