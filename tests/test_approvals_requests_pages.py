"""
Tests for the approvals_requests_pages module.

This module contains tests for the functions in the approvals_requests_pages module.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from dash import html

from pages.approvals_requests.approvals_requests_pages import (
    transform_columns_format,
    get_table_data,
    get_layout,
    open_modal_on_click
)


class TestTransformColumnsFormat(unittest.TestCase):
    """Tests for the transform_columns_format function."""

    def test_transform_columns_format_with_ignored_columns(self):
        """Test that ignored columns are excluded from the result."""
        columns = ['col1', 'col2', 'uuid_alteracoes', 'source_table', 'manual']
        result = transform_columns_format(columns)
        
        expected = [
            {'headerName': 'col1', 'field': 'col1'},
            {'headerName': 'col2', 'field': 'col2'}
        ]
        
        self.assertEqual(result, expected)
    
    def test_transform_columns_format_without_ignored_columns(self):
        """Test with columns that should all be included."""
        columns = ['col1', 'col2', 'col3']
        result = transform_columns_format(columns)
        
        expected = [
            {'headerName': 'col1', 'field': 'col1'},
            {'headerName': 'col2', 'field': 'col2'},
            {'headerName': 'col3', 'field': 'col3'}
        ]
        
        self.assertEqual(result, expected)
    
    def test_transform_columns_format_empty_list(self):
        """Test with an empty list of columns."""
        columns = []
        result = transform_columns_format(columns)
        self.assertEqual(result, [])


class TestGetTableData(unittest.TestCase):
    """Tests for the get_table_data function."""
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_user')
    def test_get_table_data_success(self, mock_get_requests):
        """Test successful retrieval and processing of data."""
        # Create a mock DataFrame to return
        mock_df = pd.DataFrame({
            'data_alteracoes': ['2025-06-26 14:30:00', '2025-06-25 10:15:00'],
            'status': [1, 3],
            'source_table': ['buildup', 'price'],
            'uuid_alteracoes': ['uuid1', 'uuid2']
        })
        mock_get_requests.return_value = mock_df
        
        # Call the function with mock user data
        result = get_table_data({'id': 'user123'})
        
        # Verify the function was called with the correct user ID
        mock_get_requests.assert_called_once_with('user123')
        
        # Check that the result has the expected format and transformations
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['status'], 'Aprovado')
        self.assertEqual(result[1]['status'], 'Pendente')
        self.assertEqual(result[0]['data_alteracoes_data'], '26/06/2025')
        self.assertEqual(result[0]['data_alteracoes_hora'], '14:30')
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_user')
    def test_get_table_data_no_user_id(self, mock_get_requests):
        """Test handling of missing user ID."""
        result = get_table_data({})
        
        # Function should return empty list and not call the API
        self.assertEqual(result, [])
        mock_get_requests.assert_not_called()
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_user')
    def test_get_table_data_api_exception(self, mock_get_requests):
        """Test handling of API exceptions."""
        mock_get_requests.side_effect = Exception("API error")
        
        result = get_table_data({'id': 'user123'})
        
        # Function should handle the exception and return empty list
        self.assertEqual(result, [])
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_user')
    def test_get_table_data_none_result(self, mock_get_requests):
        """Test handling of None result from API."""
        mock_get_requests.return_value = None
        
        result = get_table_data({'id': 'user123'})
        
        # Function should handle None result and return empty list
        self.assertEqual(result, [])


class TestOpenModalOnClick(unittest.TestCase):
    """Tests for the open_modal_on_click function."""
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_id')
    def test_open_modal_on_click_success(self, mock_get_details):
        """Test successful modal opening with details."""
        # Create a mock DataFrame to return
        mock_df = pd.DataFrame({
            'col1': ['value1', 'value2'],
            'col2': ['value3', 'value4']
        })
        mock_df.columns = ['col1', 'col2']
        mock_get_details.return_value = mock_df
        
        # Mock active cell and table data
        active_cell = {'column_id': 'detalhes', 'row': 0}
        table_data = [{'uuid_alteracoes': 'test-uuid'}]
        
        # Call the function
        is_open, content = open_modal_on_click(active_cell, table_data)
        
        # Verify the function was called with the correct request ID
        mock_get_details.assert_called_once_with('test-uuid')
        
        # Check that the modal should be open
        self.assertTrue(is_open)
        self.assertIsNotNone(content)
    
    def test_open_modal_on_click_no_active_cell(self):
        """Test handling of no active cell."""
        is_open, content = open_modal_on_click(None, [])
        
        # Modal should not open
        self.assertFalse(is_open)
        self.assertIsNone(content)
    
    def test_open_modal_on_click_invalid_row(self):
        """Test handling of invalid row index."""
        active_cell = {'column_id': 'detalhes', 'row': 5}
        table_data = [{'uuid_alteracoes': 'test-uuid'}]
        
        is_open, content = open_modal_on_click(active_cell, table_data)
        
        # Modal should not open
        self.assertFalse(is_open)
        self.assertIsNone(content)
    
    def test_open_modal_on_click_no_uuid(self):
        """Test handling of missing UUID in table data."""
        active_cell = {'column_id': 'detalhes', 'row': 0}
        table_data = [{'some_field': 'value'}]  # No uuid_alteracoes
        
        is_open, content = open_modal_on_click(active_cell, table_data)
        
        # Modal should not open
        self.assertFalse(is_open)
        self.assertIsNone(content)
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_id')
    def test_open_modal_on_click_wrong_column(self, mock_get_details):
        """Test handling of clicks on columns other than 'detalhes'."""
        active_cell = {'column_id': 'other_column', 'row': 0}
        table_data = [{'uuid_alteracoes': 'test-uuid'}]
        
        is_open, content = open_modal_on_click(active_cell, table_data)
        
        # Modal should not open and API should not be called
        self.assertFalse(is_open)
        self.assertIsNone(content)
        mock_get_details.assert_not_called()
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_id')
    def test_open_modal_on_click_empty_result(self, mock_get_details):
        """Test handling of empty result from API."""
        mock_get_details.return_value = None
        
        active_cell = {'column_id': 'detalhes', 'row': 0}
        table_data = [{'uuid_alteracoes': 'test-uuid'}]
        
        is_open, content = open_modal_on_click(active_cell, table_data)
        
        # Modal should open with error message
        self.assertTrue(is_open)
        self.assertIsNotNone(content)
    
    @patch('pages.approvals_requests.approvals_requests_pages.get_requests_for_approval_by_id')
    def test_open_modal_on_click_api_exception(self, mock_get_details):
        """Test handling of API exceptions."""
        mock_get_details.side_effect = Exception("API error")
        
        active_cell = {'column_id': 'detalhes', 'row': 0}
        table_data = [{'uuid_alteracoes': 'test-uuid'}]
        
        is_open, content = open_modal_on_click(active_cell, table_data)
        
        # Modal should open with error message
        self.assertTrue(is_open)
        self.assertIsNotNone(content)


if __name__ == '__main__':
    unittest.main()
