FROM --platform=linux/amd64 debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    clang \
    binutils \
    libc6-dev \
    qemu-system-x86 \
    python3 \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Enable core dumps
RUN echo 'kernel.core_pattern=/tmp/cores/core.%e.%p' >> /etc/sysctl.conf || true
RUN mkdir -p /tmp/cores

WORKDIR /work

# Copy freestanding runtime
COPY freestanding/ /work/freestanding/

# Default: keep container alive for exec
CMD ["sleep", "infinity"]
