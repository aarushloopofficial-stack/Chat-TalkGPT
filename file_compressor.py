"""
Chat&Talk GPT - File Compression Module
Compress and decompress files (ZIP, TAR, GZIP)
"""
import os
import gzip
import zipfile
import tarfile
import logging
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger("FileCompressor")


class FileCompressor:
    """
    File Compression Manager
    
    Features:
    - ZIP compression/decompression
    - TAR compression/decompression
    - GZIP compression
    - Batch file compression
    - Extract archives
    """
    
    def __init__(self, output_dir: str = "compressed"):
        """Initialize File Compressor"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info("File Compressor initialized")
    
    def compress_to_zip(
        self,
        files: List[str],
        output_filename: Optional[str] = None,
        compression_level: int = 6
    ) -> Dict[str, Any]:
        """
        Compress files to ZIP
        
        Args:
            files: List of file paths to compress
            output_filename: Output ZIP filename
            compression_level: 0-9 (0=store, 9=best)
            
        Returns:
            Compression result
        """
        try:
            if not output_filename:
                output_filename = f"archive_{Path().stat().st_mtime}.zip"
            
            if not output_filename.endswith('.zip'):
                output_filename += '.zip'
            
            filepath = os.path.join(self.output_dir, output_filename)
            
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
                    elif os.path.isdir(file_path):
                        for root, dirs, files_in_dir in os.walk(file_path):
                            for file in files_in_dir:
                                file_to_zip = os.path.join(root, file)
                                arcname = os.path.relpath(file_to_zip, os.path.dirname(file_path))
                                zipf.write(file_to_zip, arcname)
            
            return {
                "success": True,
                "filepath": filepath,
                "format": "zip",
                "files_count": len(files)
            }
            
        except Exception as e:
            logger.error(f"ZIP compression error: {e}")
            return {"success": False, "error": str(e)}
    
    def compress_to_tar(
        self,
        files: List[str],
        output_filename: Optional[str] = None,
        compression: str = "gz"
    ) -> Dict[str, Any]:
        """
        Compress files to TAR
        
        Args:
            files: List of file paths
            output_filename: Output filename
            compression: None, 'gz', 'bz2', or 'xz'
            
        Returns:
            Compression result
        """
        try:
            if not output_filename:
                output_filename = f"archive.tar"
            
            mode = "w"
            if compression == "gz":
                mode = "w:gz"
            elif compression == "bz2":
                mode = "w:bz2"
            elif compression == "xz":
                mode = "w:xz"
            
            if not output_filename.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz')):
                output_filename += f".tar.{compression}" if compression != "gz" else ".tar.gz"
            
            filepath = os.path.join(self.output_dir, output_filename)
            
            with tarfile.open(filepath, mode) as tar:
                for file_path in files:
                    tar.add(file_path, arcname=os.path.basename(file_path))
            
            return {
                "success": True,
                "filepath": filepath,
                "format": "tar",
                "compression": compression,
                "files_count": len(files)
            }
            
        except Exception as e:
            logger.error(f"TAR compression error: {e}")
            return {"success": False, "error": str(e)}
    
    def extract_zip(self, archive_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Extract ZIP archive"""
        try:
            if not os.path.exists(archive_path):
                return {"success": False, "error": "Archive not found"}
            
            if not output_dir:
                output_dir = os.path.join(self.output_dir, "extracted")
            
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(output_dir)
            
            return {
                "success": True,
                "output_dir": output_dir,
                "format": "zip"
            }
            
        except Exception as e:
            logger.error(f"ZIP extraction error: {e}")
            return {"success": False, "error": str(e)}
    
    def extract_tar(self, archive_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Extract TAR archive"""
        try:
            if not os.path.exists(archive_path):
                return {"success": False, "error": "Archive not found"}
            
            if not output_dir:
                output_dir = os.path.join(self.output_dir, "extracted")
            
            os.makedirs(output_dir, exist_ok=True)
            
            with tarfile.open(archive_path, 'r:*') as tar:
                tar.extractall(output_dir)
            
            return {
                "success": True,
                "output_dir": output_dir,
                "format": "tar"
            }
            
        except Exception as e:
            logger.error(f"TAR extraction error: {e}")
            return {"success": False, "error": str(e)}
    
    def compress_directory(self, directory: str, output_filename: Optional[str] = None, format: str = "zip") -> Dict[str, Any]:
        """Compress entire directory"""
        if not os.path.isdir(directory):
            return {"success": False, "error": "Directory not found"}
        
        if format == "zip":
            return self.compress_to_zip([directory], output_filename)
        elif format == "tar":
            return self.compress_to_tar([directory], output_filename)
        else:
            return {"success": False, "error": "Unsupported format"}


# Singleton
file_compressor = FileCompressor()


def compress_files(*args, **kwargs) -> Dict[str, Any]:
    return file_compressor.compress_to_zip(*args, **kwargs)


def extract_archive(*args, **kwargs) -> Dict[str, Any]:
    archive = args[0] if args else kwargs.get("archive_path")
    if archive.endswith('.zip'):
        return file_compressor.extract_zip(archive)
    else:
        return file_compressor.extract_tar(archive)
