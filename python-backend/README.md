# Python Backend

This is the backend for the Florida Corporation Search Project. It uses `playwright` for scraping,`fastapi` for the RESTful API and `sqlalchemy` for communicating with the postgresql database.

## API Documentation

### Search

Used to start a crawl for the specified corporation

```http
POST /search/corporations
Content-Type: application/json

{
  "name": "string"
  "num_results": "int(optional)"
}
```

Response:

Success: 202 Accepted

```json
{
  "search_id": "string"
}
```

Error: 503 Service Unavailable

`search_id` is used to track the progress of the search using the `/results/{searh_id}` endpoint

### Results

Used to get the results of the seacrh

```http
GET /results/{search_id}
```

Response:

- Success: 200 OK

Returns the list of companies

- Success: 202 Accepted

Search is still in progress

- Error: 404 Not Found

Search ID Not Found

- Error: 500 Internal Server Error

There was an error while processing the search

```json
{
  "detail": "string" // Error Message
}
```
