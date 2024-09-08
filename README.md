# Backend for E-commerce

This project is a comprehensive end-to-end backend solution for an e-commerce platform, showcasing advanced integrations with third-party services such as RajaOngkir for real-time shipping, Meilisearch for fast and efficient product searches, and Midtrans for secure, multi-method payment processing.

## Key Features

-   **User Authentication**: Secure user authentication utilizing JSON Web Tokens (JWT).
-   **User & Seller Management**: Complete management for both users and sellers.
-   **Real-Time Shipping Integration**: Successfully integrated with the **RajaOngkir API** to offer users real-time shipping options and cost calculations based on seller-to-user distances.
-   **Advanced Product Search**: Implemented **Meilisearch** to enable fast, accurate, and efficient product searches, enhancing the user experience.
-   **Comprehensive Payment Processing**: Seamless integration with **Midtrans** for handling multiple payment methods, with automatic notifications for transaction statuses (successful or failed). This setup supports diverse payment channels and ensures secure financial transactions.

## Technology Stack

-   **Backend**: Flask
-   **Databases**:
    -   **MySQL** for relational data
    -   **MongoDB** for non-relational data
-   **Third-Party Integrations**:
    -   **RajaOngkir**: API for real-time shipping options and cost calculations.
    -   **Meilisearch**: Search engine for fast and efficient product searches.
    -   **Midtrans**: Payment gateway for secure multi-method payment processing.

## Project Architecture

This project uses and MVC-based architecture with a clear seperation between:

-   Controller: Manages endpoint logic
-   Service: Handle business logic
-   Repository: Manages database interactions

## Database Structure

Here's Entity Relationship Diagram ([ERD](https://drive.google.com/file/d/1ldPiQ7cMJ5hv38xJ_dnrZrNk9BPiYPUh/view?usp=sharing)) of our database structure - **(Please zoom in to see the image more clearly.)**

## API Documentation

Full API documentation is available at http://localhost/apidocs once the server is running. The documentation is generated using Flasgger.

## Project Limitations

-   The project currently uses local instances of MySQL and MongoDB, which prevents direct access by other users.
-   Users need to create accounts with third-party services such as Midtrans, RajaOngkir, and Meilisearch to utilize all features.

## Future Development Plans

-   **Deployment to AWS**: The project will be deployed to an AWS server to enable public access in the future.
-   **Dummy Data Creation**: After successful deployment, there will be plans to create dummy data to test all existing backend endpoints comprehensively.

## Additional Notes

-   Currently, there are no example data or predefined test scenarios provided
-   Users will need to create their own dummy data to test the application's functionalities
-   The project currently uses local instances of MySQL and MongoDB, which prevents direct access by other users.
-   Users need to create accounts with third-party services such as Midtrans, RajaOngkir, and Meilisearch to utilize all features.

## Project Set Up

To set up the project locally, follow these steps:

1. Duplicate the `.env.template` file and rename it to `.env`.
2. Fill in all the required environment variables in the `.env` file.
3. Open MySQL Workbench and create a new database as specified in the `MYSQL_DATABASE` environment variable.
4. Open MongoDB and create a new database, then set the `MONGO_URI` in the `.env` file.
5. Install all dependencies by running:

```bash
   pip install pipenv
   pipenv install
```

6. Set the Flask environment variable:

```bash
export FLASK_APP=run.py #for mac user
set FLASK_APP=run.py #for windows user
```

7. Run the following commands to perform database migrations:

```bash
flask db init
flask db migrate
flask db upgrade
```

8. Verify in MySQL Workbench that the tables have been created successfully.
9. Run:

```bash
python import_category.py
python import_province.py
```

10. Start the backend application by running

```bash
python run.py
```

## Acknowledgments

-   **RajaOngkir API**: For providing real-time shipping information.
-   **Meilisearch**: For its fast and efficient search capabilities.
-   **Midtrans**: For a reliable payment gateway solution.
