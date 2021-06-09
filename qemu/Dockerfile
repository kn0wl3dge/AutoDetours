FROM archlinux:latest

RUN pacman -Syyu --noconfirm && \
    pacman -S qemu-arch-extra qemu --noconfirm

RUN mkdir /image

ENTRYPOINT ["qemu-system-i386"]
