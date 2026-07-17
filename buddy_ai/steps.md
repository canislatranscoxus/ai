# Steps for docker compose

Here we show the steps and commands to create the docker images,
run the containers,
run our crew ai agentic project,
and of course monitor and check the logs.



## start my containers

docker builder prune -f
docker compose up -d --build

--------------------------------------------------------------------------------

## how to run my containers ( and download my llm models too )

```
docker compose down
docker compose up --build
```


## View background logs:
If you ran the containers with -d, track what your agents are doing using

```
docker compose logs -f.
```

## Stop the application:
To gracefully shut down your agents and network components, press Ctrl + C (if running in the foreground) or type

```
docker compose down.
```

## Rebuild after changing code:
If you modify your CrewAI Python files, prompt configurations, or dependencies, force Docker to rebuild the image before restarting by typing

```
docker compose up --build
```

## how to run my crewai agents
```
docker compose start crewai
```

## Monitor the exeecution of my crew
```
docker compose logs -f crewai
```
--------------------------------------------------------------------------------