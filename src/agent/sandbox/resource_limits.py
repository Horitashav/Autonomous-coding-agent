"""Resource limits for the Docker sandbox."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxLimits:
    """Immutable configuration for sandbox resource constraints."""

    memory: str = "512m"  # RAM limit (e.g. 512MB)
    cpu_count: int = 1  # CPU core count
    timeout_seconds: int = 15  # Execution cutoff timer
    pid_limit: int = 64  # Maximum concurrent processes (stops fork bombs)
    tmpfs_size: str = "64m"  # Writable in-memory scratch space
    network_mode: str = "none"  # Disable all network adapters (no internet access)
    read_only: bool = True  # Protect container root filesystem from changes

    def to_docker_kwargs(self) -> dict:
        """Convert security limits into Docker SDK keyword arguments."""
        kwargs = {
            "mem_limit": self.memory,
            "nano_cpus": self.cpu_count * 1_000_000_000,  # 1 CPU = 1 billion nanoseconds
            "pids_limit": self.pid_limit,
            "network_mode": self.network_mode,
            "read_only": self.read_only,
        }

        # Mount temporary writable scratch space in RAM if read_only is enabled
        if self.read_only:
            # This is a container tmpfs mountpoint, not a host-side temp file.
            kwargs["tmpfs"] = {"/tmp": f"rw,size={self.tmpfs_size}"}  # nosec B108

        return kwargs


# Standard default instance for reuse
DEFAULT_LIMITS = SandboxLimits()
