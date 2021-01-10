./yaz -R
./yaz -S 192.168.5.1 -l 200 -n 50 -m 1 -s 50 -r 500

: <<'END'
usage: ./yaz <-R|-S <dest addr>>
   if sender (-S <destaddr>):
      (default destination address: 127.0.0.1
      -l <int>   minimum packet size (default: 200)
      -n <int>   packet stream length (default: 50)
      -m <int>   number of streams per measurement (default: 1)
      -r <float> set convergence resolution (default: 500.0 kb/s)
      -s <int>   mean inter-stream spacing (default: 50 milliseconds)
   for both sender and receiver:
      -p <port>  specify control port (13979)
      -P <port>  specify probe port (13989)
      -v         increase verbosity
END

# yaz dont stop iteration: abw is low(150-280Mbps)