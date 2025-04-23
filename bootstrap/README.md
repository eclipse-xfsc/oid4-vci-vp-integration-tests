# OCM-W Services Bootstrapping

This document describes the process of bootstrapping the OCM-W services and how to run tests against it.

The ocm-w BDD tests are intended to be run against services running locally bootstrapped using docker-compose.

## Prerequisites

- Docker Engine (Docker Desktop, Podman machine, Rancher ...)
- Access to the OCM-W docker registry (node-654e3bca7fbeeed18f81d7c7.ps-xaas.io)

## Bootstrapping

1. Using terminal from root `cd` into the `implementations/ocm-w` directory
2. Run the docker-compose command to start the services

Using makefile
```bash
make up
```
or Copypaste command `up` from the [Makefile](../Makefile)

3. Wait a couple of minutes for the services to start up.
4. If some services are not starting up after 3 minutes, run them manually.

5. Due to specifics of local testing, some services need to be deleted and then restarted.

Using makefile
```bash
make restart_necessary
```

or Copypaste command `restart_necessary` from the [Makefile](../Makefile)

`dummy-issuer` service must be restarted AFTER the first run of tests.

1. Make the initial run of the tests following [instructions](#running-bdd-tests)
2. Restart the `dummy-issuer` service

```bash
make restart_issuer
```

or Copypaste command `restart_issuer` from the [Makefile](../Makefile)
3. Environment is now ready!


## Running BDD tests

### Prepare the environment
1. Using terminal `cd` into upper level root directory (bdd-executor)
2. if not present,  create virtual environment (venv) and activate it
```bash
python3 -m venv venv # if not present
source venv/bin/activate
```
3. Install the required dependencies
```bash
pip install -r requirements-dev.txt
pip install -r implementations/ocm-w/requirements.txt
```
4. cd into upper level src directory

### Run the BDD tests
```bash
behave ../implementations/ocm-w
```

## Making changes to the services

1. Each service is configured separately using ENV variables specified for each service in the `docker-compose.yml` file. Make sure services environment variables values are in synch.
2. All constants like services urls, ids, etc. are stored in this [file](../src/eu/xfsc/bdd/ocm_w/components/context.py). Make sure to update them if necessary.