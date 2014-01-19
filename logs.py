import logging.config
import logging

hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)

hallog = logging.getLogger("elixys.hal")
hallog.setLevel(logging.DEBUG)
hallog.addHandler(hdlr)

statlog = logging.getLogger("elixys.stat")
statlog.setLevel(logging.DEBUG)
statlog.addHandler(hdlr)

errorlog = logging.getLogger("elixys.err")
errorlog.setLevel(logging.DEBUG)
errorlog.addHandler(hdlr)


hwsimlog = logging.getLogger("elixys.hwsim")
hwsimlog.setLevel(logging.DEBUG)
hwsimlog.addHandler(hdlr)


wsfhdlr = logging.FileHandler("wsserver.log",mode='a')
wsfhdlr.setLevel(logging.DEBUG)
wsslog = logging.getLogger("elixys.wsserver")
wsslog.setLevel(logging.DEBUG)
wsslog.addHandler(hdlr)
wsslog.addHandler(wsfhdlr)
