import pytest
from unittest.mock import MagicMock

from app.services.query_service import get_query_results
from app.core.exceptions import InvalidSQLGeneratedException, DatabaseQueryException


class TestQueryServices:

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    def test_query_services(self, mock_db, mocker):
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value="SELECT * FROM customer"
        )

        mocker.patch(
            "app.services.query_service._execute_sql",
            return_value=[{"id": 1, "name": "Akash"}]
        )

        results = get_query_results("Get all customers", mock_db)
        assert results == [{"id": 1, "name": "Akash"}]

    def test_empty_list_if_no_results(self, mock_db, mocker):
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value="SELECT * FROM customer WHERE id = -1"
        )

        mocker.patch(
            "app.services.query_service._execute_sql",
            return_value=[]
        )

        results = get_query_results("Get customer with id -1", mock_db)
        assert results == []


    def test_invalid_query_raises_exception(self, mock_db, mocker):
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            side_effect=InvalidSQLGeneratedException("Invalid query")
        )

        with pytest.raises(InvalidSQLGeneratedException):
            get_query_results("Give me all the data", mock_db)

    def test_sql_execution_failure_raises_exception(self, mock_db, mocker):
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value="SELECT * FROM customer"
        )

        mocker.patch(
            "app.services.query_service._execute_sql",
            side_effect=DatabaseQueryException("Database error")
        )

        with pytest.raises(DatabaseQueryException):
            get_query_results("Get all customers", mock_db)