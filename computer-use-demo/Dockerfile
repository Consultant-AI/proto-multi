FROM docker.io/ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_PRIORITY=high

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends \
    # UI Requirements
    xvfb \
    xterm \
    xdotool \
    scrot \
    imagemagick \
    sudo \
    mutter \
    x11vnc \
    # Python/pyenv reqs
    build-essential \
    libssl-dev  \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    git \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    # Network tools
    net-tools \
    netcat-traditional \
    # Security tools
    nginx \
    apache2-utils \
    iptables \
    iptables-persistent \
    # Dependencies for Chrome
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2t64 \
    libatk-bridge2.0-0t64 \
    libatk1.0-0t64 \
    libatspi2.0-0 \
    libcups2t64 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0t64 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    # Dependencies for VSCode
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxshmfence1 \
    libglu1-mesa \
    # Minimal UI packages
    tint2 \
    pcmanfm \
    fonts-noto-core && \
    # Install Google Chrome x86_64 with optimizations
    wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y /tmp/google-chrome-stable_current_amd64.deb && \
    rm /tmp/google-chrome-stable_current_amd64.deb && \
    # Install VSCode
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg && \
    install -D -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg && \
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list && \
    rm -f /tmp/packages.microsoft.gpg && \
    apt-get update && \
    apt-get install -y code && \
    # Additional applications
    apt-get install -y --no-install-recommends \
    gedit \
    unzip \
    # LibreOffice suite
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-draw \
    # Docker (will be installed via script below)
    apt-transport-https \
    software-properties-common && \
    # Install Node.js 20.x LTS
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    # Install Docker
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && \
    sh /tmp/get-docker.sh && \
    rm /tmp/get-docker.sh && \
    # Clean up to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install noVNC
RUN git clone --branch v1.5.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone --branch v0.12.0 https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

# setup user
ENV USERNAME=computeruse
ENV HOME=/home/$USERNAME
RUN useradd -m -s /bin/bash -d $HOME $USERNAME && \
    usermod -aG docker $USERNAME && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER computeruse
WORKDIR $HOME

# Install Claude Code CLI
RUN curl -fsSL https://raw.githubusercontent.com/anthropics/claude-code/main/install.sh | bash

# setup python
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv && \
    cd ~/.pyenv && src/configure && make -C src && cd .. && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
ENV PYENV_ROOT="$HOME/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"
ENV PYENV_VERSION_MAJOR=3
ENV PYENV_VERSION_MINOR=11
ENV PYENV_VERSION_PATCH=6
ENV PYENV_VERSION=$PYENV_VERSION_MAJOR.$PYENV_VERSION_MINOR.$PYENV_VERSION_PATCH
RUN eval "$(pyenv init -)" && \
    pyenv install $PYENV_VERSION && \
    pyenv global $PYENV_VERSION && \
    pyenv rehash

ENV PATH="$HOME/.pyenv/shims:$HOME/.pyenv/bin:$PATH"

RUN python -m pip install --upgrade pip==23.1.2 setuptools==58.0.4 wheel==0.40.0 && \
    python -m pip config set global.disable-pip-version-check true

# only reinstall if requirements.txt changes
COPY --chown=$USERNAME:$USERNAME computer_use_demo/requirements.txt $HOME/computer_use_demo/requirements.txt
RUN python -m pip install -r $HOME/computer_use_demo/requirements.txt

# setup desktop env & app
COPY --chown=$USERNAME:$USERNAME image/ $HOME
COPY --chown=$USERNAME:$USERNAME computer_use_demo/ $HOME/computer_use_demo/

ARG DISPLAY_NUM=1
ARG HEIGHT=1080
ARG WIDTH=1920
ENV DISPLAY_NUM=$DISPLAY_NUM
ENV HEIGHT=$HEIGHT
ENV WIDTH=$WIDTH

ENTRYPOINT [ "./entrypoint.sh" ]
