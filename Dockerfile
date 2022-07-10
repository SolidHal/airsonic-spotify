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
ENV SCHEDULE_FREQUENCY=""
#one of:
#  - NOW  : Run tsar & update airsonic playlist immediately, and then exit
#  - <HH:MM> : run tsar & update airsonic playlist daily at <HH:MM> UTC
#  - DEBUG : Like "NOW" but does not automatically exit when complete

# the following directories must be provided
# AIRSONIC_LIBRARY_DIR mapped to /airsonic

# the following file must be provided
# spotipy authentication cache file mapped to "/.cache-<spotify_username>"


ENV LANG C.UTF-8

# Get Ubuntu packages
RUN apt-get update && apt-get install -y  --no-install-recommends \
    build-essential \
    curl \
    python3 \
    git \
    libasound2-dev \
    python3-pip \
    pkg-config  \
    ffmpeg


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
RUN rm -rf librespot/

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

# clean up build deps to minimize image size
RUN apt-get remove -y --purge build-essential pkg-config libasound2-dev curl && apt-get autoremove -y --purge
RUN rm -rf /var/cache/apt/archives && rm -rf /usr/share/doc && rm -rf /usr/share/man

# clean up rust
RUN rustup self uninstall -y
RUN rm -rf ~/.cargo

# Setup script lib folder
RUN mkdir -p /tool_scripts
RUN touch /tool_scripts/__init__.py

# Get tsar
RUN git clone https://github.com/SolidHal/tsar.git 
RUN cp tsar/tsar.py /tool_scripts/tsar.py
RUN rm -rf tsar/

# Get supporting scripts
COPY tool_scripts/airsonic_import.py /tool_scripts/airsonic_import.py
COPY tool_scripts/spotify_update_playlist.py /tool_scripts/spotify_update_playlist.py

# dont buffer python log output
ENV PYTHONUNBUFFERED="TRUE"

COPY docker_scripts/entrypoint.sh /entrypoint.sh
COPY docker_scripts/run.py /run.py
ENTRYPOINT ["/entrypoint.sh"]