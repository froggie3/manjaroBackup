# Dealing with a full backup of Linux

This article introduces how to recover from a full backup of Linux system taken with rsync or tar archive.

[TOC]

## Making backup

First, here we have a helper script written in Python: this script just generates the final command that can be used for making backup, and note it is not something that automates everything in a whole workflow. This is currently compatible with making backup on `/` directory with either `rsync` or `tar` command. 

```python
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
```

## Recover from an image file : rsync

### Setting up loop device

Raw image     | a loop device as    | Mounted as
------------- | ------------------- | ----------
`manjaro.img` | `/dev/loop0`        | `/mnt/foo`

Get root privileges:

```shell
su -
```

Download the latest disk image from SSH:

```shell
mkdir /mnt/imglatest
rsync -rvn foo@bar:/path/to/src/manjaro.img.gz /mnt/imglatest
```

Set up loop device from a disk image:

```shell
cd /mnt/imglatest
gzip manjaro.img.gz
losetup /dev/loop0 ./manjaro.img 
```

Mount loop device into a specified directory:

```shell
mkdir /mnt/foo
mount -t btrfs /dev/loop0 /mnt/foo
```


### Environment

Target     | The directory to be `chroot` ed
---------- | -------------------------------
`/mnt/var` | `/`

!!! note Before you execute all the commands below
    * You need to make EFI  System Partition if you're trying UEFI boot! (<https://wiki.archlinux.org/title/EFI_system_partition>)
    * You need to assure the backups to have a valid root directory structure excluding critical directories (e.g. `sys`, `proc`, `dev`, and etc.)

## Recovery from a TAR archive

We are introducing how to recover the system from a full-backup taken with TAR archive.

### Extract directory on to `/` directory
```bash
tar -xvf /backup.tar.gz
```

*Continues to "next step" ...*

## Common procedures to recover

Before you start recovery, you are responsive for establishing the `chroot` ed shell in the newly migrated filesystem in a live CD or live DVD environment, so in this part we gonna explain how to deal with them. By the way all the command in here are intended to be executed as a root user. As always, be careful!

```shell
sudo su -
```

### Making / formatting partitions

You need at least two partitions to boot UEFI systems:

* ESP Partition (e.g. `/boot/efi` or just `/boot` directory)
	* **You must add `EFI System` flag on this partition**, otherwise the system never boots
* The partition for the `/` directory

I prefer to using `fdisk` command when it comes to making partitions, but you can use other way (e.g. `parted`): 

```shell
# Add and edit partitions
fdisk /dev/sdx
```

Formatting a filesystem by each partition is also necessary, after you split the partitions:

```shell
# Format the partition for `/boot` :
mkfs.fat -F 32 /dev/sdxY

# Format the partition for `/` :
mkfs.btrfs /dev/sdxY
```


!!!note Example
		If you split the partitions in the aforementioned way, the complete detail can be like this:

```plain
# fdisk -l /dev/sda
Disk /dev/sda: 127 GiB, 136365211648 bytes, 266338304 sectors
Disk model: Virtual Disk    
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: C6724339-932F-AF48-8C88-55B50E884E5A

Device       Start       End   Sectors   Size Type
/dev/sda1     2048   1128447   1126400   550M EFI System
/dev/sda2  1128448 266336255 265207808 126.5G Linux filesystem
```

### Mount required directories

Now all you have to do is mount two of them by typing this command.

```shell
# Make directory for two partitions to be mounted
mkdir /mnt/foo; mkdir /mnt/foo/boot
```

```shell
# Mount directory from the block device (sdXn should be replaced)
mount /dev/sdX1 /mnt/foo/boot; mount /dev/sdX2 /mnt/foo
```

---
You need to bind other directories into the directory to be `chroot` ed as well as ESP partition and `/`. Normally these folder is unpopulated but when the operating system starts, then they gets populated.

```shell
# Bind other directories into '/'
for i in /dev /dev/pts /proc /sys /run; do sudo mount -B $i /mnt/foo$i; done
```

You need to bind EFI Variable to the directory `/mnt/foo/sys/firmware/efi/efivars` so that system can read these values when it generates GRUB menu.

```shell
# Bind EFI Variables
mount -t efivarfs efivarfs /mnt/foo/sys/firmware/efi/efivars
```

!!!warning Preparing EFI Variable for newly installed Linux
    Check patterns below is what can be used to check if EFI Variable is available on your system. You need to try `modprobe efivarfs` by enabling the kernel module required, in case none of them work.
    * `ls /mnt/foo/sys/firmware/efi/efivars`
    * `df -la | grep efivars`
    * `efibootmgr`

After all, you will change root by this.

```bash
chroot /mnt/foo /bin/bash
```

## Installing Boot Loader

not working: just displays grub selection menu 

```bash
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
```

```bash
# Reinstall GRUB
paru -Syu grub
```

```bash
grub-mkconfig -o /boot/grub/grub.cfg
```


## Unmounting working directory

Just to make sure you should check what is subject to be unmounted, before you unmount and modify the command below (if you need)

```shell
# Make sure to check what is currently mounted
df -a | grep /mnt/foo*
```

```shell
# if everything's fine ...
for i in /boot /dev/pts /dev /proc /sys/firmware/efi/efivars /sys /run /; do sudo umount /mnt/foo$i; done
```


## References

* <https://wiki.archlinux.org/title/EFI_system_partition>
* <https://help.ubuntu.com/community/BackupYourSystem/TAR>
* <https://wiki.archlinux.org/title/GRUB>
* <https://bbs.archlinux.org/viewtopic.php?id=249546>
* <https://unix.stackexchange.com/a/418913>
