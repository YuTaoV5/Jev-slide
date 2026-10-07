"""Interactive SSH helper for the authorized NanoJev/SGLang experiment.

Reads a password from the terminal; never records it. Each subsequent input line
is a JSON command: {"cmd": "..."}, {"put": [local, remote]}, or
{"get": [remote, local]}.
"""

import getpass
import json
import os
import sys

import paramiko


HOST = "120.209.70.195"
PORT = 30113


def main() -> None:
    client = paramiko.SSHClient()
    client.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
    client.connect(
        HOST,
        port=PORT,
        username="root",
        password=getpass.getpass("SSH password: "),
        look_for_keys=False,
        allow_agent=False,
        timeout=20,
        auth_timeout=30,
    )
    client.get_transport().set_keepalive(20)
    print("SSH_READY", flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request.get("close"):
                break
            if "cmd" in request:
                _, stdout, stderr = client.exec_command(
                    request["cmd"], timeout=request.get("timeout", 60)
                )
                print(stdout.read().decode("utf-8", "replace"), flush=True)
                print(stderr.read().decode("utf-8", "replace"), flush=True)
                print("REMOTE_EXIT", stdout.channel.recv_exit_status(), flush=True)
            elif "put" in request:
                with client.open_sftp() as sftp:
                    sftp.put(*request["put"])
                print("PUT_OK", request["put"][1], flush=True)
            elif "get" in request:
                with client.open_sftp() as sftp:
                    sftp.get(*request["get"])
                print("GET_OK", request["get"][1], flush=True)
            else:
                print("UNKNOWN_REQUEST", flush=True)
        except Exception as exc:
            print("ERROR", type(exc).__name__, str(exc), flush=True)
    client.close()


if __name__ == "__main__":
    main()
