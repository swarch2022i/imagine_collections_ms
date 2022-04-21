# IMAGINE

## Microservice collection for Imagine application.

### How to run

``` bash
$docker build -t imagine_collection_ms .

$docker run --rm -d -p 8000:8000 -e NEO4J_PASSWORD=<password> -e NEO4J_BOLT_URL=<db_ip>:7687 imagine_collection_ms
```

**Julio Ernesto Quintero Peña.**  
_April, 2022_
