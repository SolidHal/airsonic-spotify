# syntax=docker/dockerfile:1
FROM ubuntu:latest


# TODO determine how to take/use PGID and PUID
# - likely need to chown things?

# the following envars must be set
# SPOTIFY_USERNAME
# SPOTIFY_PASSWORD
# SPOTIPY_CLIENT_ID
# SPOTIPY_CLIENT_SECRET
# SPOTIPY_REDIRECT_URI
# SPOTIFY_PLAYLIST_URI
# AIRSONIC_USERNAME
# AIRSONIC_PASSWORD

# the following directories must be provided
# AIRSONIC_LIBRARY_DIR
# TEMPORARY_IMPORT_DIR

# the following file must be provided
# spotipy authentication cache file


ENV LANG C.UTF-8

# Update default packages
RUN apt-get update

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl \
    python3 \
    git \
    libasound2-dev \
    python3-pip \
    pkg-config

# Update new packages
RUN apt-get update

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

# Get supporting scripts
COPY airsonic-import.py /usr/bin/airsonic-import.py
COPY spotify-update-playlist.py /usr/bin/spotify-update-playlist.py

# Get python packages
RUN pip3 install \
    py-sonic \
    click \
    eyed3 \
    spotipy \
    schedule

# TODO write entry script