FROM python:3.10-slim

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    git \
    curl \
    less \
    vim \
    procps \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install MySQL client for database interaction
RUN apt-get update && apt-get install -y mariadb-client

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install pylint pylint-django black autopep8

# Copy requirements and install them
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Create working directory
WORKDIR /workspace

# Set the default user
USER $USERNAME 