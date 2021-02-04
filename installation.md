#### iperf3 最新版
sudo apt-get -y install build-essential && git clone -b 3.9 https://github.com/esnet/iperf.git && cd iperf && ./configure && make && sudo make install && sudo ldconfig && iperf3 --version

ubuntu 18.04 使用netplan管理配置
sudo netplan apply 更新配置
cat /run/systemd/resolve/resolv.conf