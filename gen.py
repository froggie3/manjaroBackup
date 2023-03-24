#!/bin/python3
import textwrap

# Execute this shell script on your client PC!

# for 'rsync' in DESTINATION it can be something like a preset name as well
# e.g. "sshuser@192.168.3.60:/path/to"

SOURCE = "/"

DESTINATION = {
    "rsync": "/mnt/backup",
    "tar": "/mnt/VOL1/backup.tar.gz"
}

mode = "tar" # or "rsync"

# todo: exclusion in rsync allows using wildcard, but tar does not.
excludeList = [
    #"/" + DESTINATION["tar"],
    "/dev/*",
    "/proc/*",
    "/sys/*",
    "/tmp/*",
    "/run/*",
    "/mnt/*",
    "/media/*",
    "/home/*/.cache",
    "/lost+found"
]

rsyncExcludeString = "".join(["--exclude ", "{", ",".join(excludeList), "}"])
tarExcludeString = " ".join(["--exclude \"" + x + "\"" for x in excludeList])

if mode == "rsync":
    # -n equivarents to --dry-run
    message = textwrap.dedent(f"""\
        # To make backup through rsync, copy this line and then paste into your terminal.
        rsync -aAXHvn {SOURCE} {rsyncExcludeString} {DESTINATION['rsync']} \
        """)
elif mode == "tar":
    message = textwrap.dedent(f"""\
        # To make a tar.gz archive, use this:
        cd {SOURCE}
        tar -cvpzf {DESTINATION['tar']} {tarExcludeString} --one-file-system {SOURCE} \
        """)
else:
    message = textwrap.dedent(f"""\
        Sorry to bother you, but there seems to be nothing to show you. \
        """)

print(message)