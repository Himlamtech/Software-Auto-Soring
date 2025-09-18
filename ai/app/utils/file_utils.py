"""File handling utilities."""

import os
import hashlib
import mimetypes
from typing import Optional, Tuple, List
from pathlib import Path
from datetime import datetime


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Validate if file has an allowed extension.
        
        Args:
            filename: Name of the file
            allowed_extensions: List of allowed extensions (e.g., ['.puml', '.txt'])
            
        Returns:
            True if extension is allowed, False otherwise
        """
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_bytes: int) -> bool:
        """
        Validate if file size is within allowed limits.
        
        Args:
            file_path: Path to the file
            max_size_bytes: Maximum allowed file size in bytes
            
        Returns:
            True if file size is allowed, False otherwise
        """
        try:
            file_size = Path(file_path).stat().st_size
            return file_size <= max_size_bytes
        except (OSError, FileNotFoundError):
            return False
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate file hash for integrity checking.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
            
        Returns:
            File hash as hex string, or None if error
        """
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (OSError, FileNotFoundError, ValueError):
            return None
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Generate a safe filename by removing/replacing dangerous characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove or replace dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        safe_filename = ''.join(c if c in safe_chars else '_' for c in filename)
        
        # Ensure filename is not empty and not too long
        if not safe_filename or safe_filename.replace('_', '').replace('.', '').replace('-', '') == '':
            safe_filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Limit length
        if len(safe_filename) > 255:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:250-len(ext)] + ext
        
        return safe_filename
    
    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def get_mime_type(file_path: str) -> Optional[str]:
        """
        Get MIME type of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string, or None if couldn't determine
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
    
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """
        Check if file is a text file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is text, False otherwise
        """
        mime_type = FileUtils.get_mime_type(file_path)
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # Additional check for files without extensions or unknown MIME types
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try to read first 1KB as text
            return True
        except (UnicodeDecodeError, FileNotFoundError, PermissionError):
            return False
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Safely read text file content.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            File content as string, or None if error
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            return None
    
    @staticmethod
    def write_text_file(
        file_path: str,
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> bool:
        """
        Safely write text content to file.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
            create_dirs: Whether to create parent directories
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path_obj = Path(file_path)
            
            if create_dirs:
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path_obj, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except (PermissionError, OSError):
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information, or None if error
        """
        try:
            file_path_obj = Path(file_path)
            stat = file_path_obj.stat()
            
            return {
                "name": file_path_obj.name,
                "size": stat.st_size,
                "extension": file_path_obj.suffix,
                "mime_type": FileUtils.get_mime_type(file_path),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "is_text": FileUtils.is_text_file(file_path),
                "hash": FileUtils.get_file_hash(file_path)
            }
        except (OSError, FileNotFoundError):
            return None
    
    @staticmethod
    def cleanup_old_files(
        directory: str,
        days_old: int,
        pattern: str = "*",
        dry_run: bool = False
    ) -> Tuple[int, List[str]]:
        """
        Clean up old files in a directory.
        
        Args:
            directory: Directory to clean
            days_old: Files older than this many days will be deleted
            pattern: File pattern to match (glob pattern)
            dry_run: If True, only return what would be deleted
            
        Returns:
            Tuple of (count_deleted, list_of_deleted_files)
        """
        deleted_files = []
        count = 0
        
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                return 0, []
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for file_path in directory_path.glob(pattern):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    if not dry_run:
                        file_path.unlink()
                    deleted_files.append(str(file_path))
                    count += 1
            
        except (OSError, PermissionError):
            pass
        
        return count, deleted_files
