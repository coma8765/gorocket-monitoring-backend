# GoRocket monitoring backend
>This application can be used as a server solution for transferring flight data via a web interface. 
>Jet propulsion championship

## Data format
* TeamID – code team
* Time – ms (Arduino func millis())
* Voltage - voltage
* A – Acceleration vector modulus m/s2
* Altitude – Altitude in meters
* Start point - is started: 1 (true) / 0 (false)
* Apogee point - is apogee: 1 (true) / 0 (false)
* Activate point - is rescue system activate: 1 (true) / 0 (false)
* Sputnik point - is catch sputnik: 1 (true) / 0 (false)
* Landing point - is landing: 1 (true) / 0 (false)
* \n - end of line LF
#### Example: 1A;678903;8.12;9.8;44.5;1;0;0;0;0;


## Functions
* API Endpoint all messages
* WebSocket for realtime getting messages
* Save data


## Run
### Require
* python 3.9+

### Install dependencies
```shell
pip install pipenv
pipenv install
```

### Run application
```shell
pipenv run uvicorn app.main:app
```