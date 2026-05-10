


import pytest
from unittest.mock import MagicMock

from app.llm.sql_generator import generate_sql_from_english
from google.api_core import exceptions as google_exceptions
from app.core.exceptions import (
    InvalidSQLGeneratedException,
    LLMQuotaExceededException,
    LLMException,
)

@pytest.fixture
def mock_db():
    """
    Provides a mock database session for testing.
    """
    return MagicMock()



@pytest.fixture
def mock_schema(mocker):
    """
    Provides mock schema information for testing.
    """
    mocker.patch(
        "app.llm.sql_generator.get_schema_info",
        return_value=[]
    )
    mocker.patch(
        "app.llm.sql_generator.format_schema_for_prompt",
        return_value="customer(id: integer, name: varchar)"
    )



@pytest.fixture
def mock_gemini(mocker):
    """
    Patches the Gemini client so tests never make real API calls.
    Returns the mock so individual tests can control what Gemini 'returns'.
    """
    mock_response = MagicMock()
    mock_client = mocker.patch("app.llm.sql_generator.get_llm_client")
    mock_client.return_value.models.generate_content.return_value = mock_response
    return mock_response



class TestGenerateSQLFromEnglish:
    def test_valid_query_returns_sql(self, mock_db, mock_schema, mock_gemini):
        """
        Tests that a valid natural language query results in the expected SQL.
        """
        mock_gemini.text = "SELECT id, name FROM customer;"
        sql = generate_sql_from_english("Get all customers", mock_db)
        assert sql == "SELECT id, name FROM customer;"


    def test_markdown_wrapped_sql_is_cleaned(self, mock_db, mock_schema, mock_gemini):
        """
        Tests that SQL wrapped in markdown code blocks is correctly extracted.
        """
        mock_gemini.text = "```sql\nSELECT id, name FROM customer\n```"
        sql = generate_sql_from_english("Get all customers", mock_db)
        assert sql == "SELECT id, name FROM customer"


    def test_gemini_returns_invalid_raises_exception(self, mock_db, mock_schema, mock_gemini):
        """
        When Gemini can't answer, it returns 'INVALID'.
        We should raise InvalidSQLGeneratedException.
        """
        mock_gemini.text = "INVALID"

        with pytest.raises(InvalidSQLGeneratedException):
            generate_sql_from_english("delete everything", mock_db)


    def test_forbidden_keyword_raises_exception(self, mock_db, mock_schema, mock_gemini):
        """
        Even if the query starts with SELECT, forbidden keywords
        like DROP inside it should be rejected.
        """
        mock_gemini.text = "SELECT * FROM customer; DROP TABLE customer"

        with pytest.raises(InvalidSQLGeneratedException):
            generate_sql_from_english("show customers", mock_db)
   
    def test_non_select_raises_exception(self, mock_db, mock_schema, mock_gemini):
        """
        If the generated SQL doesn't start with SELECT, it's invalid.
        """
        mock_gemini.text = "UPDATE customer SET name='x'"

        with pytest.raises(InvalidSQLGeneratedException):
            generate_sql_from_english("update customer name", mock_db)

    def test_empty_response_raises_exception(self, mock_db, mock_schema, mock_gemini):
        """
        If Gemini returns empty string, we should raise InvalidSQLGeneratedException.
        """
        mock_gemini.text = ""

        with pytest.raises(InvalidSQLGeneratedException):
            generate_sql_from_english("show customers", mock_db)


    def test_quota_exceed_raises_exception(self, mock_db, mock_schema, mocker):
        """
        If Gemini raises a ResourceExhausted error, we should raise LLMQuotaExceededException.
        """
        
        mock_client = mocker.patch("app.llm.sql_generator.get_llm_client")
        mock_client.return_value.models.generate_content.side_effect = google_exceptions.ResourceExhausted("Quota exceeded")

        with pytest.raises(LLMQuotaExceededException):
            generate_sql_from_english("show customers", mock_db)

    def test_gemini_generic_failure_raises_llm_exception(self, mock_db, mock_schema, mocker):
        """
        Any unexpected Gemini error should raise LLMException.
        """

        mock_client = mocker.patch("app.llm.sql_generator.get_llm_client")
        mock_client.return_value.models.generate_content.side_effect = (
            Exception("something broke")
        )

        with pytest.raises(LLMException):
            generate_sql_from_english("show customers", mock_db)