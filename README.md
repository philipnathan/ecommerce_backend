# Backend for E-commerce

This project is a comprehensive end-to-end backend solution for an e-commerce platform, showcasing advanced integrations with third-party services such as RajaOngkir for real-time shipping, Meilisearch for fast and efficient product searches, and Midtrans for secure, multi-method payment processing.

## API Documentation

Full API documentation is available at [API Docs](http://13.250.107.176/apidocs/). The documentation is generated using Flasgger.

## Key Features

-   **User Authentication**: Secure user authentication utilizing JSON Web Tokens (JWT).
-   **User & Seller Management**: Complete management for both users and sellers.
-   **Real-Time Shipping Integration**: Successfully integrated with the **RajaOngkir API** to offer users real-time shipping options and cost calculations based on seller-to-user distances.
-   **Advanced Product Search**: Implemented **Meilisearch** to enable fast, accurate, and efficient product searches, enhancing the user experience.
-   **Comprehensive Payment Processing**: Seamless integration with **Midtrans** for handling multiple payment methods, with automatic notifications for transaction statuses (successful or failed). This setup supports diverse payment channels and ensures secure financial transactions.

## Technology Stack

-   **Backend**: Flask
-   **Databases**:
    -   **MySQL (Amazon RDS)**: Managed relational database service provided by AWS for storing structured data.
    -   **MongoDB**: for non-relational data, specifically used to store shopping carts.
-   **Third-Party Integrations**:
    -   **RajaOngkir**: API for real-time shipping options and cost calculations.
    -   **Meilisearch**: Search engine for fast and efficient product searches.
    -   **Midtrans**: Payment gateway for secure multi-method payment processing.

## Project Architecture

This project implements a layered architecture, inspired by clean architecture principles, with a clear separation of concerns:

### Layers:

1. **Controller Layer:**

    - Manages HTTP request handling and response formation
    - Passes request data and authentication information to the Service layer

2. **Service Layer:**

    - Implements core business logic and rules
    - Orchestrates the use of one or more repositories
    - Performs data transformations and complex operations

3. **Repository Layer:**
    - Manages direct interactions with the database
    - Impelements database operations (e.g., create, find, update, and, delete)

This architecture promotes:

-   Clear separation of responsibilities
-   Testability of individual components
-   Flexibility to change implementation details
-   Scalability for complex business logic

## Database Structure

Here's Entity Relationship Diagram ([ERD](https://drive.google.com/file/d/1ldPiQ7cMJ5hv38xJ_dnrZrNk9BPiYPUh/view?usp=sharing)) of our database structure - **(Please zoom in to see the image more clearly.)**

## Future Development Plans

-   **Dummy Data Creation**: After successful deployment, there will be plans to create dummy data to test all existing backend endpoints comprehensively.

## Acknowledgments

-   **RajaOngkir API**: For providing real-time shipping information.
-   **Meilisearch**: For its fast and efficient search capabilities.
-   **Midtrans**: For a reliable payment gateway solution.
