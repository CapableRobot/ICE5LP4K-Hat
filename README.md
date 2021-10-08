# ICE5LP4K-Hat

## System Setup 

```
cd loader
make
cd ..

mkdir install
cd install
wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
chmod +x litex_setup.py
./litex_setup.py init install --user 

pip3 install spidev
```
