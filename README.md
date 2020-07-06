# NeoBurnIn
Server and client implemented for the UT boards burn in process.


## Installation on Raspbian

1. Make sure Python 3.6+ is installed in Raspbian.

2. Configure the kernel parameters so that 1-wire protocol devices are
    recognized. Follow the instruction [here](https://github.com/umd-lhcb/rpi.burnin#setup).

3. Install the Udev rule for USB relay following the instruction [here](https://github.com/umd-lhcb/rpi.burnin#setup-1)

4. Install `hidapi`:
    ```
    sudo apt update
    sudo apt install libhidapi-hidraw0 libhidapi-libusb0
    ```

5. Clone this project

6. Install the dependencies with:
    ```
    pip3 install --user -r ./requirements.txt
    ```


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
