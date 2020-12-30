NTP_SERVER="s2b.time.edu.cn"
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l zhufengtian -o StrictHostKeyChecking=no 192.168.67.5 'sudo ntpdate ${NTP_SERVER}'" >/dev/null
ssh -p 3970 amax@aliyun.ylxdzsw.com \
"ssh -l amax -o StrictHostKeyChecking=no 192.168.67.3 'sudo ntpdate ${NTP_SERVER}'" >/dev/null