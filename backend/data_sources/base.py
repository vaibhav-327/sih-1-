from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import pandas as pd

class DataSource(ABC):
    """
    Abstract base class for all MPLAD data sources.
    Ensures that ML pipeline, DB, and frontend are decoupled from specific data formats.
    """
    
    @abstractmethod
    def fetch_data(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fetch raw data and return (raw_dataframe, metadata_dict).
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Return the human-readable source name e.g., 'e-Sakshi' or 'Synthetic Demo'
        """
        pass

    @abstractmethod
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Return connection health, last sync time, record count, mode.
        """
        pass
