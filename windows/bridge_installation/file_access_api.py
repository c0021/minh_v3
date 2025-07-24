#!/usr/bin/env python3
"""
Sierra Chart File Access API
============================

Secure file system API for accessing Sierra Chart historical data.
Provides read-only access to .dly (CSV) and .scid (binary) files with strict security controls.

Security Features:
- Path validation restricts access to Sierra Chart data directory only
- Read-only operations (no write/delete capabilities)
- Input sanitization and validation
- Comprehensive error handling and logging

Author: MinhOS v3 System
Date: 2025-01-24
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Query
from fastapi.responses import PlainTextResponse, Response
import mimetypes

logger = logging.getLogger(__name__)

class SierraFileAccessAPI:
    """
    Secure file access API for Sierra Chart data files.
    
    Provides controlled access to Sierra Chart's historical data archive
    with comprehensive security validations and logging.
    """
    
    def __init__(self):
        """Initialize Sierra Chart File Access API"""
        # Define allowed base paths (Sierra Chart data directories)
        self.allowed_base_paths = [
            "C:\\SierraChart\\Data",
            "C:\\Sierra Chart\\Data",
            "D:\\SierraChart\\Data",
            "D:\\Sierra Chart\\Data"
        ]
        
        # Find the actual Sierra Chart data directory
        self.sierra_data_path = self._find_sierra_data_directory()
        
        # Supported file extensions for historical data
        self.allowed_extensions = {'.dly', '.scid', '.depth', '.txt', '.csv'}
        
        # File type mapping
        self.mime_types = {
            '.dly': 'text/csv',
            '.scid': 'application/octet-stream',
            '.depth': 'application/octet-stream',
            '.txt': 'text/plain',
            '.csv': 'text/csv'
        }
        
        logger.info(f"Sierra File Access API initialized - Data path: {self.sierra_data_path}")
    
    def _find_sierra_data_directory(self) -> Optional[str]:
        """Find the actual Sierra Chart data directory"""
        for path in self.allowed_base_paths:
            if os.path.exists(path) and os.path.isdir(path):
                logger.info(f"Found Sierra Chart data directory: {path}")
                return path
        
        logger.warning("No Sierra Chart data directory found - using default path")
        return self.allowed_base_paths[0]  # Default to first path
    
    def _validate_path(self, file_path: str) -> str:
        """
        Validate and normalize file path for security.
        
        Args:
            file_path: Requested file path
            
        Returns:
            Normalized absolute path
            
        Raises:
            HTTPException: If path is invalid or outside allowed directories
        """
        try:
            # Normalize path separators and resolve relative paths
            normalized_path = os.path.normpath(file_path.replace('/', '\\'))
            
            # Convert to absolute path
            if not os.path.isabs(normalized_path):
                normalized_path = os.path.join(self.sierra_data_path, normalized_path)
            
            # Resolve any remaining relative components
            resolved_path = os.path.abspath(normalized_path)
            
            # Security check: Ensure path is within allowed directories
            is_allowed = False
            for allowed_path in self.allowed_base_paths:
                try:
                    # Check if resolved path is within allowed directory
                    allowed_abs = os.path.abspath(allowed_path)
                    if resolved_path.startswith(allowed_abs + os.sep) or resolved_path == allowed_abs:
                        is_allowed = True
                        break
                except Exception:
                    continue
            
            if not is_allowed:
                logger.error(f"Access denied - path outside allowed directories: {resolved_path}")
                raise HTTPException(status_code=403, detail="Access denied - path outside allowed directories")
            
            # Check file extension
            file_ext = Path(resolved_path).suffix.lower()
            if file_ext not in self.allowed_extensions:
                logger.error(f"Access denied - unsupported file extension: {file_ext}")
                raise HTTPException(status_code=403, detail=f"Access denied - unsupported file extension: {file_ext}")
            
            logger.debug(f"Path validation successful: {resolved_path}")
            return resolved_path
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid file path")
    
    async def list_files(self, path: str = Query(..., description="Directory path to list")) -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            path: Directory path to list
            
        Returns:
            Dictionary containing file listing
        """
        try:
            # Validate directory path
            validated_path = self._validate_path(path)
            
            # Check if directory exists
            if not os.path.exists(validated_path):
                raise HTTPException(status_code=404, detail="Directory not found")
            
            if not os.path.isdir(validated_path):
                raise HTTPException(status_code=400, detail="Path is not a directory")
            
            # List directory contents
            files = []
            directories = []
            
            try:
                for item in os.listdir(validated_path):
                    item_path = os.path.join(validated_path, item)
                    
                    if os.path.isfile(item_path):
                        # Check if file extension is allowed
                        file_ext = Path(item).suffix.lower()
                        if file_ext in self.allowed_extensions:
                            stat_info = os.stat(item_path)
                            files.append({
                                'name': item,
                                'size': stat_info.st_size,
                                'modified': stat_info.st_mtime,
                                'type': 'file',
                                'extension': file_ext
                            })
                    
                    elif os.path.isdir(item_path):
                        directories.append({
                            'name': item,
                            'type': 'directory'
                        })
                        
            except PermissionError:
                logger.error(f"Permission denied accessing directory: {validated_path}")
                raise HTTPException(status_code=403, detail="Permission denied")
            
            result = {
                'path': validated_path,
                'files': files,
                'directories': directories,
                'total_files': len(files),
                'total_directories': len(directories)
            }
            
            logger.info(f"Listed directory: {validated_path} - {len(files)} files, {len(directories)} directories")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def read_file(self, path: str = Query(..., description="File path to read")) -> PlainTextResponse:
        """
        Read text file content (for .dly, .txt, .csv files).
        
        Args:
            path: File path to read
            
        Returns:
            Plain text response with file content
        """
        try:
            # Validate file path
            validated_path = self._validate_path(path)
            
            # Check if file exists
            if not os.path.exists(validated_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.isfile(validated_path):
                raise HTTPException(status_code=400, detail="Path is not a file")
            
            # Check if it's a text file
            file_ext = Path(validated_path).suffix.lower()
            if file_ext not in {'.dly', '.txt', '.csv'}:
                raise HTTPException(status_code=400, detail="File is not a text file - use read_binary endpoint")
            
            # Read file content
            try:
                with open(validated_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"Read text file: {validated_path} - {len(content)} characters")
                
                # Return with appropriate content type
                mime_type = self.mime_types.get(file_ext, 'text/plain')
                return PlainTextResponse(content=content, media_type=mime_type)
                
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(validated_path, 'r', encoding='latin1') as f:
                        content = f.read()
                    
                    logger.info(f"Read text file with latin1 encoding: {validated_path}")
                    return PlainTextResponse(content=content, media_type='text/plain')
                    
                except Exception as e:
                    logger.error(f"Failed to read file with multiple encodings: {e}")
                    raise HTTPException(status_code=500, detail="Unable to read file - encoding error")
            
            except PermissionError:
                logger.error(f"Permission denied reading file: {validated_path}")
                raise HTTPException(status_code=403, detail="Permission denied")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def read_binary_file(self, path: str = Query(..., description="Binary file path to read")) -> Response:
        """
        Read binary file content (for .scid, .depth files).
        
        Args:
            path: Binary file path to read
            
        Returns:
            Binary response with file content
        """
        try:
            # Validate file path
            validated_path = self._validate_path(path)
            
            # Check if file exists
            if not os.path.exists(validated_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.isfile(validated_path):
                raise HTTPException(status_code=400, detail="Path is not a file")
            
            # Read binary content
            try:
                with open(validated_path, 'rb') as f:
                    content = f.read()
                
                logger.info(f"Read binary file: {validated_path} - {len(content)} bytes")
                
                # Determine content type
                file_ext = Path(validated_path).suffix.lower()
                mime_type = self.mime_types.get(file_ext, 'application/octet-stream')
                
                return Response(content=content, media_type=mime_type)
                
            except PermissionError:
                logger.error(f"Permission denied reading binary file: {validated_path}")
                raise HTTPException(status_code=403, detail="Permission denied")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading binary file: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_file_info(self, path: str = Query(..., description="File path to get info")) -> Dict[str, Any]:
        """
        Get file information and metadata.
        
        Args:
            path: File path to analyze
            
        Returns:
            Dictionary containing file metadata
        """
        try:
            # Validate file path
            validated_path = self._validate_path(path)
            
            # Check if file exists
            if not os.path.exists(validated_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            # Get file statistics
            stat_info = os.stat(validated_path)
            file_path = Path(validated_path)
            
            file_info = {
                'path': validated_path,
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size': stat_info.st_size,
                'created': stat_info.st_ctime,
                'modified': stat_info.st_mtime,
                'accessed': stat_info.st_atime,
                'is_file': os.path.isfile(validated_path),
                'is_directory': os.path.isdir(validated_path),
                'mime_type': self.mime_types.get(file_path.suffix.lower(), 'application/octet-stream')
            }
            
            logger.info(f"Retrieved file info: {validated_path}")
            return file_info
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def get_status(self) -> Dict[str, Any]:
        """Get file access API status"""
        return {
            'service': 'sierra_file_access_api',
            'status': 'operational',
            'sierra_data_path': self.sierra_data_path,
            'allowed_base_paths': self.allowed_base_paths,
            'allowed_extensions': list(self.allowed_extensions),
            'data_directory_exists': os.path.exists(self.sierra_data_path) if self.sierra_data_path else False
        }

# Global instance
sierra_file_api = SierraFileAccessAPI()