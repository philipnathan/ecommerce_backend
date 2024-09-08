# Backend Application with Flask and Flask-Migrate

This README provides a comprehensive guide for setting up and running the backend application locally.

## Installation

1. Clone the repository
2. Create a `.env` file (please check .env.example on root directory)
3. Go to backend folder using terminal and install all dependencies

## Database Configuration

1. Open your MYSQL Workbench app
2. Create new database. Used `MYSQL_DATABASE` from .env file you've created as your database name

    ```sql
    CREATE DATABASE <MYSQL_DATABASE_ENV_NAME>;
    ```

## Flask Configuration

### If

1.  Go to backend folder and run this code on your terminal

    -   For windows user (This command will not return any response)

    ```
    set FLASK_APP=run.py
    ```

2.  On your terminal, run this command

        ```
        flask db upgrade
        ```

3.  Open MySQL Workbench and check if the table has been created successfully.

## How to run this API Services

1. Go to backend folder and run this code on your terminal to add all locations to locations' table

    ```
    python location_data_import.py
    ```

2. Run this on your terminal to start app

    ```
    python run.py
    ```
