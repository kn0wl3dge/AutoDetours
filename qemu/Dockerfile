FROM debian:bullseye-slim

RUN apt-get update && apt-get -y upgrade && \
    apt-get --no-install-recommends -y install \
        qemu-system-x86 \
    && apt-get clean

RUN mkdir /image

ENTRYPOINT ["qemu-system-i386", "-nographic", "-m", "1024","-loadvm", "agent", "-enable-kvm"]
