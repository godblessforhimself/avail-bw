#!/bin/bash
prefix="/home/amax/jintao_test/avail-tools/data"
tick(){
	begin=$(date)
}
tock(){
	end=$(date)
	echo "$1: ${begin} -> ${end}"
	begin=$(date)
}
tick
bash experiment-scripts/spruce.sh ${prefix}/spruce-noIC 0 1>data/spruce.run 2>data/spruce.error
tock "spruce noIC"
bash experiment-scripts/igi-ptr.sh ${prefix}/igi-noIC 0 1>data/igi.run 2>data/igi.error
tock "igi noIC"
bash experiment-scripts/pathload.sh ${prefix}/pathload-noIC 0 1>data/pathload.run 2>data/pathload.error
tock "pathload noIC"
bash experiment-scripts/assolo.sh ${prefix}/assolo-noIC 0 1>data/assolo.run 2>data/assolo.error
tock "assolo noIC"
bash experiment-scripts/spruce.sh ${prefix}/spruce-IC 1 1>data/spruce-IC.run 2>data/spruce-IC.error
tock "spruce IC"
bash experiment-scripts/igi-ptr.sh ${prefix}/igi-IC 1 1>data/igi-IC.run 2>data/igi-IC.error
tock "igi IC"
bash experiment-scripts/pathload.sh ${prefix}/pathload-IC 1 1>data/pathload-IC.run 2>data/pathload-IC.error
tock "pathload IC"
bash experiment-scripts/assolo.sh ${prefix}/assolo-IC 1 1>data/assolo-IC.run 2>data/assolo-IC.error
tock "assolo IC"