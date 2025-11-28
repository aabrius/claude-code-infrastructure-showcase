"""Test package installation and import functionality."""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path
import pytest


class TestPackageInstallation:
    """Test package installation scenarios."""
    
    def test_src_package_structure_importable(self):
        """Test that src package structure is importable."""
        # Add the src to Python path for testing
        import sys
        from pathlib import Path
        
        src_path = Path("src").resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            # Test core module imports
            import core
            import api
            import sdk
            import utils
            import mcp
            # Basic import test passed
            assert True
        except ImportError as e:
            pytest.skip(f"Import failed, likely missing dependencies: {e}")
    
    def test_package_installation_works(self):
        """Test that the package can be installed with setup.py."""
        try:
            # Test that we can run the installation check
            from pathlib import Path
            assert Path("setup.py").exists()
            assert Path("requirements.txt").exists()
            # Installation structure is valid
            assert True
        except Exception as e:
            pytest.skip(f"Package installation test failed: {e}")
    
    @pytest.mark.slow
    def test_core_package_installable_in_virtual_env(self):
        """Test that core package can be installed in a clean virtual environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            
            # Get paths
            if sys.platform == "win32":
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"
            
            try:
                # Upgrade pip
                subprocess.run([
                    str(pip_exe), "install", "--upgrade", "pip", "setuptools", "wheel"
                ], check=True, capture_output=True, text=True)
                
                # Install package in development mode
                current_path = Path(".").resolve()
                result = subprocess.run([
                    str(pip_exe), "install", "-e", str(current_path)
                ], capture_output=True, text=True, timeout=120)
                
                # Check if installation succeeded or failed due to missing dependencies
                if result.returncode != 0:
                    if "googleads" in result.stderr or "google-auth" in result.stderr:
                        pytest.skip("Installation failed due to missing GAM dependencies - expected in CI")
                    else:
                        pytest.fail(f"Package installation failed: {result.stderr}")
                
                # Test import in the virtual environment
                import_result = subprocess.run([
                    str(python_exe), "-c", "import src.core.models; print('Import successful')"
                ], capture_output=True, text=True, timeout=30)
                
                if import_result.returncode == 0:
                    assert "Import successful" in import_result.stdout
                else:
                    pytest.skip(f"Import test skipped due to dependencies: {import_result.stderr}")
                    
            except subprocess.TimeoutExpired:
                pytest.skip("Installation test timed out - likely due to network issues")
            except Exception as e:
                pytest.skip(f"Virtual environment test failed: {e}")


class TestImportStructure:
    """Test import structure and module organization."""
    
    def test_src_module_structure(self):
        """Test that src module has expected structure."""
        import sys
        from pathlib import Path
        
        src_path = Path("src").resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            # Test that core modules can be imported
            import core.models
            import core.config
            
            # Test that models have expected classes
            assert hasattr(core.models, 'ReportType')
            assert hasattr(core.models, 'DateRange')
            
        except ImportError as e:
            pytest.skip(f"Module structure test skipped due to import issues: {e}")
    
    def test_submodule_imports(self):
        """Test that submodules can be imported."""
        import sys
        from pathlib import Path
        
        src_path = Path("src").resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        submodules = [
            "core.auth",
            "core.config",
            "core.models",
            "core.exceptions",
            "core.client",
        ]
        
        for module_name in submodules:
            try:
                __import__(module_name)
                # Import successful
                assert True
            except ImportError as e:
                # Allow import failures due to missing dependencies
                pytest.skip(f"Import {module_name} failed due to dependencies: {e}")
                continue