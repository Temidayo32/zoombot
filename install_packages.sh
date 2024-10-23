#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install necessary system packages
echo "Installing necessary packages..."

# Packages required by some of the Python packages
sudo apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    libatlas-base-dev \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    libhdf5-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libsndfile1-dev \
    portaudio19-dev \
    libglib2.0-0 \
    libwebsocketpp-dev \
    libboost-all-dev \
    git

sudo apt update
sudo apt install wmctrl xdotool

# Clone FFmpeg repository
echo "Cloning FFmpeg repository..."
sudo git clone https://github.com/FFmpeg/FFmpeg.git /FFmpeg

# Build FFmpeg from source
echo "Building FFmpeg from source..."
cd /FFmpeg
sudo ./configure \
    --enable-gpl \
    --enable-version3 \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libvpx \
    --enable-libmp3lame \
    --enable-libopus \
    --enable-openssl \
    --enable-libpulse

# Compile and install FFmpeg
sudo make
sudo make install

# Clean up
echo "Cleaning up..."
sudo apt-get autoremove -y
sudo apt-get clean

# Indicate that all required packages have been installed
echo "All necessary packages have been installed, and FFmpeg has been built successfully!"
