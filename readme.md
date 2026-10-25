# Music Video Optimization & Performance Syndicate System

## Project Overview

An automated, local data engine designed to ingest, normalize, and analyze high-volume streaming performance metrics across fragmented distribution landscapes. This system processes raw platform transaction logs to track audience engagement behavior and evaluate syndication pipeline efficiency.

## Core Technical Stack

* **Data Architecture:** Relational DB Modeling, Snowflake/Star Schema Design, Constraint Enforcement
* **Languages:** Python (Pandas, Sqlite3 Engine drivers), ANSI SQL  
* **Tools Used:** VS Code Workspace, Database Layout Mapping

## Engineering Highlights & Execution

1. **Relational Database Design:** Engineered a multi-table database blueprint modeling Artist, Video, Platform, and Fact-Metric relationships with absolute structural integrity.
2. **Automated ETL Pipeline:** Developed an object-oriented Python script to ingest real-world high-density datasets (2,500+ records), drop rows with numeric parsing anomalies, and populate tracking targets cleanly.
3. **Multi-Table Relational Queries:** Authored production-grade SQL optimization scripts leveraging multi-dimensional aggregations (`JOIN`, `GROUP BY`, composite tracking calculations) to isolate performance trends.
![System Database Layout Blueprint](erd_blueprint.png)
