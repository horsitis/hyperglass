"""CLI utility functions."""
# Third Party Imports
import click

# Project Imports
from cli.echo import error
from cli.echo import info
from cli.echo import status
from cli.echo import success
from cli.static import CL
from cli.static import NL
from cli.static import WS
from cli.static import E


def async_command(func):
    """Decororator for to make async functions runable from syncronous code."""
    import asyncio
    from functools import update_wrapper

    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


def fix_ownership(user, group, directory):
    """Make user & group the owner of the directory."""
    import grp
    import pwd
    import os

    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    try:
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                full_path = os.path.join(root, d)
                os.chown(full_path, uid, gid)
            for f in files:
                full_path = os.path.join(root, f)
                os.chown(full_path, uid, gid)
            os.chown(root, uid, gid)
    except Exception as e:
        error("Failed to change 'hyperglass/' ownership", e)

    success("Successfully changed 'hyperglass/' ownership")


def fix_permissions(directory):
    """Make directory readable by public."""
    import os

    try:
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                full_path = os.path.join(root, d)
                os.chmod(full_path, 0o744)
            for f in files:
                full_path = os.path.join(root, f)
                os.chmod(full_path, 0o744)
            os.chmod(root, 0o744)
    except Exception as e:
        error("Failed to change 'hyperglass/' permissions", e)

    success("Successfully changed 'hyperglass/' permissions")


def start_web_server(start, params):
    """Start web server."""
    msg_start = "Starting hyperglass web server on"
    msg_uri = "http://"
    msg_host = str(params["host"])
    msg_port = str(params["port"])
    msg_len = len("".join([msg_start, WS[1], msg_uri, msg_host, CL[1], msg_port]))
    try:
        click.echo(
            NL[1]
            + WS[msg_len + 8]
            + E.ROCKET
            + NL[1]
            + E.CHECK
            + click.style(msg_start, fg="green", bold=True)
            + WS[1]
            + click.style(msg_uri, fg="white")
            + click.style(msg_host, fg="blue", bold=True)
            + click.style(CL[1], fg="white")
            + click.style(msg_port, fg="magenta", bold=True)
            + WS[1]
            + E.ROCKET
            + NL[1]
            + WS[1]
            + NL[1]
        )
        start()

    except Exception as e:
        error("Failed to start test server", e)


def migrate_config(config_dir):
    """Copy example config files and remove .example extensions."""
    status("Migrating example config files...")

    import os
    import glob
    import shutil

    examples = glob.iglob(os.path.join(config_dir, "*.example"))

    for file in examples:
        basefile, extension = os.path.splitext(file)
        try:
            if os.path.exists(basefile):
                info(f"{basefile} already exists")
            else:
                shutil.copyfile(file, basefile)
                success(f"Migrated {basefile}")
        except Exception as e:
            error(f"Failed to migrate {basefile}", e)

    success("Successfully migrated example config files")


def migrate_systemd(source, destination):
    """Copy example systemd service file to /etc/systemd/system/."""
    import os
    import shutil

    basefile, extension = os.path.splitext(source)
    newfile = os.path.join(destination, basefile)

    try:
        status("Migrating example systemd service...")

        if os.path.exists(newfile):
            info(f"{newfile} already exists")
        else:
            shutil.copyfile(source, newfile)

    except Exception as e:
        error("Error migrating example systemd service", e)

    success(f"Successfully migrated systemd service to: {newfile}")