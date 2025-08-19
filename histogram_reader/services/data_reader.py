"""Data reader service for processing histogram CSV files."""

import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class DataReaderService:
    """Service for reading and processing histogram data files."""

    def __init__(self):
        """Initialize the data reader service."""
        self.loaded_files: Dict[str, pd.DataFrame] = {}
        self.processed_data: Dict[str, Dict[str, np.ndarray]] = {}

    def read_csv_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Read a CSV file and return the data as a pandas DataFrame.

        Args:
            file_path: Path to the CSV file

        Returns:
            DataFrame containing the histogram data or None if failed
        """
        try:
            # Read CSV with colon separator
            df = pd.read_csv(file_path, sep=":", header=0, index_col=0)

            # Clean column names (remove whitespace)
            df.columns = df.columns.str.strip()

            # Convert index to numeric (bin values)
            df.index = pd.to_numeric(df.index, errors="coerce")

            # Drop any rows with NaN index (invalid bin values)
            df = df.dropna()

            # Convert data to numeric, replacing non-numeric values with 0
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            return df

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def process_histogram_data(self, file_path: str) -> Optional[Dict[str, np.ndarray]]:
        """Process histogram data by grouping A0 and A1 channels.

        Args:
            file_path: Path to the processed file

        Returns:
            Dictionary mapping channel names to histogram data arrays
        """
        if file_path not in self.loaded_files:
            return None

        df = self.loaded_files[file_path]

        # Group channels by removing A0/A1 suffix
        channel_groups: Dict[str, List[str]] = {}
        for col in df.columns:
            # Extract base channel name (e.g., "Ch01" from "Ch01A0")
            base_channel = col[:-2] if col.endswith(("A0", "A1")) else col

            if base_channel not in channel_groups:
                channel_groups[base_channel] = []
            channel_groups[base_channel].append(col)

        # Process each channel group
        processed_channels: Dict[str, np.ndarray] = {}
        bin_values = df.index.values

        for base_channel, sub_channels in channel_groups.items():
            if len(sub_channels) == 2:  # A0 and A1
                # Sum the A0 and A1 values for each bin
                channel_data = df[sub_channels].sum(axis=1).values
                processed_channels[base_channel] = channel_data
            else:
                # Single channel, use as is
                channel_data = df[sub_channels[0]].values
                processed_channels[base_channel] = channel_data

        return {
            "channels": processed_channels,
            "bin_values": bin_values,
            "num_bins": len(bin_values),
        }

    def load_file(self, file_path: str) -> bool:
        """Load a file into memory.

        Args:
            file_path: Path to the file to load

        Returns:
            True if file was loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            return False

        # Read the CSV file
        df = self.read_csv_file(file_path)
        if df is None:
            return False

        # Store the raw data
        self.loaded_files[file_path] = df

        # Process the data
        processed = self.process_histogram_data(file_path)
        if processed:
            self.processed_data[file_path] = processed

        return True

    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get information about a loaded file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information or None if not loaded
        """
        if file_path not in self.loaded_files:
            return None

        df = self.loaded_files[file_path]
        processed = self.processed_data.get(file_path, {})

        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "num_channels": len(processed.get("channels", {})),
            "num_bins": processed.get("num_bins", 0),
            "bin_range": {
                "min": float(df.index.min()) if len(df.index) > 0 else 0,
                "max": float(df.index.max()) if len(df.index) > 0 else 0,
            },
            "channels": list(processed.get("channels", {}).keys()),
        }

    def get_channel_data(
        self, file_path: str, channel_name: str
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get histogram data for a specific channel.

        Args:
            file_path: Path to the file
            channel_name: Name of the channel

        Returns:
            Tuple of (bin_values, histogram_values) or None if not found
        """
        if file_path not in self.processed_data:
            return None

        processed = self.processed_data[file_path]
        channels = processed.get("channels", {})

        if channel_name not in channels:
            return None

        return processed["bin_values"], channels[channel_name]

    def get_all_channel_data(
        self, file_path: str
    ) -> Optional[Dict[str, Tuple[np.ndarray, np.ndarray]]]:
        """Get histogram data for all channels in a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary mapping channel names to (bin_values, histogram_values) tuples
        """
        if file_path not in self.processed_data:
            return None

        processed = self.processed_data[file_path]
        channels = processed.get("channels", {})

        result = {}
        for channel_name, histogram_values in channels.items():
            result[channel_name] = (processed["bin_values"], histogram_values)

        return result

    def scan_folder(self, folder_path: str) -> List[str]:
        """Scan a folder for supported histogram files.

        Args:
            folder_path: Path to the folder to scan

        Returns:
            List of file paths for supported files
        """
        supported_extensions = {".csv", ".txt", ".dat"}
        found_files = []

        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()

                    if file_ext in supported_extensions:
                        found_files.append(file_path)
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")

        return found_files

    def unload_file(self, file_path: str) -> bool:
        """Unload a file from memory.

        Args:
            file_path: Path to the file to unload

        Returns:
            True if file was unloaded successfully, False otherwise
        """
        if file_path in self.loaded_files:
            del self.loaded_files[file_path]

        if file_path in self.processed_data:
            del self.processed_data[file_path]

        return True

    def unload_all_files(self) -> None:
        """Unload all files from memory."""
        self.loaded_files.clear()
        self.processed_data.clear()

    def get_loaded_files(self) -> List[str]:
        """Get list of currently loaded file paths.

        Returns:
            List of file paths
        """
        return list(self.loaded_files.keys())

    def is_file_loaded(self, file_path: str) -> bool:
        """Check if a file is currently loaded.

        Args:
            file_path: Path to the file

        Returns:
            True if file is loaded, False otherwise
        """
        return file_path in self.loaded_files
