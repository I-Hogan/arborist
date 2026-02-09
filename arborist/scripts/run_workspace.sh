#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
workspace_root=$(cd "$script_dir/../.." && pwd)
arborist_root=$(cd "$script_dir/.." && pwd)
ui_port="${ARBORIST_UI_PORT:-7788}"
ui_url="http://localhost:${ui_port}"
runner_pid=""
ui_pid=""

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM
  if [[ -n "${runner_pid}" ]] && kill -0 "${runner_pid}" >/dev/null 2>&1; then
    kill "${runner_pid}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${ui_pid}" ]] && kill -0 "${ui_pid}" >/dev/null 2>&1; then
    kill "${ui_pid}" >/dev/null 2>&1 || true
  fi
  wait >/dev/null 2>&1 || true
  exit "${exit_code}"
}

trap cleanup EXIT INT TERM

if ! [[ "${ui_port}" =~ ^[0-9]+$ ]] || (( ui_port < 1 || ui_port > 65535 )); then
  echo "Invalid ARBORIST_UI_PORT: ${ui_port}" >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required." >&2
  exit 1
fi

if [[ ! -d "${arborist_root}/node_modules" ]]; then
  echo "Installing Arborist UI dependencies..."
  npm --prefix "${arborist_root}" install --silent
fi

echo "Starting Arborist UI server..."
ARBORIST_UI_PORT="${ui_port}" node "${script_dir}/web_ui.mjs" &
ui_pid=$!

sleep 1
if ! kill -0 "${ui_pid}" >/dev/null 2>&1; then
  set +e
  wait "${ui_pid}"
  ui_status=$?
  set -e
  echo "Arborist UI failed to start." >&2
  exit "${ui_status}"
fi

echo "Starting Arborist runner..."
if [[ "$#" -eq 0 ]]; then
  "${script_dir}/run_arborist.sh" "${workspace_root}" &
else
  "${script_dir}/run_arborist.sh" "$@" &
fi
runner_pid=$!

echo
echo "Arborist is running."
echo "Website: ${ui_url}"
echo "Press Ctrl+C to stop both runner and website."
echo

set +e
wait -n "${ui_pid}" "${runner_pid}"
first_exit_status=$?
set -e

ui_alive=0
runner_alive=0
if kill -0 "${ui_pid}" >/dev/null 2>&1; then
  ui_alive=1
fi
if kill -0 "${runner_pid}" >/dev/null 2>&1; then
  runner_alive=1
fi

if (( ui_alive == 0 && runner_alive == 1 )); then
  echo "Arborist UI exited; stopping runner." >&2
  kill "${runner_pid}" >/dev/null 2>&1 || true
  wait "${runner_pid}" >/dev/null 2>&1 || true
  exit "${first_exit_status}"
fi

if (( ui_alive == 1 && runner_alive == 0 )); then
  echo "Arborist runner exited; stopping UI server." >&2
  kill "${ui_pid}" >/dev/null 2>&1 || true
  wait "${ui_pid}" >/dev/null 2>&1 || true
  exit "${first_exit_status}"
fi

exit "${first_exit_status}"
