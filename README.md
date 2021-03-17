# Freeflowconnect backend

This project contains the api and the redis implementation for the Freeflowconnect backend.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
make install
```

### Running in debug (Using VsCode)

Auto generated launch.json file (Press F5 and select Flask)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "0"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true
        }
    ]
}
```

### Running with docker

```
make docker-run
```


### Running with UWSGI

```
make server-run
```

### Running with Flask

```
make flask-run
```
