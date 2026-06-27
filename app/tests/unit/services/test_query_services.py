import pytest
from unittest.mock import MagicMock
from app.services.query_service import get_query_results
from app.core.exceptions import (
    InvalidSQLGeneratedException,
    LLMQuotaExceededException,
    DatabaseQueryException,
)


class TestGetQueryResults:

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    def test_returns_sql_explanation_and_data_on_success(self, mock_db, mocker):
        # ARRANGE
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value=("SELECT * FROM dell_customers", "This query returns all customers.")
        )
        mocker.patch(
            "app.services.query_service._execute_sql",
            return_value=[{"id": 1, "name": "Rahul"}]
        )
        mocker.patch(
            "app.services.query_service.generate_insights",
            return_value="There is 1 customer in the database."
        )

        # ACT
        sql, explanation, data, insight = get_query_results("show all customers", mock_db)

        # ASSERT
        assert sql == "SELECT * FROM dell_customers"
        assert explanation == "This query returns all customers."
        assert data == [{"id": 1, "name": "Rahul"}]
        assert insight == "There is 1 customer in the database."

    def test_returns_empty_data_when_no_results(self, mock_db, mocker):
        # ARRANGE
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value=("SELECT * FROM dell_customers WHERE id = 999", "This query finds customer 999.")
        )
        mocker.patch(
            "app.services.query_service._execute_sql",
            return_value=[]
        )
        mocker.patch(
            "app.services.query_service.generate_insights",
            return_value="No data found for this query."
        )

        # ACT
        sql, explanation, data, insight = get_query_results("find customer 999", mock_db)

        # ASSERT
        assert data == []
        assert insight == "No data found for this query."

    def test_bubbles_up_invalid_sql_exception(self, mock_db, mocker):
        # ARRANGE
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            side_effect=InvalidSQLGeneratedException("bad sql")
        )

        # ACT + ASSERT
        with pytest.raises(InvalidSQLGeneratedException):
            get_query_results("do something weird", mock_db)

    def test_bubbles_up_quota_exception(self, mock_db, mocker):
        # ARRANGE
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            side_effect=LLMQuotaExceededException("quota hit")
        )

        # ACT + ASSERT
        with pytest.raises(LLMQuotaExceededException):
            get_query_results("show customers", mock_db)

    def test_bubbles_up_db_exception(self, mock_db, mocker):
        # ARRANGE
        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value=("SELECT * FROM dell_customers", "Returns all customers.")
        )
        mocker.patch(
            "app.services.query_service._execute_sql",
            side_effect=DatabaseQueryException("db error")
        )

        # ACT + ASSERT
        with pytest.raises(DatabaseQueryException):
            get_query_results("show customers", mock_db)

    def test_insight_receives_correct_results(self, mock_db, mocker):
        # ARRANGE — verify insights gets the DB results, not something else
        mock_results = [{"id": 1, "name": "Rahul"}, {"id": 2, "name": "Priya"}]

        mocker.patch(
            "app.services.query_service.generate_sql_from_english",
            return_value=("SELECT * FROM dell_customers", "Returns all customers.")
        )
        mocker.patch(
            "app.services.query_service._execute_sql",
            return_value=mock_results
        )
        mock_insights = mocker.patch(
            "app.services.query_service.generate_insights",
            return_value="2 customers found."
        )

        # ACT
        get_query_results("show customers", mock_db)

        # ASSERT — insights was called with the right arguments
        mock_insights.assert_called_once_with("show customers", mock_results)