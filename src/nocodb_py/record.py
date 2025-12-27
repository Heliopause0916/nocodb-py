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
    """
    
    def __init__(self,
                 data: Dict[str, Any],
                 record_id: Optional[int] = None,
                 table: Optional['NocoDBTable'] = None,
                 schema: Optional['NocoDBSchema'] = None):
        """
        Initialize NocoDB record
        
        Args:
            data: All record fields dictionary (user data + system fields)
            record_id: Record ID, None for offline records
            table: Table object, None for offline records
            schema: Table schema for field validation and classification
        """
        # Deep copy data to prevent external modifications
        self._data = copy.deepcopy(data) if data else {}
        self._record_id = record_id
        self._table = table
        self._schema = schema
        
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
    
    def attach(self, table: 'NocoDBTable', record_id: int) -> None:
        """Attach offline record to a table"""
        self._table = table
        self._record_id = record_id
    
    def detach(self) -> None:
        """Detach record from table, making it offline"""
        self._table = None
        self._record_id = None
    
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
            schema=schema
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
        table_id = self.table_id if self._table else None
        return f"NocoDBRecord(record_id={self._record_id}, table_id={table_id}, status={status}, data={self._data})"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return self.__str__()


class NocoDBRecordSet:
    """
    NocoDB record set, encapsulating multiple records
    
    Attributes:
        records (List[NocoDBRecord]): List of records
        table (Optional['NocoDBTable']): Table object
    """
    
    def __init__(self,
                 records: List[NocoDBRecord],
                 table: Optional['NocoDBTable'] = None):
        """
        Initialize record set
        
        Args:
            records: List of records
            table: Table object, optional
        """
        self.records = records
        self.table = table
    
    def __len__(self) -> int:
        """Number of records"""
        return len(self.records)
    
    def __getitem__(self, index: int) -> NocoDBRecord:
        """Index access"""
        return self.records[index]
    
    def __iter__(self) -> Iterator[NocoDBRecord]:
        """Iterator support"""
        return iter(self.records)
    
    def to_list(self) -> List[NocoDBRecord]:
        """Convert to plain list (backward compatibility)"""
        return self.records.copy()
    
    def to_api_format_list(self) -> List[Dict[str, Any]]:
        """Convert to NocoDB API format list"""
        return [record.to_api_format() for record in self.records]
    
    def __str__(self) -> str:
        """String representation"""
        table_id = self.table.table_id if self.table else None
        return f"NocoDBRecordSet(count={len(self.records)}, table_id={table_id})"
    
    def __repr__(self) -> str:
        """Official string representation"""
        return self.__str__()
