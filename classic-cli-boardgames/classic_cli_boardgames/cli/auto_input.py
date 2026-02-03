"""Non-blocking input helpers for auto-play modes."""

from __future__ import annotations

import os
import sys
import time
from typing import Optional

if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    import msvcrt

    _FILE_TYPE_CHAR = 0x0002
    _FILE_TYPE_PIPE = 0x0003


class AutoCommandReader:
    """Read lines without blocking so auto-play can keep moving."""

    def __init__(self, poll_interval: float = 0.05) -> None:
        self._poll_interval = poll_interval
        self._eof = False
        self._buffer = ""
        self._pipe_buffer = b""
        self._encoding = sys.stdin.encoding or "utf-8"
        self._is_windows = os.name == "nt"
        if self._is_windows:
            self._handle = msvcrt.get_osfhandle(sys.stdin.fileno())
            self._kernel32 = ctypes.windll.kernel32
            self._file_type = self._kernel32.GetFileType(self._handle)

    def poll(self, timeout: float = 0.0) -> Optional[str]:
        """Return a line if one is ready, otherwise None."""
        if self._eof:
            return None
        if self._is_windows:
            return self._poll_windows(timeout)
        return self._poll_posix(timeout)

    def _poll_posix(self, timeout: float) -> Optional[str]:
        import select

        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return None
        line = sys.stdin.readline()
        if line == "":
            self._eof = True
            return None
        return line.rstrip("\r\n")

    def _poll_windows(self, timeout: float) -> Optional[str]:
        end_time = time.monotonic() + timeout
        while True:
            if self._file_type == _FILE_TYPE_CHAR:
                line = self._read_console_line()
            elif self._file_type == _FILE_TYPE_PIPE:
                line = self._read_pipe_line()
            else:
                return None
            if line is not None:
                return line
            if time.monotonic() >= end_time:
                return None
            time.sleep(self._poll_interval)

    def _read_console_line(self) -> Optional[str]:
        while msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                line = self._buffer
                self._buffer = ""
                return line
            if ch == "\b":
                self._buffer = self._buffer[:-1]
                continue
            if ch == "\003":
                raise KeyboardInterrupt
            self._buffer += ch
        return None

    def _pipe_bytes_available(self) -> int:
        available = wintypes.DWORD()
        success = self._kernel32.PeekNamedPipe(
            self._handle,
            None,
            0,
            None,
            ctypes.byref(available),
            None,
        )
        if not success:
            return 0
        return int(available.value)

    def _read_pipe_line(self) -> Optional[str]:
        available = self._pipe_bytes_available()
        if available <= 0:
            return None
        chunk = os.read(sys.stdin.fileno(), available)
        if not chunk:
            self._eof = True
            return None
        self._pipe_buffer += chunk
        if b"\n" not in self._pipe_buffer:
            return None
        line, self._pipe_buffer = self._pipe_buffer.split(b"\n", 1)
        return line.decode(self._encoding, errors="replace").rstrip("\r")
