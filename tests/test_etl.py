import unittest
from unittest.mock import patch, Mock
import sys
import os
import sqlite3

# add parent directory to sys.path to access the modules to test
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..',)))

from etl import route_events_to_sql
from sql_interface import delete


class TestRouter(unittest.TestCase):

    @patch("etl.sql_interface")
    def test_route_events(self, mock_sql_interface):

        # sample data
        events = [
            {'data_type':'organizations', 'action':'DELETE', 'data':'test_data', 'datetime':'2025-01-01T00:00:00.0299313Z'},
            {'data_type':'merchants', 'action':'UPDATE', 'data':'test_data', 'datetime':'2025-01-01T00:00:00.0299313Z'},
            {'data_type':'devices', 'action':'CREATE', 'data':'test_data', 'datetime':'2025-01-01T00:00:00.0299313Z'}
        ]

        # mock connection
        mock_connection = Mock(sqlite3.Connection)

        # call function to test
        route_events_to_sql(events, mock_connection)

        # here the assertions ensure correct methods were called
        mock_sql_interface.delete.assert_called_once_with(events[0], mock_connection)
        mock_sql_interface.update.assert_called_once_with(events[1], mock_connection)
        mock_sql_interface.load.assert_called_once_with(events[2], mock_connection)


class TestDeleteFunction(unittest.TestCase):

    @patch("sqlite3.Connection")
    def test_delete_success(self, MockConnection):

        # mock connection and cursor
        mock_conn = MockConnection.return_value
        mock_cursor = mock_conn.cursor.return_value
        
        # sample data
        event = {
            'data_type': 'merchants',
            'action':'DELETE',
            'data': {'id': 123},
            'datetime':'2025-01-01T00:00:00.0299313Z'
        }

        # call function to test
        delete(event, mock_conn)
        
        
        # here assertion ensures that the correct SQL query is executed
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM merchants WHERE id = '123'"
        )
        
        # here assertion ensures that commit was called on the connection to save changes
        mock_conn.commit.assert_called_once()

    @patch("sqlite3.Connection")
    def test_delete_sqlite_error(self, MockConnection):

        # mock connection and cursor
        mock_conn = MockConnection.return_value
        mock_cursor = mock_conn.cursor.return_value
        
        # Simulate a SQLite error
        mock_cursor.execute.side_effect = sqlite3.Error("forced SQL error!")
        
        # sample data
        event = {
            'data_type': 'devices',
            'action':'DELETE',
            'data': {'id': 456},
            'datetime':'2025-01-01T00:00:00.0299313Z'
        }
        
        # call function to test
        delete(event, mock_conn)
        
        # here the assertion ensures that `conn.commit` was not called if the query fails
        mock_conn.commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()