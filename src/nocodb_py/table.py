"""
Filename: src/nocodb_py/table.py

NocoDB Table for Python
"""

# pylint: disable=unused-import
# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=too-many-public-methods
# pylint: disable=line-too-long
# pylint: disable=import-outside-toplevel

import time
import threading
import copy
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from typing import TYPE_CHECKING
import requests
from .utils import parse_utc_datetime, count_of_nocodb_data
from .client import NocoDBClient
from .project import NocoDBProject
from .record import NocoDBRecord, NocoDBRecordSet
if TYPE_CHECKING:
    from .column import NocoDBColumn, NocoDBSchema

class RecordNotFoundError(Exception):
    """Exception raised when a record is not found in the table."""
    
    def __init__(self, table_id: str, record_id: int, original_error: Exception):
        self.table_id = table_id
        self.record_id = record_id
        self.original_error = original_error
        super().__init__(f"Record with ID {record_id} not found in table {table_id}")

# pylint: disable=too-many-instance-attributes
class NocoDBTable:
    """
    A class representing a NocoDB table with table-specific operations
    
    Attributes:
        _project (NocoDBProject): The NocoDB project instance
        _table_id (str): The unique table identifier
    """

    def __init__(self, project: NocoDBProject, table_id: str, timeout: int = 30, cache_ttl: Optional[int] = 300):
        """
        Initialize the NocoDBTable with project and table ID
        
        Args:
            project (NocoDBProject): The NocoDB project instance
            table_id (str): The unique table identifier
            timeout (int): Request timeout in seconds
            cache_ttl (Optional[int]): Cache time-to-live in seconds
        """
        self._project = project
        self._table_id = table_id
        self._timeout = timeout
        self._cache_ttl = cache_ttl

        # Table-specific cache
        self._table_info_cache = None
        self._table_info_timestamp = 0
        self._columns_cache = None
        self._columns_timestamp = 0
        self._schema_cache = None
        self._schema_timestamp = 0
        self._cache_lock = threading.RLock()

    def __str__(self) -> str:
        """
        String representation of the NocoDBTable
        
        Returns:
            str: String representation of the table
        """
        return f"NocoDBTable(id='{self._table_id}', project={self._project})"

    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBTable
        
        Returns:
            str: Official representation of the table
        """
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another NocoDBTable
        
        Args:
            other (object): The other object to compare with
            
        Returns:
            bool: True if equal, False otherwise
        """
        if not isinstance(other, NocoDBTable):
            return False
        return self._table_id == other._table_id and self._project == other._project

    @property
    def table_id(self) -> str:
        """Get the table ID"""
        return self._table_id

    @property
    def project(self) -> NocoDBProject:
        """Get the project instance"""
        return self._project

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBTable.
        
        Returns:
            int: Hash value based on immutable attributes that define identity
        """
        return hash((self._project, self._table_id))

    def __copy__(self):
        """
        Shallow copy implementation for NocoDBTable.
        
        Returns:
            NocoDBTable: A new table instance with same configuration but fresh cache
        """
        new_table = NocoDBTable(self._project, self._table_id,
                              self._timeout, self._cache_ttl)
        # Reset cache state
        new_table._table_info_cache = None
        new_table._table_info_timestamp = 0
        new_table._columns_cache = None
        new_table._columns_timestamp = 0
        return new_table

    def __deepcopy__(self, memo):
        """
        Deep copy implementation for NocoDBTable.
        
        Args:
            memo: Memo dictionary for deepcopy
            
        Returns:
            NocoDBTable: A new table instance with same configuration but fresh cache
        """
        # For NocoDBTable, deepcopy is the same as shallow copy
        # since we don't want to copy cache state and project is shared
        return self.__copy__()

    def __getstate__(self):
        """
        Get state for pickling.
        
        Returns:
            dict: State dictionary without non-serializable objects
        """
        state = self.__dict__.copy()
        # Remove non-serializable objects
        state.pop('_cache_lock', None)
        state.pop('_table_info_cache', None)
        state.pop('_table_info_timestamp', None)
        state.pop('_columns_cache', None)
        state.pop('_columns_timestamp', None)
        return state

    def __setstate__(self, state):
        """
        Set state from pickling.
        
        Args:
            state: State dictionary
        """
        self.__dict__.update(state)
        # Reinitialize non-serializable objects
        self._cache_lock = threading.RLock()
        self._table_info_cache = None
        self._table_info_timestamp = 0
        self._columns_cache = None
        self._columns_timestamp = 0

    def get_table_id(self) -> str:
        """
        Get the table ID (compatibility method)
        
        Returns:
            str: The table ID
        """
        return self.table_id
    
    get_id = get_table_id

    def get_project(self) -> NocoDBProject:
        """
        Get the project instance (compatibility method)
        
        Returns:
            NocoDBProject: The project instance
        """
        return self.project

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix
        
        Returns:
            str: The meta v2 prefix
        """
        return f"/api/v2/meta/tables/{self._table_id}"

    def get_data_v2_prefix(self) -> str:
        """
        Get the data v2 prefix
        
        Returns:
            str: The data v2 prefix
        """
        return f"/api/v2/tables/{self._table_id}"


    def get_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get the full info for the table
        
        Args:
            force_refresh (bool): Whether to force a refresh of the table info
            
        Returns:
            Dict: The full table info
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
               self._table_info_cache is not None and
               (cache_ttl is None or current_time - self._table_info_timestamp < cache_ttl)
               ):
                return self._table_info_cache

            # pylint: disable=protected-access
            # Reason: NocoDBClient._get is intentionally accessible to NocoDB-related classes
            self._table_info_cache = self._project.client._get(
                f"{self.get_meta_v2_prefix()}"
            )
            self._table_info_timestamp = current_time
            return self._table_info_cache

    def get_title(self, force_refresh: bool = False) -> str:
        """
        Get the title of the table
        
        Args:
            force_refresh (bool): Whether to force refresh the cache
            
        Returns:
            str: The title of the table
            
        Raises:
            ValueError: When title is not found in table info
        """
        table_info = self.get_full_info(force_refresh=force_refresh)
        title = table_info.get("title")
        if title is None:
            raise ValueError("Title not found in table info")
        return title

    def get_description(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get the description of the table
        
        Args:
            force_refresh (bool): Whether to force refresh the cache
            
        Returns:
            Optional[str]: The description of the table, or None if not set
        """
        table_info = self.get_full_info(force_refresh=force_refresh)
        return table_info.get("description")

    def get_columns_full_info(self, force_refresh: bool = False) -> List:
        """
        Get the full column info for the table
        
        Args:
            force_refresh (bool): Force refresh the cache
            
        Returns:
            Dict: The full column info
        """
        full_info = self.get_full_info(force_refresh=force_refresh)
        return full_info.get("columns", [])

    def list_columns(self, force_refresh: bool = False,
                    full_info: bool = False, convert_time: bool = False) -> List:
        """
        List the column names for the table
        
        Args:
            force_refresh (bool): Force refresh the cache
            
        Returns:
            List[str]: The column names
        """
        columns_data = self.get_columns_full_info(force_refresh=force_refresh)
        columns_list = columns_data

        if convert_time:
            columns_list = [
                {
                    **col,
                    'created_at': parse_utc_datetime(col.get('created_at', None)),
                    'updated_at': parse_utc_datetime(col.get('updated_at', None)),
                }
                for col in columns_list
            ]

        if not full_info:
            columns_list = [
                {
                    "id": col.get("id", ""),
                    "title": col.get("title", ""),
                    "uidt": col.get("uidt", ""),
                }
                for col in columns_list
            ]
        return columns_list

    def find_columns_by_title(self, title: str, match_func: Optional[Callable[[str, str], bool]] = None, force_refresh: bool = False) -> List[str]:
        """
        Find list of matching column_ids by title

        Args:
            title (str): The title string to search for
            match_func (Callable): Matching function, accepts two string arguments and returns bool, defaults to exact match
            force_refresh (bool): Whether to force refresh the cache

        Returns:
            List[str]: List of matching column_ids
        """
        # pylint: disable=import-outside-toplevel
        from .utils import exact_match  # Avoid circular import

        if match_func is None:
            match_func = exact_match

        columns: Optional[List[Dict[str, Any]]] = self.list_columns(force_refresh=force_refresh, full_info=False)
        if columns is None:
            return []

        return [
            column["id"] for column in columns
            if match_func(title, column.get("title", ""))
        ]

    def count_columns(self) -> int:
        """Count columns in a table."""
        column_info = self.get_columns_full_info()
        column_list = column_info
        if isinstance(column_list, List):
            return len(column_list)
        return 0

    def get_column(self, column_id: str) -> 'NocoDBColumn':
        """
        Get a column object by column ID
        
        Args:
            column_id (str): The column ID to get
            
        Returns:
            NocoDBColumn: The column object
            
        Note:
            This method does not validate if the column exists and does not use cache.
            It directly creates a NocoDBColumn instance with the provided column ID.
        """
        from .column import NocoDBColumn
        return NocoDBColumn(
            table=self,
            column_id=column_id,
            timeout=self._timeout,
            cache_ttl=self._cache_ttl
        )

    def clear_table_info_cache(self):
        """
        Clear table info cache
        """
        with self._cache_lock:
            self._table_info_cache = None
            self._table_info_timestamp = 0

    def clear_columns_cache(self):
        """
        Clear columns cache
        """
        with self._cache_lock:
            self._columns_cache = None
            self._columns_timestamp = 0
    
    def get_schema(self, force_refresh: bool = False) -> 'NocoDBSchema':
        """
        Get the table schema
        
        Args:
            force_refresh (bool): Whether to force a refresh of the schema cache
            
        Returns:
            NocoDBSchema: The table schema instance
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
               self._schema_cache is not None and
               (cache_ttl is None or current_time - self._schema_timestamp < cache_ttl)
               ):
                return self._schema_cache

            from .column import NocoDBSchema
            schema = NocoDBSchema(self)
            schema.load_schema(force_refresh)
            self._schema_cache = schema
            self._schema_timestamp = current_time
            return schema
    
    def clear_schema_cache(self):
        """
        Clear schema cache
        """
        with self._cache_lock:
            self._schema_cache = None
            self._schema_timestamp = 0

    def list_records(self) -> NocoDBRecordSet:
        """
        List all records from the table.
        
        Returns:
            NocoDBRecordSet: A set of NocoDBRecord objects.
        """
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._get is intentionally accessible to NocoDB-related classes
        response = self._project.client._get(path)
        records_data = response.get("list", [])
        
        # Convert to NocoDBRecord objects
        records = []
        for record_data in records_data:
            record = NocoDBRecord.from_api_format(record_data, table=self)
            records.append(record)
            
        return NocoDBRecordSet(records, table=self)
    
    get_records = list_records
    
    def count_records(self) -> int:
        """
        Count the number of records in the table.
        
        Returns:
            int: The number of records in the table.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response format is invalid.
            
        Example:
            >>> table.count_records()
            42
            
        Note:
            API response format: {"count": 1}
        """
        path = f"{self.get_data_v2_prefix()}/records/count"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._get is intentionally accessible to NocoDB-related classes
        response = self._project.client._get(path)
        
        # Validate response format
        if not isinstance(response, dict):
            raise ValueError(f"Invalid API response format: expected dict, got {type(response)}")
            
        count = response.get("count")
        if count is None:
            raise ValueError("Missing 'count' field in API response")
            
        if not isinstance(count, (int, float)):
            raise ValueError(f"Invalid count type: expected number, got {type(count)}")
            
        return int(count)

    def get_record(self, record_id:int) -> Optional[NocoDBRecord]:
        """
        Get a single record from the table by its ID.
        
        Args:
            record_id (int): The record ID to retrieve
            
        Returns:
            Optional[NocoDBRecord]: The record as a NocoDBRecord object if found
            
        Raises:
            RecordNotFoundError: If the record with the specified ID does not exist
            requests.exceptions.HTTPError: For other HTTP errors (e.g., 500 Internal Server Error)
            
        Example:
            >>> record = table.get_record(123)
            >>> print(record)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'title': 'Sample Record', 'created_at': '2023-01-01T00:00:00Z'})
        """
        try:
            path = f"{self.get_data_v2_prefix()}/records/{record_id}"
            # pylint: disable=protected-access
            # Reason: NocoDBClient._get is intentionally accessible to NocoDB-related classes
            response = self._project.client._get(path)
            return NocoDBRecord.from_api_format(response, table=self)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise RecordNotFoundError(self._table_id, record_id, e) from e
            raise

    def _validate_column_names(self, record: Dict) -> None:
        """
        Validate that all keys in the record exist as column titles in the table.
        
        Args:
            record (Dict): The record to validate
            
        Raises:
            ValueError: If any key in the record is not a valid column title
        """
        # Get column information for validation
        columns_info = self.get_columns_full_info()
        column_titles = [col.get('title', '') for col in columns_info]
        
        invalid_columns = []
        for key in record.keys():
            if key not in column_titles:
                invalid_columns.append(key)
        
        if invalid_columns:
            raise ValueError(f"Invalid column names: {invalid_columns}. Valid columns are: {column_titles}")

    def _filter_read_only_columns(self, record: Dict) -> Dict:
        """
        Filter out read-only columns from the record.
        
        Args:
            record (Dict): The record to filter
            
        Returns:
            Dict: The filtered record with only writable columns
        """
        # Get column information for filtering
        columns_info = self.get_columns_full_info()
        
        # Get column titles that are read-only
        read_only_titles = []
        for col in columns_info:
            # Check if column is system column (system=1) or readonly (readonly=1)
            if col.get('system') == 1 or col.get('readonly') == 1:
                read_only_titles.append(col.get('title', ''))
        
        # Filter out read-only columns
        filtered_record = {}
        for key, value in record.items():
            if key not in read_only_titles:
                filtered_record[key] = value
        
        return filtered_record

    def _process_record_for_creation(self, record: Union[Dict, NocoDBRecord]) -> Dict:
        """
        Process a single record for creation, including validation and filtering.
        
        Args:
            record (Union[Dict, NocoDBRecord]): Record to process
            
        Returns:
            Dict: Processed record data ready for API
        """
        if isinstance(record, NocoDBRecord):
            # Use record's data
            record_data = record.to_api_format()
            # Remove ID if present (should not be present for new records)
            if "Id" in record_data:
                del record_data["Id"]
        else:
            record_data = record
            
        # Validate column names
        self._validate_column_names(record_data)
        
        # Filter out read-only columns
        return self._filter_read_only_columns(record_data)
    
    def _process_record_for_update(self, record: Union[Dict, NocoDBRecord]) -> Tuple[Dict, int]:
        """
        Process a single record for update, including validation and filtering.
        
        Args:
            record (Union[Dict, NocoDBRecord]): Record to process
            
        Returns:
            Tuple[Dict, int]: Processed record data and record ID
        """
        if isinstance(record, NocoDBRecord):
            # Use record's data and ensure it has an ID
            record_data = record.to_api_format()
            if "Id" not in record_data:
                raise ValueError("NocoDBRecord must be attached (have an ID) to be updated")
        else:
            record_data = record
            
        # Check if record has "Id" field
        if "Id" not in record_data:
            raise ValueError("Record must contain an 'Id' field to identify which record to update")
        
        # Get record ID and ensure it's an integer
        record_id = record_data.get("Id")
        if record_id is None:
            raise ValueError("Record ID is required for update")
        try:
            record_id_int = int(record_id)
        except (TypeError, ValueError):
            raise ValueError(f"Record ID must be an integer, got {type(record_id)}")
        
        # Validate column names (excluding "Id" which is required for update)
        record_without_id = {k: v for k, v in record_data.items() if k != "Id"}
        self._validate_column_names(record_without_id)
        
        # Filter out read-only columns (but keep "Id" for identification)
        filtered_record = self._filter_read_only_columns(record_data)
        
        # Ensure "Id" is preserved even if it's a read-only column
        if "Id" in record_data and "Id" not in filtered_record:
            filtered_record["Id"] = record_data["Id"]
        
        return filtered_record, record_id_int
    
    def _process_record_for_deletion(self, record: Union[Dict, NocoDBRecord]) -> Dict:
        """
        Process a single record for deletion, extracting the record ID.
        
        Args:
            record (Union[Dict, NocoDBRecord]): Record to process
            
        Returns:
            Dict: Record data with ID for deletion
        """
        if isinstance(record, NocoDBRecord):
            # Use record's ID
            if not record.is_attached:
                raise ValueError("NocoDBRecord must be attached (have an ID) to be deleted")
            return {"Id": record.record_id}
        else:
            # Check if record has "Id" field
            if "Id" not in record:
                raise ValueError("Record must contain an 'Id' field to identify which record to delete")
            return {"Id": record["Id"]}
    
    def create_record(self, record: Union[Dict, NocoDBRecord]) -> NocoDBRecord:
        """
        Create a single record in the table.
        
        Args:
            record (Union[Dict, NocoDBRecord]): Record to create. Can be dictionary or NocoDBRecord object.
            
        Returns:
            NocoDBRecord: Created record as NocoDBRecord object
            
        Raises:
            ValueError: If column names in record are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Example:
            >>> # Create record from dictionary
            >>> result = table.create_record({"Name": "John", "Age": 30})
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John', 'Age': 30})
            
            >>> # Create record from NocoDBRecord
            >>> record = NocoDBRecord({"Name": "John", "Age": 30})
            >>> result = table.create_record(record)
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John', 'Age': 30})
        """
        filtered_record = self._process_record_for_creation(record)
        
        # Send POST request
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._post is intentionally accessible to NocoDB-related classes
        response = self._project.client._post(path, data=filtered_record)
        
        # Create and return NocoDBRecord object
        record_id = response.get("Id")
        if record_id is None:
            raise ValueError("API response does not contain record ID")
            
        if isinstance(record, NocoDBRecord):
            # Attach the existing record to the table
            record._attach(self, record_id)
            return record
        else:
            # Create new record object
            return NocoDBRecord.from_api_format(response, table=self)
    
    def _create_records_batch(self, records: List[Union[Dict, NocoDBRecord]]) -> List[NocoDBRecord]:
        """
        Create multiple records in the table (internal batch method).
        
        Args:
            records (List[Union[Dict, NocoDBRecord]]): List of records to create. Can be dictionaries or NocoDBRecord objects.
            
        Returns:
            List[NocoDBRecord]: Created records as NocoDBRecord objects
            
        Raises:
            ValueError: If column names in records are invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Process each record
        filtered_records = []
        original_records = []  # Keep track of original NocoDBRecord objects
        for record in records:
            if isinstance(record, NocoDBRecord):
                original_records.append(record)
            else:
                original_records.append(None)
            filtered_records.append(self._process_record_for_creation(record))
        
        # Send POST request with batch data
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._post is intentionally accessible to NocoDB-related classes
        response = self._project.client._post(path, data=filtered_records)
        
        # Create and return NocoDBRecord objects
        result_records = []
        for i, record_response in enumerate(response):
            record_id = record_response.get("Id")
            if record_id is None:
                raise ValueError("API response does not contain record ID")
                
            if original_records[i] is not None:
                # Attach the existing record to the table
                original_records[i].attach(self, record_id)
                result_records.append(original_records[i])
            else:
                # Create new record object
                result_records.append(NocoDBRecord.from_api_format(record_response, table=self))
        
        return result_records
    
    def update_record(self, record: Union[Dict, NocoDBRecord]) -> NocoDBRecord:
        """
        Update a single record in the table.
        
        Args:
            record (Union[Dict, NocoDBRecord]): Record to update. Can be dictionary or NocoDBRecord object.
                The record must contain an "Id" field to identify which record to update.
            
        Returns:
            NocoDBRecord: Updated record as NocoDBRecord object
            
        Raises:
            ValueError: If column names in record are invalid or if "Id" field is missing
            requests.exceptions.RequestException: If the API request fails
            
        Example:
            >>> # Update record from dictionary
            >>> result = table.update_record({"Id": 123, "Name": "John Updated", "Age": 31})
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John Updated', 'Age': 31})
            
            >>> # Update record from NocoDBRecord
            >>> record = table.get_record(123)
            >>> record["Name"] = "John Updated"
            >>> result = table.update_record(record)
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John Updated', 'Age': 31})
        """
        filtered_record, record_id = self._process_record_for_update(record)
        
        # Send PATCH request
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._patch is intentionally accessible to NocoDB-related classes
        response = self._project.client._patch(path, data=filtered_record)
        
        # Return the updated NocoDBRecord object
        if isinstance(record, NocoDBRecord):
            # Update the existing record's data
            record._data = {k: v for k, v in filtered_record.items() if k != "Id"}
            return record
        else:
            # Create new record object with updated data
            return NocoDBRecord.from_api_format(response, table=self)
    
    def _update_records_batch(self, records: List[Union[Dict, NocoDBRecord]]) -> List[NocoDBRecord]:
        """
        Update multiple records in the table (internal batch method).
        
        Args:
            records (List[Union[Dict, NocoDBRecord]]): List of records to update. Can be dictionaries or NocoDBRecord objects.
                Each record must contain an "Id" field to identify which record to update.
            
        Returns:
            List[NocoDBRecord]: Updated records as NocoDBRecord objects
            
        Raises:
            ValueError: If column names in records are invalid or if "Id" field is missing
            requests.exceptions.RequestException: If the API request fails
        """
        # Process each record
        filtered_records = []
        original_records = []  # Keep track of original NocoDBRecord objects
        
        for record in records:
            if isinstance(record, NocoDBRecord):
                original_records.append(record)
            else:
                original_records.append(None)
                
            filtered_record, _ = self._process_record_for_update(record)
            filtered_records.append(filtered_record)
        
        # Send PATCH request with batch data
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._patch is intentionally accessible to NocoDB-related classes
        response = self._project.client._patch(path, data=filtered_records)
        
        # Return the updated NocoDBRecord objects
        result_records = []
        for i, record_response in enumerate(response):
            if original_records[i] is not None:
                # Update the existing record's data
                original_records[i]._data = {k: v for k, v in filtered_records[i].items() if k != "Id"}
                result_records.append(original_records[i])
            else:
                # Create new record object with updated data
                result_records.append(NocoDBRecord.from_api_format(record_response, table=self))
        
        return result_records
    
    def delete_record(self, record: Union[Dict, NocoDBRecord]) -> Dict:
        """
        Delete a single record from the table.
        
        Args:
            record (Union[Dict, NocoDBRecord]): Record to delete. Can be dictionary or NocoDBRecord object.
                The record must contain an "Id" field to identify which record to delete.
            
        Returns:
            Dict: Deletion result (API response)
            
        Raises:
            ValueError: If "Id" field is missing in record
            requests.exceptions.RequestException: If the API request fails
            
        Example:
            >>> # Delete record from dictionary
            >>> result = table.delete_record({"Id": 123})
            >>> print(result)
            {"Id": 123}
            
            >>> # Delete record from NocoDBRecord
            >>> record = table.get_record(123)
            >>> result = table.delete_record(record)
            >>> print(result)
            {"Id": 123}
        """
        validated_record = self._process_record_for_deletion(record)
        
        # Send DELETE request
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._delete is intentionally accessible to NocoDB-related classes
        response = self._project.client._delete(path, data=validated_record)
        
        # Mark the record as deleted
        if isinstance(record, NocoDBRecord):
            record._mark_deleted()
        
        # Return the deletion result
        return response
    
    def _delete_records_batch(self, records: List[Union[Dict, NocoDBRecord]]) -> List[Dict]:
        """
        Delete multiple records from the table (internal batch method).
        
        Args:
            records (List[Union[Dict, NocoDBRecord]]): List of records to delete. Can be dictionaries or NocoDBRecord objects.
                Each record must contain an "Id" field to identify which record to delete.
            
        Returns:
            List[Dict]: Deletion results (API responses)
            
        Raises:
            ValueError: If "Id" field is missing in records
            requests.exceptions.RequestException: If the API request fails
        """
        # Process each record
        validated_records = []
        for record in records:
            validated_record = self._process_record_for_deletion(record)
            validated_records.append(validated_record)
        
        # Send DELETE request with batch data
        path = f"{self.get_data_v2_prefix()}/records"
        # pylint: disable=protected-access
        # Reason: NocoDBClient._delete is intentionally accessible to NocoDB-related classes
        response = self._project.client._delete(path, data=validated_records)
        
        # Mark all NocoDBRecord objects as deleted
        for record in records:
            if isinstance(record, NocoDBRecord):
                record._mark_deleted()
        
        # Return the list of deletion results
        return response
    
    # Backward compatibility methods - these wrap the new separated methods
    def create_records(self, records: Union[Dict, NocoDBRecord, List[Dict], List[NocoDBRecord]]) -> Union[NocoDBRecord, List[NocoDBRecord]]:
        """
        Create one or more records in the table (backward compatibility wrapper).
        
        This method wraps the new create_record and create_records methods for backward compatibility.
        
        Args:
            records (Union[Dict, NocoDBRecord, List[Dict], List[NocoDBRecord]]):
                Single record or list of records to create. Can be dictionaries or NocoDBRecord objects.
            
        Returns:
            Union[NocoDBRecord, List[NocoDBRecord]]: Created record(s) as NocoDBRecord objects
            
        Raises:
            ValueError: If column names in records are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Example:
            >>> # Create single record from dictionary
            >>> result = table.create_records({"Name": "John", "Age": 30})
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John', 'Age': 30})
            
            >>> # Create single record from NocoDBRecord
            >>> record = NocoDBRecord({"Name": "John", "Age": 30})
            >>> result = table.create_records(record)
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John', 'Age': 30})
            
            >>> # Create multiple records
            >>> result = table.create_records([
            ...     {"Name": "John", "Age": 30},
            ...     {"Name": "Jane", "Age": 25}
            ... ])
            >>> print(result)
            [NocoDBRecord(record_id=123, ...), NocoDBRecord(record_id=124, ...)]
        """
        if isinstance(records, list):
            # Type assertion: List[Dict] | List[NocoDBRecord] is compatible with List[Dict | NocoDBRecord]
            return self._create_records_batch(records)  # type: ignore
        else:
            return self.create_record(records)
    
    def update_records(self, records: Union[Dict, NocoDBRecord, List[Dict], List[NocoDBRecord]]) -> Union[NocoDBRecord, List[NocoDBRecord]]:
        """
        Update one or more records in the table (backward compatibility wrapper).
        
        This method wraps the new update_record and _update_records_batch methods for backward compatibility.
        
        Args:
            records (Union[Dict, NocoDBRecord, List[Dict], List[NocoDBRecord]]):
                Single record or list of records to update. Can be dictionaries or NocoDBRecord objects.
                Each record must contain an "Id" field to identify which record to update.
            
        Returns:
            Union[NocoDBRecord, List[NocoDBRecord]]: Updated record(s) as NocoDBRecord objects
            
        Raises:
            ValueError: If column names in records are invalid or if "Id" field is missing
            requests.exceptions.RequestException: If the API request fails
            
        Example:
            >>> # Update single record from dictionary
            >>> result = table.update_records({"Id": 123, "Name": "John Updated", "Age": 31})
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John Updated', 'Age': 31})
            
            >>> # Update single record from NocoDBRecord
            >>> record = table.get_record(123)
            >>> record["Name"] = "John Updated"
            >>> result = table.update_records(record)
            >>> print(result)
            NocoDBRecord(record_id=123, table_id='table_id', status=attached, data={'Name': 'John Updated', 'Age': 31})
            
            >>> # Update multiple records
            >>> result = table.update_records([
            ...     {"Id": 123, "Name": "John Updated", "Age": 31},
            ...     {"Id": 124, "Name": "Jane Updated", "Age": 26}
            ... ])
            >>> print(result)
            [NocoDBRecord(record_id=123, ...), NocoDBRecord(record_id=124, ...)]
        """
        if isinstance(records, list):
            # Type assertion: List[Dict] | List[NocoDBRecord] is compatible with List[Dict | NocoDBRecord]
            return self._update_records_batch(records)  # type: ignore
        else:
            return self.update_record(records)
    
    def delete_records(self, records: Union[Dict, NocoDBRecord, List[Dict], List[NocoDBRecord]]) -> Union[Dict, List[Dict]]:
        """
        Delete one or more records from the table (backward compatibility wrapper).
        
        This method wraps the new delete_record and _delete_records_batch methods for backward compatibility.
        
        Args:
            records (Union[Dict, NocoDBRecord, List[Dict], List[NocoDBRecord]]):
                Single record or list of records to delete. Can be dictionaries or NocoDBRecord objects.
                Each record must contain an "Id" field to identify which record to delete.
            
        Returns:
            Union[Dict, List[Dict]]: Deletion result(s) (API response)
            
        Raises:
            ValueError: If "Id" field is missing in records
            requests.exceptions.RequestException: If the API request fails
            
        Example:
            >>> # Delete single record from dictionary
            >>> result = table.delete_records({"Id": 123})
            >>> print(result)
            {"Id": 123}
            
            >>> # Delete single record from NocoDBRecord
            >>> record = table.get_record(123)
            >>> result = table.delete_records(record)
            >>> print(result)
            {"Id": 123}
            
            >>> # Delete multiple records
            >>> result = table.delete_records([
            ...     {"Id": 123},
            ...     {"Id": 124}
            ... ])
            >>> print(result)
            [{"Id": 123}, {"Id": 124}]
        """
        if isinstance(records, list):
            # Type assertion: List[Dict] | List[NocoDBRecord] is compatible with List[Dict | NocoDBRecord]
            return self._delete_records_batch(records)  # type: ignore
        else:
            return self.delete_record(records)

