#!/usr/bin/env python3
"""
Sierra Chart File System Bridge API Extension
============================================

Extends the bridge to provide file system access to Sierra Chart data files.
Enables MinhOS to read historical .dly and .scid files directly.

Security Note: Only allows read access to Sierra Chart data directory.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
import mimetypes

logger = logging.getLogger(__name__)

class SierraFileAccessAPI:
    """API for accessing Sierra Chart data files"""
    
    def __init__(self, app: FastAPI):
        """Initialize file access API"""
        self.app = app
        
        # Security: Only allow access to Sierra Chart data directory
        self.allowed_base_paths = [
            "C:\\SierraChart\\Data",
            "C:\\SierraChart\\Data\\MarketDepthData"
        ]
        
        # Register endpoints
        self._register_endpoints()
        
        logger.info("Sierra Chart File Access API initialized")
    
    def _register_endpoints(self):
        """Register file access endpoints"""
        
        @self.app.get("/api/file/read")
        async def read_text_file(path: str = Query(..., description="File path to read")):
            """Read text file content (for .dly files)"""
            return await self._read_text_file(path)
        
        @self.app.get("/api/file/read_binary")
        async def read_binary_file(path: str = Query(..., description="Binary file path to read")):
            """Read binary file content (for .scid files)"""
            return await self._read_binary_file(path)
        
        @self.app.get("/api/file/list")
        async def list_directory(path: str = Query("C:\\SierraChart\\Data", description="Directory to list")):
            """List files in Sierra Chart data directory"""
            return await self._list_directory(path)
        
        @self.app.get("/api/file/info")
        async def get_file_info(path: str = Query(..., description="File path for info")):
            """Get file information"""
            return await self._get_file_info(path)
    
    async def _read_text_file(self, file_path: str) -> dict:
        """Read text file content with security validation"""
        try:
            # Validate path security
            if not self._is_path_allowed(file_path):
                raise HTTPException(status_code=403, detail="Access denied to this path")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Get file stats
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "content": content,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": file_path
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    async def _read_binary_file(self, file_path: str) -> Response:
        """Read binary file content with security validation"""
        try:
            # Validate path security
            if not self._is_path_allowed(file_path):
                raise HTTPException(status_code=403, detail="Access denied to this path")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            # Read binary content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"inline; filename={os.path.basename(file_path)}",
                    "X-File-Size": str(len(content)),
                    "X-File-Path": file_path
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading binary file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    async def _list_directory(self, dir_path: str) -> dict:
        """List directory contents with security validation"""
        try:
            # Validate path security
            if not self._is_path_allowed(dir_path):
                raise HTTPException(status_code=403, detail="Access denied to this path")
            
            # Check if directory exists
            if not os.path.exists(dir_path):
                raise HTTPException(status_code=404, detail="Directory not found")
            
            if not os.path.isdir(dir_path):
                raise HTTPException(status_code=400, detail="Path is not a directory")
            
            # List directory contents
            files = []
            directories = []
            
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                stat = os.stat(item_path)
                
                item_info = {
                    "name": item,
                    "path": item_path,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "is_directory": os.path.isdir(item_path)
                }
                
                if os.path.isdir(item_path):
                    directories.append(item_info)
                else:
                    # Add file extension info
                    item_info["extension"] = os.path.splitext(item)[1].lower()
                    files.append(item_info)
            
            return {
                "success": True,
                "path": dir_path,
                "files": sorted(files, key=lambda x: x["name"]),
                "directories": sorted(directories, key=lambda x: x["name"]),
                "total_files": len(files),
                "total_directories": len(directories)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")
    
    async def _get_file_info(self, file_path: str) -> dict:
        """Get detailed file information"""
        try:
            # Validate path security
            if not self._is_path_allowed(file_path):
                raise HTTPException(status_code=403, detail="Access denied to this path")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "is_directory": os.path.isdir(file_path),
                "extension": os.path.splitext(file_path)[1].lower(),
                "readable": os.access(file_path, os.R_OK),
                "size_mb": round(stat.st_size / (1024 * 1024), 2)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting file info {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        try:
            # Normalize path
            normalized_path = os.path.normpath(os.path.abspath(path))
            
            # Check against allowed base paths
            for allowed_path in self.allowed_base_paths:
                allowed_normalized = os.path.normpath(os.path.abspath(allowed_path))
                
                # Check if path is within allowed directory
                if normalized_path.startswith(allowed_normalized):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating path {path}: {e}")
            return False


def add_file_access_to_bridge(app: FastAPI):
    """Add file access API to existing bridge application"""
    file_api = SierraFileAccessAPI(app)
    logger.info("Sierra Chart file access API added to bridge")
    return file_api