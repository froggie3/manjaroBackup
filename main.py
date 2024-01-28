#!/usr/bin/env python3
import sys
import textwrap


def excludeList():
    # note: exclusion in rsync allows using wildcard, but tar does not.
    return [
        "dev/*",
        "proc/*",
        "sys/*",
        "tmp/*",
        "run/*",
        "mnt/*",
        "media/*",
        ".cache/*",
        "lost+found/*",
    ]


def concatExcludeList(mode, excludeList):
    excludeList = {
        "rsync": [f"--exclude='{x}'" for x in excludeList],
        "tar": [f"--exclude='{x}'" for x in excludeList],
    }
    if mode in excludeList.keys():
        return excludeList[mode]


def getMessage(mode, SOURCE, DESTINATION):
    excludeString = concatExcludeList(mode, excludeList())
    if excludeString is None:
        print(f"error: unsuported mode. supports only 'rsync' and 'tar'")
        return None

    messages = {
        # -n equivarents to --dry-run
        "rsync": (
            "rsync", 
            *excludeString, 
            "-a", 
            "-A", 
            "-X", 
            "-H", 
            "-v", 
            "-n",
            SOURCE, 
            DESTINATION,
        ),
        #"tar": f"tar -cvpzf {DESTINATION} {excludeString} --one-file-system {SOURCE}"
        "tar": (
            'tar', 
            *excludeString, 
            '--zstd', 
            '-c', 
            '-v', 
            '-p', 
            '-f', 
            DESTINATION, 
            #'--one-file-system', 
            SOURCE,
        )
    }

    string = " ".join(messages[mode])
    print(string)


if __name__ == "__main__":
    # print(sys.argv)
    if len(sys.argv) != 4 or "--help" in sys.argv:
        print(f"usage: {sys.argv[0]} MODE SOURCE DESTINATION\n"
              "\n"
              "Description:\n"
              "  Execute this shell script on your client PC.\n"
              "  The output can be used as a boilerplate for your backup.\n"
              "\n"
              "Note:\n"
              "  if you assigned 'rsync' for MODE, you can specify remote drive for DESTINATION\n"
              "  e.g. sshuser@192.168.3.60:/path/to\n"
              "\n"
              "Examples:\n"
              f"  {sys.argv[0]} tar / /mnt/VOL1/backup.tar.gz\n"
              f"  {sys.argv[0]} rsync / /mnt/backup"
        )
        sys.exit(1)

    mode, SOURCE, DESTINATION = sys.argv[1:]
    # print(sys.argv[2:])
    getMessage(mode, SOURCE, DESTINATION)
    sys.exit(0)

