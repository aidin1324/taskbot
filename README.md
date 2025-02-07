# Taskbot Project

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.12
- [Poetry](https://python-poetry.org/docs/#installation)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/taskbot.git
    cd taskbot
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install
    ```

3. Set up environment variables:
    Create a `.env` file in the root directory and add your environment variables.

### Database Migration

1. Initialize the database using Alembic:
    ```sh
    alembic upgrade head
    ```

### Running the Project

1. Activate the virtual environment:
    ```sh
    poetry shell
    ```

2. Run the application:
    ```sh
    python main.py
    ```

### Additional Commands

- To create a new Alembic migration:
    ```sh
    alembic revision --autogenerate -m "Migration message"
    ```

- To apply migrations:
    ```sh
    alembic upgrade head
    ```

### Contributing

Feel free to submit issues and enhancement requests.

### License

Distributed under the MIT License. See `LICENSE` for more information.