# syntax=docker/dockerfile:1
FROM ubuntu:latest


# TODO determine how to take/use PGID and PUID
# - likely need to chown things?

# the following envars must be set
ENV PUID=""
ENV PGID=""
ENV SPOTIFY_USERNAME=""
ENV SPOTIFY_PASSWORD=""
ENV SPOTIPY_CLIENT_ID=""
ENV SPOTIPY_CLIENT_SECRET=""
ENV SPOTIPY_REDIRECT_URI=""
ENV SPOTIFY_PLAYLIST_URI=""
ENV AIRSONIC_USERNAME=""
ENV AIRSONIC_PASSWORD=""
ENV AIRSONIC_SERVER=""
ENV AIRSONIC_PORT=""

# the following directories must be provided
# AIRSONIC_LIBRARY_DIR mapped to /airsonic

# the following file must be provided
# spotipy authentication cache file mapped to "/.cache-<spotify_username>"


ENV LANG C.UTF-8

# Get Ubuntu packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3 \
    git \
    libasound2-dev \
    python3-pip \
    pkg-config  \
    ffmpeg


RUN apt-get autoremove --purge

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

# include rust in the path
ENV PATH="/root/.cargo/bin:${PATH}"


# Check cargo is visible
RUN cargo --help


# Get librespot
# TODO switch to upstream librespot once PR has merged
RUN git clone https://github.com/SolidHal/librespot.git
RUN cd librespot && cargo build --release
RUN cp librespot/target/release/librespot /usr/bin/librespot
RUN librespot --version

# Get tsar
RUN git clone https://github.com/SolidHal/tsar.git
RUN cp tsar/tsar.py /usr/bin/tsar.py

# Get python packages
RUN pip3 install \
    py-sonic \
    click \
    eyed3 \
    spotipy \
    schedule

# create the user and group
RUN useradd -u 911 -U -d /config -s /bin/false abc
RUN usermod -G users abc
RUN mkdir -p /config

# set timezone
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Chicago /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
ENV TZ="America/Chicago"

# Get supporting scripts
COPY tool_scripts/airsonic_import.py /usr/bin/airsonic_import.py
COPY tool_scripts/spotify_update_playlist.py /usr/bin/spotify_update_playlist.py

# dont buffer python log output
ENV PYTHONUNBUFFERED="TRUE"

COPY docker_scripts/entrypoint.sh /entrypoint.sh
COPY docker_scripts/run.py /run.py
ENTRYPOINT ["/entrypoint.sh"]