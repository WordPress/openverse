FROM docker.io/library/fedora:40

# We need Python available for basic bootstrapping. All other packages
# should be defined
RUN dnf install -y python3.12

# Define environment variables in here that will affect the PATH
# Otherwise they cannot be expanded referring to the existing PATH
# Generally, it's easier to maintain environment variables defined
# in run.sh because it doesn't require rebuilding (and recreating the
# container environment) to update them

# Set HOME to /opt so XDG-respecting utilities automatically use it
# without additional configuration
# This gets chmodded with wide open permissions, so that
# on Linux hosts, the explicitly passed user (with docker group)
# is able to read/write from here, as well as the root user used by
# macOS hosts (who don't have Docker permissions or host filesystem
# permissions issues to contend with and as such run the container as root)
ENV HOME="/opt"

# location where PDM installs Python interpreters
ENV PDM_PYTHONS="${HOME}/pdm/bin"
# location where `n` installs Node.js versions
ENV N_PREFIX="${HOME}/n"

# Add tooling installed in custom locations to `PATH`.
ENV PATH="${N_PREFIX}/bin:${PDM_PYTHONS}:${HOME}/.local/bin:${PATH}"

# The fedora container's default entrypoint + command behaviour is to keep running
# so we do not need to modify entrypoint and command to use the container as a
# persistent environment.
