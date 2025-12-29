FROM jenkins/jenkins:lts-jdk17

USER root

# Install docker cli
RUN apt-get update && \
    apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release && \
    curl -fsSL https://get.docker.com | sh

# Install docker compose plugin
RUN mkdir -p /usr/local/lib/docker/cli-plugins && \
    curl -SL https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64 \
    -o /usr/local/lib/docker/cli-plugins/docker-compose && \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Add jenkins user to docker group
RUN usermod -aG docker jenkins

USER jenkins
