"""
Filename: src/nocodb_py/record.py

NocoDB Record and RecordSet classes for Python
"""

import copy
from typing import Dict, List, Any, Optional, Iterator
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .table import NocoDBTable
    from .column import NocoDBSchema


class NocoDBRecord:
    """
    NocoDB record object, encapsulating record data and metadata
    
    Supports two states: online (attached to table) and offline (local data organization).
    
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
        return hash(frozenset(self._data.items()))
    
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
        """Safe access to user data"""
        return self._data.get(key, default)
    
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
    NocoDB record set with compressed columnar storage
    
    This implementation uses columnar storage to optimize memory usage for large datasets.
    Instead of storing each record as a separate dictionary with repeated field names,
    it stores data in columns (arrays of values per field) to avoid redundancy.
    
    Key features:
    - Columnar storage: Field names are stored once, values are stored in arrays
    - Memory optimization: Significant reduction in memory usage for large datasets
    - State management: Tracks online/offline, modified, and deleted states
    - Performance: Optimized batch operations and API format conversion
    
    Attributes:
        _field_names (List[str]): Unique field names across all records
        _data_columns (Dict[str, List[Any]]): Columnar data storage by field
        _record_metadata (List[Dict]): Record metadata (ID, status, etc.)
        _table (Optional['NocoDBTable']): Table object
        _schema (Optional['NocoDBSchema']): Table schema
        _is_attached (bool): Whether any record is attached to table
    """
    
    def __init__(self,
                 records: List[NocoDBRecord],
                 table: Optional['NocoDBTable'] = None):
        """
        Initialize record set with compressed columnar storage
        
        Args:
            records: List of records
            table: Table object, optional
        """
        # Initialize columnar storage structure
        self._field_names: List[str] = []
        self._data_columns: Dict[str, List[Any]] = {}
        self._record_metadata: List[Dict[str, Any]] = []
        self._table = table
        
        # Get schema from first record (if exists)
        self._schema = records[0].schema if records else None
        
        # Check if any record is attached
        self._is_attached = any(record.is_attached for record in records) if records else False
        
        # Build columnar storage
        self._build_columnar_storage(records)
    
    def _build_columnar_storage(self, records: List[NocoDBRecord]) -> None:
        """Build columnar storage from list of records"""
        if not records:
            return
        
        # Collect all unique field names
        all_field_names = set()
        for record in records:
            all_field_names.update(record._data.keys())
        self._field_names = sorted(all_field_names)
        
        # Initialize data columns
        for field in self._field_names:
            self._data_columns[field] = []
        
        # Fill data and metadata
        for i, record in enumerate(records):
            # Fill data columns
            for field in self._field_names:
                self._data_columns[field].append(record._data.get(field))
            
            # Create record metadata
            metadata = {
                "internal_index": i,
                "record_id": record.record_id,
                "is_attached": record.is_attached,
                "is_deleted": record.is_deleted,
                "is_modified": record.is_modified,
                "original_hash": record._original_data_hash
            }
            self._record_metadata.append(metadata)
    
    def __len__(self) -> int:
        """Number of records"""
        return len(self._record_metadata)
    
    def __getitem__(self, index: int) -> NocoDBRecord:
        """Get record by internal index"""
        if index < 0 or index >= len(self._record_metadata):
            raise IndexError(f"Record index {index} out of range")
        
        metadata = self._record_metadata[index]
        
        # Build record data dictionary
        data = {}
        for field in self._field_names:
            data[field] = self._data_columns[field][index]
        
        # Create NocoDBRecord object
        return NocoDBRecord(
            data=data,
            record_id=metadata["record_id"],
            table=self._table,
            schema=self._schema,
            is_deleted=metadata["is_deleted"]
        )
    
    def __iter__(self) -> Iterator[NocoDBRecord]:
        """Iterator support"""
        for i in range(len(self._record_metadata)):
            yield self[i]
    
    def to_list(self) -> List[NocoDBRecord]:
        """Convert to plain list (backward compatibility)"""
        return list(self)
    
    def to_api_format_list(self) -> List[Dict[str, Any]]:
        """Convert to NocoDB API format list with batch optimization"""
        result = []
        for i, metadata in enumerate(self._record_metadata):
            # Build API format data
            api_data = {}
            for field in self._field_names:
                api_data[field] = self._data_columns[field][i]
            
            # Add record ID (if exists)
            if metadata["record_id"] is not None:
                api_data["Id"] = metadata["record_id"]
            
            result.append(api_data)
        
        return result
    
    @property
    def is_attached(self) -> bool:
        """Whether any record in the set is attached to a table"""
        return self._is_attached
    
    @property
    def is_detached(self) -> bool:
        """Whether all records in the set are detached"""
        return not self._is_attached
    
    def get_attached_records(self) -> List[int]:
        """Get indices of attached records"""
        return [i for i, meta in enumerate(self._record_metadata) if meta["is_attached"]]
    
    def get_detached_records(self) -> List[int]:
        """Get indices of detached records"""
        return [i for i, meta in enumerate(self._record_metadata) if not meta["is_attached"]]
    
    def get_modified_records(self) -> List[int]:
        """Get indices of modified records"""
        return [i for i, meta in enumerate(self._record_metadata) if meta["is_modified"]]
    
    def get_deleted_records(self) -> List[int]:
        """Get indices of deleted records"""
        return [i for i, meta in enumerate(self._record_metadata) if meta["is_deleted"]]
    
    def mark_all_clean(self) -> None:
        """Mark all records as unmodified"""
        for meta in self._record_metadata:
            meta["is_modified"] = False
    
    def update_record(self, internal_index: int, updates: Dict[str, Any]) -> None:
        """Update specific record data"""
        if internal_index < 0 or internal_index >= len(self._record_metadata):
            raise IndexError(f"Record index {internal_index} out of range")
        
        # Update data columns
        for field, value in updates.items():
            if field in self._data_columns:
                self._data_columns[field][internal_index] = value
        
        # Mark as modified
        self._record_metadata[internal_index]["is_modified"] = True
    
    def bulk_update(self, updates: Dict[int, Dict[str, Any]]) -> None:
        """Bulk update multiple records"""
        for internal_index, record_updates in updates.items():
            self.update_record(internal_index, record_updates)
    
    def get_field_values(self, field_name: str) -> List[Any]:
        """Get all values for a specific field"""
        return self._data_columns.get(field_name, [])
    
    @property
    def memory_usage(self) -> int:
        """Estimate memory usage in bytes"""
        # Field names storage
        field_names_size = sum(len(field) for field in self._field_names)
        
        # Data columns storage estimation
        data_size = 0
        for field, values in self._data_columns.items():
            data_size += len(field)  # Field name
            data_size += sum(self._estimate_value_size(v) for v in values)
        
        # Metadata storage
        metadata_size = len(self._record_metadata) * 100  # Estimate 100 bytes per metadata
        
        return field_names_size + data_size + metadata_size
    
    def _estimate_value_size(self, value: Any) -> int:
        """Estimate size of a value in bytes"""
        if isinstance(value, str):
            return len(value)
        elif isinstance(value, (int, float)):
            return 8
        elif value is None:
            return 0
        else:
            return 50  # Default estimate
    
    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio compared to original storage"""
        if not self._record_metadata:
            return 1.0
        
        # Estimate original storage size (each record stores field names independently)
        original_size = len(self._record_metadata) * sum(len(field) for field in self._field_names)
        original_size += self.memory_usage  # Add data itself
        
        return self.memory_usage / original_size if original_size > 0 else 1.0
    
    def __str__(self) -> str:
        """String representation"""
        table_id = self._table.table_id if self._table else None
        compression_info = f", compression_ratio={self.compression_ratio:.2%}" if self._record_metadata else ""
        return f"NocoDBRecordSet(count={len(self._record_metadata)}, table_id={table_id}{compression_info})"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return self.__str__()
