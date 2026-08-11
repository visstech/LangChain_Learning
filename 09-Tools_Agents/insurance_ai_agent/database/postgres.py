"""
PostgreSQL database connection module.

This module provides a reusable PostgreSQL connection class
for the Insurance AI Agent application.
"""

import psycopg2


class PostgreSQL:
    """
    Manages connections to the PostgreSQL database.
    """

    def __init__(
        self,
        host="localhost",
        port=5432,
        database="insurance_ai",
        user="postgres",
        password="postgres123"
    ):
        """
        Initialize PostgreSQL connection settings.

        Args:
            host: PostgreSQL server hostname.
            port: PostgreSQL server port.
            database: Database name.
            user: PostgreSQL username.
            password: PostgreSQL password.
        """

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        self.connection = None

    def connect(self):
        """
        Establish a connection to PostgreSQL.

        Returns:
            The active PostgreSQL connection.
        """

        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

        print("PostgreSQL connected successfully.")

        return self.connection

    def close(self):
        """
        Close the PostgreSQL connection if it is open.
        """

        if self.connection:

            self.connection.close()

            print("PostgreSQL connection closed.")