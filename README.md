# NeoBurnIn
Server and client implemented for the UT boards burn in process.


## Usage
All for scripts (`{Ctrl,Data}{Client,Server}.py`) have identical command line
interface:
```
<script_name> --config-file <path_to_config_file>
```

A sample configuration file for each script can be found at both project root
and `measurements` folder.


### `CtrlServer.py`
#### To control USB relay
```
curl -X POST http://<ip_addr_of_pi>:<port>/relay/0001:0003:00/2/on
curl -X POST http://<ip_addr_of_pi>:<port>/relay/0001:0003:00/2/off
```


## Running tests
Install `pytest`, then:
```
cd ./test
pytest .
```
