.PHONY: install server client
install: ; pip install -r requirements.txt
server:  ; python burnserver.py      # exposes the Vivado burn commands over HTTP
client:  ; python burnclient.py
