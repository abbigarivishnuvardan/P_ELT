Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices


 ---------------------
 these code for postgres_project
version: '3'

services:

  source_postgres:
    image: postgres:15
    ports:
      - "5433:5432"
    networks:
      - elt_network
    environment:
      POSTGRES_DB: source_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 2002
    volumes:
      - ./source_db_init/init.sql:/docker-entrypoint-initdb.d/init.sql

  destination_postgres:
    image: postgres:15
    ports:
      - "5434:5432"
    networks:
      - elt_network
    depends_on:
      - source_postgres
    environment:
      POSTGRES_DB: destination_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 2002

  elt_script:
    build:
      context: ./elt
      dockerfile: Dockerfile
    command: ["python", "elt_script.py"]
    networks:
      - elt_network
    depends_on:
      - destination_postgres

  dbt:
    image: ghcr.io/dbt-labs/dbt-postgres:1.4.7
    command:
      [
        "run",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt",
        "--full-refresh"
      ]
    networks:
      - elt_network
    volumes:
      - ./custom_postgres:/dbt
      - ~/.dbt:/root
    depends_on:
      - elt_script
    environment:
      DBT_PROFILE: default
      DBT_TARGET: dev

networks:
  elt_network:
    driver: bridge
-------------------------------------------------


docker file 
FROM node:22-alpine
WORKDIR /app
COPY . .
RUN yarn install --production
CMD ["node", "./src/index.js"]
------------

to run air flow 
cd ELT 
docker compose up 
docker compose up init-airflow -d
docker compose up 
