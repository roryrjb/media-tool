# media tools

## About

This is basically a wrapper script for `ffmpeg` that I use regularly, mostly to quickly edit dog photos and videos... no seriously.

This script has been written for and only tested on Windows with an NVIDIA GPU.

__Commands:__

* `media-tool clipify` - Reduce framerate by half if over 45fps (NVENC)
* `media-tool convert` - Convert video container format (stream copy)
* `media-tool cut` - Cut/trim video between start and end times (NVENC)
* `media-tool gif` - Convert video segment to optimized GIF
* `media-tool reencode` - Re-encode video using NVENC H.264
* `media-tool resize` - Resize video to specified height (NVENC, CUDA)
* `media-tool silence` - Remove audio track from video
* `media-tool slomo` - Create slow motion video (NVENC)

All commands support `--help` for usage details.

## Requirements

* `ffmpeg.exe` and `ffprobe.exe` in your `%PATH%`

## Build

Run `build.bat` to build into a single `media-tool.exe`. Requires [uv](https://docs.astral.sh/uv/).
