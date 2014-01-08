Elixys Hardware Software API
==============================================
pyelixys is a library for communicating with the Sofie Biosciences [sofiebiolink]
[Elixys hardware][elixyslink].  The the hardware is a design based upon the [mbed 
development board][mbedlink].  It communicates with the hardware using the 
[websocket protocol][websocketlink].  This library abstracts the hardware to python objects.

Developing with pyelixys
------------------------
First you should install python and virtualenv.
```bash
pip install virtualenv
virtualenv pyelixys
cd pyelixys
source bin/activate
git clone git@github.com:henryeherman/pyelixys.git
cd pyelixys
pip install -r requirements.txt
```

[mbedlink]: http://mbed.org/
[sofiebiolink]: http://sofiebio.com/
[elixyslink]: http://sofiebio.com/products/chemistry/
[websocketlink]: http://en.wikipedia.org/wiki/WebSocket
