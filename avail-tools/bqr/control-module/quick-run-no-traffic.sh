# !/bin/bash
# ./quick-run-no-traffic.sh data_filename [send_script]
# send_script should be like "deploy-tools/sender.sh"
if [[ $# -eq 2 ]]; then
	bash control-module/quick-run.sh $2
else
	bash control-module/quick-run.sh
fi
bash fetch-tools/fetch-timestamp.sh $1