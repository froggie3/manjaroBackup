#!/usr/bin/env python3
from typing import Tuple
import sys


def exclude_list() -> Tuple[str]:
    return (
        "dev/*",
        "proc/*",
        "sys/*",
        "tmp/*",
        "run/*",
        "mnt/*",
        "media/*",
        ".cache/*",
        "lost+found/*",
    )


def concat_exclude_list(command_type: str, excludes: Tuple[str]) -> Tuple[str] | None:
    exclude_args_by_command_type = {
        "rsync": tuple(f"--exclude='{x}'" for x in excludes),
        "tar": tuple(f"--exclude='{x}'" for x in excludes),
    }
    if command_type not in exclude_args_by_command_type.keys():
        return None

    return exclude_args_by_command_type[command_type]


def get_args(command_type, src: str, dest: str) -> Tuple[str] | None:
    exclude_string = concat_exclude_list(command_type, exclude_list())
    if exclude_string is None:
        print("error: unsuported mode. supports only 'rsync' and 'tar'")
        return None

    args_by_command_type = {
        # -n equivarents to --dry-run
        "rsync": (
            "rsync",
            *exclude_string,
            "-a",
            "-A",
            "-X",
            "-H",
            "-v",
            "-n",
            src,
            dest,
        ),
        # "tar": f"tar -cvpzf {DESTINATION} {excludeString} --one-file-system {SOURCE}"
        "tar": (
            'tar',
            *exclude_string,
            '--zstd',
            '-c',
            '-v',
            '-p',
            '-f',
            dest,
            # '--one-file-system',
            src,
        )
    }
    return args_by_command_type[command_type]


def show_args(last_args: Tuple[str]) -> None:
    string = " ".join(last_args)
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

    mode, source, destination = sys.argv[1:]
    # print(sys.argv[2:])
    args = get_args(mode, source, destination)
    show_args(args)

    sys.exit(0)
