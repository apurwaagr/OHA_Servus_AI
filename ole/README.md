## How to Build and Run

This project uses Docker Compose to automate the process of building the OpenTripPlanner graph and running the server.

### 1. Build the Graph

To build the routing graph from your data files, run the `otp_builder` service. This is a one-time process and can be resource-intensive.

```sh
docker compose --profile build up
```
### 1. Run the Planner

To build the routing graph from your data files, run the `otp_builder` service. This is a one-time process and can be resource-intensive.

```sh
docker compose --profile serve up -d
```
