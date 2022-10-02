# Rental scraper and visualization for Stockholm housing

## Overview

Scraper collects information from various APIs and store them in a mongoDB database. Currently Blocket graphql and Google Transit API are used.

Utility libraries provided to access typed data from mongoDB and plot it on a map.

The code can be used standalone or though the `present.ipynb` Jupyter notebook.

### Scraping

The data collection and enrichment code can be found in the `scraper` folder

The scraper updated the provided database with new ads page by page until it reaches the first already stored ad and then stops.

Data is enriched with distance from a designated location. Distance information provided by the Google Transit API.

Unit test are provided using real world data obtained with browser dev tools. These files are not included in the repository since it may contain personal information.

Currently maps with distance or price information are available.

## Environment variables

```bash
MONGO_USER=<mongodb-user>
PSWD=<mongodb-password>
APIKEY=<google-transit-api-key>
ENDPOINT=<qasa-graphql-endpoint>
```

> You can set the `mongodb` credentials in the `docker-compose.yml` file