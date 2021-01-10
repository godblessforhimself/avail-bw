nohup ./pathchirp_rcv &
nohup ./pathchirp_snd &
./pathchirp_run -S 192.168.2.3 -R 192.168.5.1 -n 11 -d 1.5 -b 5 -J 6 -u 1000 -p 1472 -t 60 -s 1.2 -a 3

./pathchirp_run -S 192.168.2.3 -R 192.168.5.1 -n 11 -d 1.5 -J 6 -u 1000 -p 1472 -t 60 -s 1.2 -a 3

./pathchirp_run -S 192.168.2.3 -R 192.168.5.1 -t 60


# not accurate