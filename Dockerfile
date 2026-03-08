FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://foundry.paradigm.xyz | bash \
    && . $HOME/.bashrc \
    && foundryup

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Decentralized Voting Platform"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

COPY --from=builder /root/.foundry /root/.foundry
ENV PATH="/root/.foundry/bin:$PATH"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    RPC_URL=http://localhost:8545 \
    ANVIL_PORT=8545 \
    BACKEND_DIR=/app/backend \
    FOUNDRY_DIR=/app/voting-foundry \
    BUILD_DIR=/app/build

EXPOSE 8000 8545

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

COPY Taskfile.yml /usr/local/bin/taskfile
RUN chmod +x /usr/local/bin/taskfile

CMD ["task", "start"]
