# media tools

## About

This is basically a wrapper script for `ffmpeg` that I use regularly, mostly to quickly edit dog photos and videos... no seriously.

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

## Installation

_Technically_ this is all portable Python but I only really care about Windows, therefore there's a simple `build.bat` script that will build the script into a single `media-tool.exe`. It just assumes you have the default Python for Windows installation setup. Also assumes you have `ffmpeg.exe` and `ffprobe.exe` somewhere in your `%PATH%`.

For development/direct use, the script supports [`uv`](https://github.com/astral-sh/uv) via its inline script metadata — just run `uv run media-tool.py <command>`.
