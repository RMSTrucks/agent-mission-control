"""
SuperOptiX Client Wrapper

Provides a Python interface to SuperOptiX CLI commands.
Handles Windows encoding issues and provides clean API.

Usage:
    client = SuperOptiXClient()
    result = client.compile_agent("my_agent")
    if result.success:
        print(f"Compiled to: {result.output}")
"""

import subprocess
import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result from a SuperOptiX command execution"""
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    data: Optional[Dict[str, Any]] = None


class SuperOptiXClient:
    """
    Python wrapper for SuperOptiX CLI commands.

    Automatically handles:
    - Windows encoding issues (UTF-8)
    - Command path resolution
    - Output parsing
    - Error handling
    """

    def __init__(
        self,
        super_path: Optional[str] = None,
        project_root: Optional[str] = None
    ):
        """
        Initialize SuperOptiX client.

        Args:
            super_path: Path to super.exe (auto-detected if None)
            project_root: Root directory for agent projects (defaults to cwd)
        """
        self.super_path = super_path or self._find_super_exe()
        self.project_root = Path(project_root) if project_root else Path.cwd()

        # Validate super.exe exists
        if not os.path.exists(self.super_path):
            raise FileNotFoundError(
                f"SuperOptiX executable not found at: {self.super_path}\n"
                f"Install with: pip install superoptix"
            )

        logger.info(f"SuperOptiX client initialized: {self.super_path}")

    def _find_super_exe(self) -> str:
        """Auto-detect super.exe location"""
        # Common locations on Windows
        possible_paths = [
            r"C:\Users\Jake\AppData\Roaming\Python\Python312\Scripts\super.exe",
            r"C:\Python312\Scripts\super.exe",
            os.path.expanduser("~/.local/bin/super"),  # Linux/Mac
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Try PATH
        try:
            result = subprocess.run(
                ["where", "super.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass

        raise FileNotFoundError(
            "Could not find super.exe. Please install SuperOptiX:\n"
            "  pip install superoptix"
        )

    def _run_command(
        self,
        args: List[str],
        cwd: Optional[str] = None,
        capture_json: bool = False
    ) -> CommandResult:
        """
        Execute a SuperOptiX command.

        Args:
            args: Command arguments (after 'super')
            cwd: Working directory (defaults to project_root)
            capture_json: Try to parse output as JSON

        Returns:
            CommandResult with success status and output
        """
        cmd = [self.super_path] + args
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # Fix Windows encoding issues

        work_dir = cwd or str(self.project_root)

        logger.debug(f"Running: {' '.join(cmd)} in {work_dir}")

        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters instead of crashing
                env=env,
                timeout=300  # 5 minute timeout
            )

            success = result.returncode == 0
            output = result.stdout.strip() if result.stdout else ""
            error = result.stderr.strip() if result.stderr else None

            # Try to extract JSON data if requested
            data = None
            if capture_json and output:
                try:
                    data = json.loads(output)
                except json.JSONDecodeError:
                    # Try to find JSON in output
                    import re
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(0))
                        except json.JSONDecodeError:
                            pass

            return CommandResult(
                success=success,
                output=output,
                error=error,
                exit_code=result.returncode,
                data=data
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(cmd)}")
            return CommandResult(
                success=False,
                output="",
                error="Command timed out after 5 minutes",
                exit_code=-1
            )
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return CommandResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1
            )

    # ========================================================================
    # Core Commands
    # ========================================================================

    def version(self) -> CommandResult:
        """Get SuperOptiX version"""
        return self._run_command(["--version"])

    def help(self, command: Optional[str] = None) -> CommandResult:
        """Get help for SuperOptiX or specific command"""
        args = ["--help"] if not command else [command, "--help"]
        return self._run_command(args)

    # ========================================================================
    # Agent Commands
    # ========================================================================

    def compile_agent(
        self,
        agent_name: str,
        output_dir: Optional[str] = None
    ) -> CommandResult:
        """
        Compile an agent to SuperSpec format.

        Args:
            agent_name: Name of the agent to compile
            output_dir: Output directory (optional)

        Returns:
            CommandResult with compilation status
        """
        args = ["agent", "compile", agent_name]
        if output_dir:
            args.extend(["--output", output_dir])

        return self._run_command(args)

    def list_agents(self) -> CommandResult:
        """List all available agents"""
        return self._run_command(["agent", "list"], capture_json=True)

    def deploy_agent(
        self,
        agent_name: str,
        target: Optional[str] = None
    ) -> CommandResult:
        """
        Deploy an agent.

        Args:
            agent_name: Name of agent to deploy
            target: Deployment target (e.g., 'vapi', 'vocode')
        """
        args = ["agent", "deploy", agent_name]
        if target:
            args.extend(["--target", target])

        return self._run_command(args)

    # ========================================================================
    # Testing Commands
    # ========================================================================

    def run_tests(
        self,
        spec_file: str,
        scenario: Optional[str] = None,
        verbose: bool = False
    ) -> CommandResult:
        """
        Run BDD tests on a SuperSpec file.

        Args:
            spec_file: Path to SuperSpec YAML file
            scenario: Specific scenario to run (optional)
            verbose: Verbose output

        Returns:
            CommandResult with test results
        """
        args = ["test", "run", spec_file]
        if scenario:
            args.extend(["--scenario", scenario])
        if verbose:
            args.append("--verbose")

        return self._run_command(args, capture_json=True)

    def create_test(
        self,
        spec_file: str,
        scenario_name: str,
        description: Optional[str] = None
    ) -> CommandResult:
        """
        Create a new test scenario.

        Args:
            spec_file: Path to SuperSpec file
            scenario_name: Name of the scenario
            description: Scenario description
        """
        args = ["test", "create", spec_file, scenario_name]
        if description:
            args.extend(["--description", description])

        return self._run_command(args)

    # ========================================================================
    # Optimization Commands (GEPA)
    # ========================================================================

    def optimize(
        self,
        spec_file: str,
        iterations: int = 10,
        strategy: str = "gepa",
        output: Optional[str] = None
    ) -> CommandResult:
        """
        Optimize an agent using GEPA.

        Args:
            spec_file: Path to SuperSpec YAML file
            iterations: Number of optimization iterations (default: 10)
            strategy: Optimization strategy (default: "gepa")
            output: Output file for optimized spec

        Returns:
            CommandResult with optimization results
        """
        args = ["optimize", spec_file]
        args.extend(["--iterations", str(iterations)])
        args.extend(["--strategy", strategy])
        if output:
            args.extend(["--output", output])

        return self._run_command(args, capture_json=True)

    def evaluate(
        self,
        spec_file: str,
        baseline: bool = False
    ) -> CommandResult:
        """
        Evaluate agent performance.

        Args:
            spec_file: Path to SuperSpec file
            baseline: Run as baseline evaluation

        Returns:
            CommandResult with evaluation metrics
        """
        args = ["evaluate", spec_file]
        if baseline:
            args.append("--baseline")

        return self._run_command(args, capture_json=True)

    # ========================================================================
    # Project Commands
    # ========================================================================

    def init_project(
        self,
        project_name: str,
        project_dir: Optional[str] = None
    ) -> CommandResult:
        """
        Initialize a new SuperOptiX project.

        Args:
            project_name: Name of the project
            project_dir: Directory to create project in
        """
        args = ["init", project_name]
        cwd = project_dir or str(self.project_root)

        return self._run_command(args, cwd=cwd)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def check_installation(self) -> Dict[str, Any]:
        """
        Check SuperOptiX installation status.

        Returns:
            Dict with installation info
        """
        version_result = self.version()

        return {
            "installed": version_result.success,
            "path": self.super_path,
            "version": version_result.output if version_result.success else None,
            "error": version_result.error
        }

    def get_config(self) -> Dict[str, Any]:
        """
        Get current client configuration.

        Returns:
            Dict with client config
        """
        return {
            "super_path": self.super_path,
            "project_root": str(self.project_root),
            "exists": os.path.exists(self.super_path)
        }


# ========================================================================
# Convenience Functions
# ========================================================================

def create_client(project_root: Optional[str] = None) -> SuperOptiXClient:
    """
    Create a SuperOptiX client instance.

    Args:
        project_root: Root directory for agent projects

    Returns:
        Configured SuperOptiXClient
    """
    return SuperOptiXClient(project_root=project_root)


def check_superoptix_installed() -> bool:
    """
    Quick check if SuperOptiX is installed and working.

    Returns:
        True if installed and working, False otherwise
    """
    try:
        client = create_client()
        result = client.version()
        return result.success
    except Exception as e:
        logger.error(f"SuperOptiX check failed: {e}")
        return False


# ========================================================================
# Module-level test
# ========================================================================

if __name__ == "__main__":
    # Test the client
    print("Testing SuperOptiX Client...")

    try:
        client = create_client()
        print(f"\nClient Config: {json.dumps(client.get_config(), indent=2)}")

        print("\nChecking installation...")
        install_info = client.check_installation()
        print(json.dumps(install_info, indent=2))

        if install_info["installed"]:
            print("\nSUCCESS: SuperOptiX is installed and working!")
        else:
            print(f"\nERROR: {install_info['error']}")

    except Exception as e:
        print(f"\nERROR: {e}")
