# NeoBurnIn
Server and client implemented for the UT boards burn in process.


## `CtrlServer.py`
### To control USB relay
```
curl -X POST http://<ip_addr_of_pi>:<port>/relay/0001:0003:00/2/on
curl -X POST http://<ip_addr_of_pi>:<port>/relay/0001:0003:00/2/off
```
