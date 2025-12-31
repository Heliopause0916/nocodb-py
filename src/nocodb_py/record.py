"""
Filename: src/nocodb_py/record.py

NocoDB Record and RecordSet classes for Python
"""

import copy
from typing import Dict, List, Any, Optional, Iterator
from typing import TYPE_CHECKING
from .exceptions import RecordNotFoundError
if TYPE_CHECKING:
    from .table import NocoDBTable
    from .column import NocoDBSchema


class NocoDBRecord:
    """
    NocoDB record object, encapsulating record data and metadata
    
    Supports two states: online (attached to table) and offline (local data organization).
    
    === STATE SPECIFICATIONS ===
    
    Record Sources:
        Records can only come from two sources:
        1. API-returned records: Returned by get_record() or list_records() methods,
           naturally in attached state with ID and table_id
        2. Locally generated records: Created by users locally, not yet saved to table,
           in detached state with record_id=None and table=None
    
    State Transitions:
        - create_record() is the ONLY method that converts detached records to attached
        - State is IRREVERSIBLE: once a record has an ID (attached), it can never
          return to detached state
        - State protection: Prevents illegal state transitions to ensure data consistency
    
    Copy Operations:
        When using copy.copy() or copy.deepcopy():
        - ID and table_id cannot be copied, copied record becomes detached
        - System columns (Id, CreatedAt, UpdatedAt, etc.) cannot be copied
        - Advanced columns (link, attachment, etc.) copy strategy needs separate discussion
        - User data fields are copied normally
    
    Data Access Interfaces:
        - Dictionary-style access: record["field"] and record.get("field")
        - Property access: record_id, table_id, schema properties for metadata
        - API format conversion: to_api_format() and from_api_format() methods
        - State detection: is_attached and is_detached properties
    
    State Protection:
        - _attach() method: Protected method, should only be called by table's
          create_records or create_record methods. Strongly discouraged to call directly.
        - _mark_deleted() method: Protected method, should only be called by table's
          delete_records or delete_record methods. Strongly discouraged to call directly.
    
    === ATTRIBUTES ===
    
    Attributes:
        _data (Dict[str, Any]): All record fields including user data and system fields
        _record_id (Optional[int]): Record ID, None for offline records
        _table (Optional['NocoDBTable']): Table object, None for offline records
        _schema (Optional[NocoDBSchema]): Table schema for field validation
        _original_data_hash (int): Hash of original data for modification detection
        _is_deleted (bool): Whether the record has been deleted from the database
    """
    
    def __init__(self,
                 data: Dict[str, Any],
                 record_id: Optional[int] = None,
                 table: Optional['NocoDBTable'] = None,
                 schema: Optional['NocoDBSchema'] = None,
                 is_deleted: bool = False):
        """
        Initialize NocoDB record
        
        Args:
            data: All record fields dictionary (user data + system fields)
            record_id: Record ID, None for offline records
            table: Table object, None for offline records
            schema: Table schema for field validation and classification
            is_deleted: Whether the record has been deleted from the database
        """
        # Deep copy data to prevent external modifications
        self._data = copy.deepcopy(data) if data else {}
        self._record_id = record_id
        self._table = table
        self._schema = schema
        self._is_deleted = is_deleted
        
        # Track original data state for modification detection
        self._original_data_hash = self._compute_data_hash()
    
    def _compute_data_hash(self) -> int:
        """Compute hash of the current data for modification detection"""
        def _hash_value(value: Any) -> int:
            """Recursively compute hash for nested data structures"""
            if isinstance(value, dict):
                # Hash dictionary by recursively hashing key-value pairs
                return hash(frozenset((k, _hash_value(v)) for k, v in value.items()))
            elif isinstance(value, (list, tuple)):
                # Hash sequence by recursively hashing elements
                return hash(tuple(_hash_value(item) for item in value))
            elif isinstance(value, set):
                # Hash set by recursively hashing elements
                return hash(frozenset(_hash_value(item) for item in value))
            else:
                # Hash primitive values directly
                return hash(value)
        
        return _hash_value(self._data)
    
    @property
    def record_id(self) -> Optional[int]:
        """Record ID, None for offline records"""
        return self._record_id
    
    @property
    def table(self) -> Optional['NocoDBTable']:
        """Table object, None for offline records"""
        return self._table
    
    @property
    def table_id(self) -> Optional[str]:
        """Table ID, None for offline records (convenience property)"""
        return self._table.table_id if self._table else None
    
    @property
    def schema(self) -> Optional['NocoDBSchema']:
        """Table schema, if available"""
        return self._schema
    
    @property
    def is_attached(self) -> bool:
        """Whether the record is attached to a NocoDB table"""
        return self._record_id is not None and self._table is not None
    
    @property
    def is_detached(self) -> bool:
        """Whether the record is offline (detached)"""
        return not self.is_attached
    
    @property
    def is_modified(self) -> bool:
        """Whether the record data has been modified since creation"""
        return self._compute_data_hash() != self._original_data_hash
    
    @property
    def is_deleted(self) -> bool:
        """Whether the record has been deleted from the database"""
        return self._is_deleted
    
    def _attach(self, table: 'NocoDBTable', record_id: int) -> None:
        """
        Attach offline record to a table (protected method)
        
        This method should only be called by table's create_records or create_record methods.
        Strongly discouraged to call this method directly from external code.
        
        Args:
            table: Table object to attach to
            record_id: Record ID assigned by NocoDB
        """
        self._table = table
        self._record_id = record_id
        self._is_deleted = False  # Reset deleted status when attaching
    
    def _mark_deleted(self) -> None:
        """
        Mark record as deleted (protected method)
        
        This method should only be called by table's delete_records or delete_record methods.
        Strongly discouraged to call this method directly from external code.
        """
        self._is_deleted = True
    
    def sync(self) -> 'NocoDBRecord':
        """
        Synchronize record data with the database by fetching the latest version.
        
        This method is only available for attached (online) records. It calls the
        table's get_record method to retrieve the latest data from the database
        and updates the record's internal data.
        
        Returns:
            NocoDBRecord: Self for method chaining
            
        Raises:
            ValueError: If the record is not attached to a table or has been deleted
            RecordNotFoundError: If the record no longer exists in the database
            requests.exceptions.HTTPError: For other HTTP errors
        """
        # Check if record is attached
        if not self.is_attached:
            raise ValueError("Cannot sync detached record. Only attached records can be synchronized.")
        
        # Check if record is deleted
        if self.is_deleted:
            raise ValueError("Cannot sync deleted record.")
        
        # Check if table is available
        if self._table is None:
            raise ValueError("Cannot sync record: table reference is None")
        
        # Type assertion for record_id (should not be None for attached records)
        if self._record_id is None:
            raise ValueError("Cannot sync record: record_id is None for attached record")
        
        try:
            # Get latest record data from table as JSON
            latest_data = self._table.get_record(self._record_id, return_type="json")
            
            # Type assertion: latest_data should be Dict when return_type="json"
            if not isinstance(latest_data, dict):
                raise TypeError(f"Expected dict from get_record with return_type='json', got {type(latest_data)}")
            
            # Create a copy of the API data (all fields including system fields)
            data = latest_data.copy()
            
            # Remove Id field from data to avoid duplication (same as from_api_format)
            if "Id" in data:
                del data["Id"]
            
            # Update internal data with latest data
            self._data = data
            
            # Reset original data hash to reflect new state
            self._original_data_hash = self._compute_data_hash()
            
            return self
        except RecordNotFoundError:
            # If record no longer exists, mark as deleted
            self._mark_deleted()
            raise
    
    def exists(self) -> bool:
        """
        Check if the record still exists in the database.
        
        This method is only available for attached (online) records. It calls the
        table's get_record method to check if the record exists, but does not
        update the record's internal data.
        
        Returns:
            bool: True if the record exists in the database, False otherwise
            
        Raises:
            ValueError: If the record is not attached to a table or has been deleted
            requests.exceptions.HTTPError: For other HTTP errors
        """
        # Check if record is attached
        if not self.is_attached:
            raise ValueError("Cannot check existence of detached record. Only attached records can be checked.")
        
        # Check if record is deleted
        if self.is_deleted:
            raise ValueError("Cannot check existence of deleted record.")
        
        # Check if table is available
        if self._table is None:
            raise ValueError("Cannot check record existence: table reference is None")
        
        # Type assertion for record_id (should not be None for attached records)
        if self._record_id is None:
            raise ValueError("Cannot check record existence: record_id is None for attached record")
        
        try:
            # Try to get the record (we don't care about the data, just if it exists)
            self._table.get_record(self._record_id, return_type="json")
            return True
        except RecordNotFoundError:
            # If record no longer exists, mark as deleted
            self._mark_deleted()
            return False
    
    def to_api_format(self) -> Dict[str, Any]:
        """
        Convert to NocoDB API native format
        
        Returns:
            Dict: Record dictionary in NocoDB API format
        """
        result = self._data.copy()
        
        # Add record ID if present
        if self._record_id is not None:
            result["Id"] = self._record_id
            
        return result
    
    @classmethod
    def from_api_format(cls, api_data: Dict[str, Any], table: Optional['NocoDBTable'] = None, schema: Optional['NocoDBSchema'] = None) -> 'NocoDBRecord':
        """
        Create record object from NocoDB API response
        
        Args:
            api_data: Record data returned by NocoDB API
            table: Table object, optional
            schema: Table schema, optional
            
        Returns:
            NocoDBRecord: Created record object
        """
        # Extract record ID from API data
        record_id = api_data.get("Id")
        
        # Create a copy of the API data (all fields including system fields)
        data = api_data.copy()
        
        # Remove Id field from data to avoid duplication
        if "Id" in data:
            del data["Id"]
            
        return cls(
            data=data,
            record_id=record_id,
            table=table,
            schema=schema,
            is_deleted=False
        )
    
    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access to user data"""
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-style setting of user data"""
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Safe access to user data with deep copy protection"""
        value = self._data.get(key, default)
        # Return deep copy to prevent external modifications
        # Only copy if value is not None and not the default value
        if value is not None and value is not default:
            return copy.deepcopy(value)
        else:
            return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value for a specific field by title
        
        Args:
            key: Field title/name
            value: Value to set
        """
        self._data[key] = value
    
    def __str__(self) -> str:
        """String representation"""
        status = "attached" if self.is_attached else "detached"
        deleted_status = ", deleted" if self.is_deleted else ""
        table_id = self.table_id if self._table else None
        return f"NocoDBRecord(record_id={self._record_id}, table_id={table_id}, status={status}{deleted_status}, data={self._data})"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return self.__str__()


