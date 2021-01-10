#!/bin/bash
# interrupt coalescing switch
switch(){
	ssh zhufengtian@192.168.67.5 "sudo ethtool -C enp27s0f0 rx-usecs $1" 1>/dev/null
	printf "IC switch $1\n"
}
switch $@
