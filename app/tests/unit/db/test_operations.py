from app.db.operations import get_schema_info, format_schema_for_prompt
from app.core.exceptions import SchemaFetchException
from app.db.operations import invalidate_schema_cache

from unittest.mock import MagicMock
import pytest
import pytest
from app.db import operations



@pytest.fixture(autouse=True)
def reset_schema_cache():
    """Reset schema cache before every test so tests don't interfere with each other."""
    operations._schema_cache = None
    operations._schema_cache_timestamp = 0.0
    yield
    operations._schema_cache = None
    operations._schema_cache_timestamp = 0.0




class TestFormatSchemaForPrompt:

    def test_groups_columns_by_table(self):
        """
        Tests that columns are correctly grouped by their respective tables in the formatted output.
        """
        schema_rows = [
            {"table_name": "customer", "column_name": "id", "data_type": "integer"},
            {"table_name": "customer", "column_name": "name", "data_type": "varchar"},
            {"table_name": "orders", "column_name": "order_id", "data_type": "integer"},
            {"table_name": "orders", "column_name": "amount", "data_type": "decimal"},
        ]
        formatted = format_schema_for_prompt(schema_rows)
        expected = (
            "customer(id: integer, name: varchar)\n"
            "orders(order_id: integer, amount: decimal)"
        )
        assert formatted == expected


    def test_empty_schema_returns_empty_string(self):
        """
        Tests that an empty list of schema rows results in an empty string output.
        """
        schema_rows = []
        formatted = format_schema_for_prompt(schema_rows)
        assert formatted == ""




class TestGetSchemaInfo:

    def test_return_list_of_dicts_on_success(self):
        """
        Tests that get_schema_info returns a list of dictionaries when the database query is successful.
        """

        ### Arrange
        mock_db = MagicMock()
        mock_db.execute.return_value.mappings().fetchall.return_value = [
            {"table_name": "customer", "column_name": "id", "data_type": "integer"},
            {"table_name": "customer", "column_name": "name", "data_type": "varchar"},
        ]


        ## Act
        result = get_schema_info(mock_db)

        ## Assert
        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)


    def test_return_empty_list_on_no_tables(self):
        """
        Tests that get_schema_info returns an empty list if there are no tables in the database.
        """
       
        ### arrange
        mock_db = MagicMock()
        mock_db.execute.return_value.mappings().fetchall.return_value = []

        ## act
        result = get_schema_info(mock_db)

        ## assert
        assert result == []

    def test_raise_exception_on_db_error(self):
        """
        Tests that get_schema_info raises a SchemaFetchException if the database query fails.
        """
        ## arrange
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("DB error")

        ## act + assert
        with pytest.raises(SchemaFetchException) as exc_info:
            get_schema_info(mock_db)



    def test_subsequent_calls_uses_caches(self):
        mock_db = MagicMock()
        mock_db.execute.return_value.mappings.return_value.fetchall.return_value = [
                {"table_name": "dell_customers", "column_name": "id", "data_type": "integer"},
            ]

        
        invalidate_schema_cache()

        get_schema_info(mock_db)
        get_schema_info(mock_db)

        mock_db.execute.assert_called_once()



class TestFormatSchemaForPrompt:

    def test_groups_columns_by_table(self):
        # ARRANGE
        schema_rows = [
            {"table_name": "dell_customers", "column_name": "id",   "data_type": "integer"},
            {"table_name": "dell_customers", "column_name": "name", "data_type": "varchar"},
            {"table_name": "dell_products",  "column_name": "id",   "data_type": "integer"},
        ]

        # ACT
        result = format_schema_for_prompt(schema_rows)

        # ASSERT
        assert "dell_customers(id: integer, name: varchar)" in result
        assert "dell_products(id: integer)" in result

    def test_each_table_on_its_own_line(self):
        # ARRANGE
        schema_rows = [
            {"table_name": "dell_customers", "column_name": "id", "data_type": "integer"},
            {"table_name": "dell_products",  "column_name": "id", "data_type": "integer"},
        ]

        # ACT
        result = format_schema_for_prompt(schema_rows)
        lines  = result.split("\n")

        # ASSERT
        assert len(lines) == 2

    def test_returns_empty_string_for_empty_input(self):
        # ACT
        result = format_schema_for_prompt([])

        # ASSERT
        assert result == ""

    def test_columns_in_correct_order(self):
        # ARRANGE — id should appear before name
        schema_rows = [
            {"table_name": "dell_customers", "column_name": "id",   "data_type": "integer"},
            {"table_name": "dell_customers", "column_name": "name", "data_type": "varchar"},
        ]

        # ACT
        result = format_schema_for_prompt(schema_rows)

        # ASSERT
        assert result.index("id") < result.index("name")