class NocoDBRecordSet:
    """
    NocoDB record set with row-based storage
    
    This implementation uses row-based storage to optimize for frequent insert/delete operations.
    Field names are stored once in _field_names, and each record is stored as a list of values
    in the same order as _field_names. Metadata is stored in separate lists for efficiency.
    
    Key features:
    - Row-based storage: Each record is a list of values, field names stored once
    - Efficient insert/delete: O(n) complexity for row operations
    - State management: Tracks online/offline, modified, and deleted states
    - Performance: Optimized for row-level CRUD operations
    
    Attributes:
        _field_names (List[str]): Unique field names across all records (ordered)
        _data (List[List[Any]]): Row-based data storage, each inner list is a record
        _record_ids (List[Optional[int]]): Record IDs for each record
        _is_attached (List[bool]): Attachment status for each record
        _is_deleted (List[bool]): Deletion status for each record
        _is_modified (List[bool]): Modification status for each record
        _original_hashes (List[int]): Original data hashes for modification detection
        _table (Optional['NocoDBTable']): Table object
        _schema (Optional['NocoDBSchema']): Table schema
        _is_attached_any (bool): Whether any record is attached to table
    
    WARNING: After insert or delete operations, existing indices may point to different records.
    This is standard Python list behavior. Always refresh indices after structural modifications.
    """
    
    def __init__(self,
                 records: List[NocoDBRecord],
                 table: Optional['NocoDBTable'] = None):
        """
        Initialize record set with row-based storage
        
        Args:
            records: List of records
            table: Table object, optional
        """
        # Initialize row-based storage structure
        self._field_names: List[str] = []
        self._data: List[List[Any]] = []
        self._record_ids: List[Optional[int]] = []
        self._is_attached: List[bool] = []
        self._is_deleted: List[bool] = []
        self._is_modified: List[bool] = []
        self._original_hashes: List[int] = []
        self._table = table
        
        # Get schema from first record (if exists)
        self._schema = records[0].schema if records else None
        
        # Check if any record is attached
        self._is_attached_any = any(record.is_attached for record in records) if records else False
        
        # Build row-based storage
        self._build_row_storage(records)
    
    def _build_row_storage(self, records: List[NocoDBRecord]) -> None:
        """Build row-based storage from list of records"""
        if not records:
            return
        
        # Collect all field names and deduplicate while preserving order
        all_field_names = []
        for record in records:
            all_field_names.extend(record._data.keys())
        self._field_names = list(dict.fromkeys(all_field_names))
        
        # Build row-based data and metadata
        for record in records:
            # Build record row in field name order
            row = [record._data.get(field) for field in self._field_names]
            self._data.append(row)
            
            # Store metadata in separate lists
            self._record_ids.append(record.record_id)
            self._is_attached.append(record.is_attached)
            self._is_deleted.append(record.is_deleted)
            self._is_modified.append(record.is_modified)
            self._original_hashes.append(record._original_data_hash)
    
    def __len__(self) -> int:
        """Number of records"""
        return len(self._data)
    
    def __getitem__(self, index: int) -> NocoDBRecord:
        """Get record by internal index"""
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Record index {index} out of range")
        
        # Build record data dictionary from row data
        data = {}
        for i, field in enumerate(self._field_names):
            data[field] = self._data[index][i]
        
        # Create NocoDBRecord object
        return NocoDBRecord(
            data=data,
            record_id=self._record_ids[index],
            table=self._table,
            schema=self._schema,
            is_deleted=self._is_deleted[index]
        )
    
    def __iter__(self) -> Iterator[NocoDBRecord]:
        """Iterator support"""
        for i in range(len(self._data)):
            yield self[i]
    
    def to_list(self) -> List[NocoDBRecord]:
        """Convert to plain list (backward compatibility)"""
        return list(self)
    
    def to_api_format_list(self) -> List[Dict[str, Any]]:
        """Convert to NocoDB API format list with batch optimization"""
        result = []
        for i in range(len(self._data)):
            # Build API format data
            api_data = {}
            for j, field in enumerate(self._field_names):
                api_data[field] = self._data[i][j]
            
            # Add record ID (if exists)
            if self._record_ids[i] is not None:
                api_data["Id"] = self._record_ids[i]
            
            result.append(api_data)
        
        return result
    
    @property
    def is_attached(self) -> bool:
        """Whether any record in the set is attached to a table"""
        return self._is_attached_any
    
    @property
    def is_detached(self) -> bool:
        """Whether all records in the set are detached"""
        return not self._is_attached_any
    
    def get_attached_records(self) -> List[int]:
        """Get indices of attached records"""
        return [i for i, attached in enumerate(self._is_attached) if attached]
    
    def get_detached_records(self) -> List[int]:
        """Get indices of detached records"""
        return [i for i, attached in enumerate(self._is_attached) if not attached]
    
    def get_modified_records(self) -> List[int]:
        """Get indices of modified records"""
        return [i for i, modified in enumerate(self._is_modified) if modified]
    
    def get_deleted_records(self) -> List[int]:
        """Get indices of deleted records"""
        return [i for i, deleted in enumerate(self._is_deleted) if deleted]
    
    def mark_all_clean(self) -> None:
        """Mark all records as unmodified"""
        for i in range(len(self._is_modified)):
            self._is_modified[i] = False
    
    def update_record(self, internal_index: int, updates: Dict[str, Any]) -> None:
        """Update specific record data"""
        if internal_index < 0 or internal_index >= len(self._data):
            raise IndexError(f"Record index {internal_index} out of range")
        
        # Update data in the row
        for field, value in updates.items():
            if field in self._field_names:
                field_index = self._field_names.index(field)
                self._data[internal_index][field_index] = value
        
        # Mark as modified
        self._is_modified[internal_index] = True
    
    def bulk_update(self, updates: Dict[int, Dict[str, Any]]) -> None:
        """Bulk update multiple records"""
        for internal_index, record_updates in updates.items():
            self.update_record(internal_index, record_updates)
    
    def get_field_values(self, field_name: str) -> List[Any]:
        """Get all values for a specific field"""
        if field_name not in self._field_names:
            return []
        
        field_index = self._field_names.index(field_name)
        return [row[field_index] for row in self._data]
    
    def insert_record(self, index: int, record: NocoDBRecord) -> None:
        """
        Insert a record at the specified index
        
        Args:
            index: Position to insert the record
            record: Record to insert
        
        WARNING: After insertion, existing indices may point to different records.
        This is standard Python list behavior. Always refresh indices after structural modifications.
        """
        if index < 0 or index > len(self._data):
            raise IndexError(f"Insert index {index} out of range")
        
        # Build record row in field name order
        row = [record._data.get(field) for field in self._field_names]
        
        # Insert data and metadata
        self._data.insert(index, row)
        self._record_ids.insert(index, record.record_id)
        self._is_attached.insert(index, record.is_attached)
        self._is_deleted.insert(index, record.is_deleted)
        self._is_modified.insert(index, record.is_modified)
        self._original_hashes.insert(index, record._original_data_hash)
        
        # Update attachment status
        if record.is_attached:
            self._is_attached_any = True
    
    def delete_record(self, index: int) -> None:
        """
        Delete record at the specified index
        
        Args:
            index: Index of record to delete
        
        WARNING: After deletion, existing indices may point to different records.
        This is standard Python list behavior. Always refresh indices after structural modifications.
        """
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Delete index {index} out of range")
        
        # Delete data and metadata
        del self._data[index]
        del self._record_ids[index]
        del self._is_attached[index]
        del self._is_deleted[index]
        del self._is_modified[index]
        del self._original_hashes[index]
        
        # Update attachment status if needed
        if not any(self._is_attached):
            self._is_attached_any = False
    
    def __str__(self) -> str:
        """String representation"""
        table_id = self._table.table_id if self._table else None
        return f"NocoDBRecordSet(count={len(self._data)}, table_id={table_id})"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return self.__str__()
