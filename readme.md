# Trajectory Matching in Large-Scale Football Match Data

This project aims to [brief description of your project].

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

To run this project, you need:

- Python 3.x
- PostgreSQL database server

### Installation

1. Clone the repository:

```git clone https://github.com/username/project-name.git```

2. Change into the project directory:

```cd project-name/```


3. Create a directory named "data" in the root directory of the project:

```mkdir data/```

4. Place your event data files in the "data" directory.

5. Create a PostgreSQL database and configure the ".env" file based on your PostgreSQL configuration. Replace "username", "password", and "db_name" with your PostgreSQL credentials.
6. Install the project dependencies:
```pip install -r requirements.txt```

7. Run the SQL commands in the "queries.sql" file to create the necessary database tables.

### Data Insertion

1. Run the "data_insert.py" file to insert the event data into the database:
```python3 data_insert.py```

### Heuristic Search

1. Set up the targetPath variable in h_search.py file and run the file
```python3 h_search.py```