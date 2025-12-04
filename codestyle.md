# Backend Code Style Guide
This document outlines coding standards derived from established Python conventions and practices observed within the existing Flask/Database application.

# General Guidelines
## 1.1. Scope
+ Applies to all backend components, including Python, Flask, and database-related code.

## 1.2. Naming Conventions
+ Avoid ambiguous or unclear names.
+ Choose meaningful and descriptive identifiers.
+ Naming Standards
+ Modules/Files: snake_case
+ Functions/Methods (excluding FastAPI wrapper): camelCase
+ Functions/Methods (within FastAPI wrapper): snake_case
+ Variables: snake_case
+ Classes (Pydantic Models): PascalCase
+ Constants: UPPER_CASE_WITH_UNDERSCORES
+ Database Collections: snake_case (preferably plural form)

## 3.1. General Rules
+ Indentation: 4 spaces per level
+ Line Length: Limit to 79 characters where possible
+ Quotes: Prefer double quotes (") for string definitions

## 3.2. Import Organization
+ Arrange imports in separate lines, grouped as follows:
+ Standard library modules
+ Third-party packages
+ Local application-specific imports
+ Function and Endpoint Design
+ Decorators: Place FastAPI decorators directly above async def or def statements
+ Type Annotations: Include type hints for all parameters and return values
+ Input Handling: Utilize FastAPI/Pydantic constructs such as Header(None) and structured models for processing inputs

## 4.1. RESTful API Principles
+ Adhere to RESTful design patterns:
+ GET: Retrieve data
+ POST: Create new records
+ PUT: Update existing records
+ DELETE: Remove records

## 4.2. Core Implementation
+ Database Connectivity: Verify active database connections at the start of critical functions
+ Data Validation: Perform explicit checks for unique constraints and business rules prior to database operations
+ Access Control: Centralize authentication checks (e.g., token validation logic)

## 4.3. Exception Management

+ Standard Errors: Employ HTTPException to return appropriate HTTP status codes (e.g., 400, 401, 404, 500)
+ Error Containment: Enclose complex or failure-prone operations in try-except blocks, returning HTTP 500 responses for unhandled exceptions
+ Database Operations

## 5.1. General Practices
+ Object Identification: Convert string IDs from URLs using ObjectId() for document queries
+ Unique Identifiers: Centralize UID generation mechanisms (e.g., through dedicated utility functions)

## 5.2. Query Methods
+ Single Results: Apply find_one for individual document retrieval
+ Multiple Results: Use list(collection.find(...)) for querying multiple documents