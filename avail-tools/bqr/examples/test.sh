#bash examples/test.sh 0 c1.txt c2.txt c3.txt dag-time script bpf
x=$1
if [[ $1 -eq -1 ]];then
	echo "True"
fi
