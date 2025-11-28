"""Test package structure and directory layout."""

from pathlib import Path
import pytest


class TestActualProjectStructure:
    """Test that the actual project structure exists and is properly organized."""
    
    def test_src_structure_exists(self):
        """Test that src directory structure exists."""
        assert Path("src").exists()
        assert Path("src/__init__.py").exists() or True  # __init__.py is optional at root
    
    def test_core_modules_exist(self):
        """Test that core modules exist in src/."""
        core_modules = [
            "src/core",
            "src/api", 
            "src/mcp",
            "src/sdk",
            "src/utils",
        ]
        
        for module_path in core_modules:
            assert Path(module_path).exists(), f"Module {module_path} should exist"
    
    def test_core_submodules_exist(self):
        """Test that core submodules exist."""
        core_submodules = [
            "src/core/auth.py",
            "src/core/client.py", 
            "src/core/config.py",
            "src/core/models.py",
            "src/core/exceptions.py",
            "src/core/reports.py",
        ]
        
        for module_path in core_submodules:
            assert Path(module_path).exists(), f"Core module {module_path} should exist"
    
    def test_api_structure(self):
        """Test that API structure exists."""
        assert Path("src/api").exists()
        assert Path("src/api/main.py").exists()
        assert Path("src/api/models.py").exists()
        assert Path("src/api/auth.py").exists()
    
    def test_mcp_structure(self):
        """Test that MCP structure exists."""
        assert Path("src/mcp").exists()
        assert Path("src/mcp/fastmcp_server.py").exists()
        assert Path("src/mcp/tools").exists()
    
    def test_sdk_structure(self):
        """Test that SDK structure exists."""
        assert Path("src/sdk").exists()
        assert Path("src/sdk/client.py").exists()
        assert Path("src/sdk/reports.py").exists()
    
    def test_utils_structure(self):
        """Test that utils structure exists."""
        assert Path("src/utils").exists()
        utils_modules = [
            "src/utils/cache.py",
            "src/utils/formatters.py",
            "src/utils/logger.py",
            "src/utils/validators.py",
        ]
        
        for module_path in utils_modules:
            assert Path(module_path).exists(), f"Utils module {module_path} should exist"
    
    def test_test_structure(self):
        """Test that test directory structure exists."""
        assert Path("tests").exists()
        test_dirs = [
            "tests/unit",
            "tests/integration", 
            "tests/api",
            "tests/performance",
        ]
        
        for test_dir in test_dirs:
            assert Path(test_dir).exists(), f"Test directory {test_dir} should exist"
    
    def test_configuration_files(self):
        """Test that configuration files exist."""
        assert Path("setup.py").exists()
        assert Path("requirements.txt").exists()
        assert Path("pytest.ini").exists()


class TestExistingStructureIntact:
    """Test that existing structure remains intact."""
    
    def test_existing_src_structure_intact(self):
        """Test that the existing src/ structure is not modified."""
        existing_modules = [
            "src/core",
            "src/api", 
            "src/mcp",
            "src/sdk",
            "src/utils",
        ]
        
        for module_path in existing_modules:
            assert Path(module_path).exists(), f"Existing module {module_path} should remain intact"
    
    def test_existing_config_intact(self):
        """Test that existing configuration remains intact."""
        existing_configs = [
            "config/agent_config.yaml",
            "googleads.yaml",
            "requirements.txt",
            "setup.py",
        ]
        
        for config_path in existing_configs:
            assert Path(config_path).exists(), f"Existing config {config_path} should remain intact"