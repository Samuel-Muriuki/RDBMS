# RDBMS Presentation & Learning Guide

## What is a Relational Database Management System (RDBMS)?
A Relational Database Management System (RDBMS) is a software application designed to manage and manipulate relational databases. It organizes data into structured tables, enabling efficient storage, retrieval, and manipulation of data while ensuring data integrity through defined relationships.

### Core Concepts to Present

| Concept | Explanation |
|---------|-------------|
| **Tables (Relations)** | Data is stored in tables with named columns (attributes) and rows (records). |
| **SQL** | Structured Query Language is the standard way to interact with the database. |
| **Relationships** | Tables are connected using Primary and Foreign Keys. |
| **Data Integrity** | Enforces rules like referential integrity to maintain accuracy. |
| **ACID Compliance** | Atomicity, Consistency, Isolation, and Durability ensure reliable transactions. |

### Why RDBMS?
- **Business Applications**: Backbone of ERP and CRM systems.
- **Web Development**: Powers the backend of most web applications.
- **Data Warehousing**: Ideal for complex analytics and reporting.

### RDBMS Examples
- **MySQL**: Fast, open-source, widely used.
- **PostgreSQL**: Advanced, highly extensible.
- **SQLite**: Lightweight, serverless.
- **Oracle / SQL Server**: Powerful enterprise solutions.

## How to Demo This Project
1. **Show the Code**: Briefly explain the custom SQL Parser and Storage Engine.
2. **Execute Queries**: Use the SQL Console to demonstrate real SQL syntax working on your custom engine.
3. **Show Real-time Sync**: Open two browser windows and show how adding a task in one reflects in the other.
4. **Demonstrate Relational Power**: Perform an `INNER JOIN` in the console: `SELECT tasks.title, categories.name FROM tasks INNER JOIN categories ON tasks.category_id = categories.id;`
5. **Switch Themes**: Toggle light/dark mode and explain user-centric design.
