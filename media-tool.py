import sys
import argparse
from os import path
import ffmpeg
from datetime import datetime

TIME_FORMAT = "%H:%M:%S"
DEFAULT_SCALE_RESIZE = 640
DEFAULT_SCALE_GIF = 320


def time_validator(input_str: str):
    datetime.strptime(input_str, TIME_FORMAT)
    return input_str


def get_video_fps(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream:
        if "avg_frame_rate" in video_stream:
            numerator, denominator = video_stream["avg_frame_rate"].split("/")
            fps = float(numerator) / float(denominator)
            return fps
        elif "r_frame_rate" in video_stream:
            numerator, denominator = video_stream["r_frame_rate"].split("/")
            fps = float(numerator) / float(denominator)
            return fps
    return None


def change_video_fps(input_path, output_path, target_fps):
    stream = ffmpeg.input(input_path, hwaccel="cuda")
    stream = ffmpeg.output(
        stream,
        output_path,
        r=target_fps,
        vcodec="h264_nvenc",
        preset="p2",
        cq=23,
        acodec="copy",
    )
    ffmpeg.run(stream, overwrite_output=True)


def cmd_clipify(args):
    (name, ext) = path.splitext(args.filename)
    out = f"{name}-clip{ext}"
    original_framerate = get_video_fps(args.filename)
    if original_framerate > 45:
        new_framerate = original_framerate / 2
        change_video_fps(args.filename, out, new_framerate)


def cmd_convert(args):
    for filename in args.filenames:
        (name, _) = path.splitext(filename)
        out = f"{name}.{args.extension}"
        cmd = ffmpeg.input(filename).output(
            out,
            acodec="copy",
            vcodec="copy",
        )
        print(" ".join(cmd.compile()))
        if args.dry_run:
            continue
        cmd.run()


def cmd_cut(args):
    (name, ext) = path.splitext(args.filename)
    out = args.name if args.name else f"{name}-cut{ext}"
    cmd = ffmpeg.input(args.filename, ss=args.start, to=args.end).output(
        out,
        vcodec="h264_nvenc",
        preset="p2",
        cq=23,
        acodec="copy",
    )
    print(" ".join(cmd.compile()))
    if args.dry_run:
        sys.exit(0)
    cmd.run()


def cmd_gif(args):
    (name, _) = path.splitext(args.filename)
    out = args.name if args.name else f"{name}.gif"
    cmd = ffmpeg.input(args.filename, ss=args.start, to=args.end).output(
        out,
        vf=f"scale={args.scale}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse,fps={args.fps}",
    )
    print(" ".join(cmd.compile()))
    cmd.run()


def cmd_reencode(args):
    for filename in args.filenames:
        (name, ext) = path.splitext(filename)
        out = args.name if args.name else f"{name}-reencoded{ext}"
        cmd = ffmpeg.input(filename, hwaccel="cuda").output(
            out,
            vcodec="h264_nvenc",
            preset="p2",
            cq=23,
            acodec="copy" if not args.reencode_audio else "aac",
        )
        print(" ".join(cmd.compile()))
        if args.dry_run:
            continue
        cmd.run()


def cmd_remove_audio(args):
    (name, ext) = path.splitext(args.filename)
    out = args.name if args.name else f"{name}-noaudio{ext}"
    cmd = ffmpeg.input(args.filename).output(
        out,
        an=None,
        vcodec="copy",
    )
    print(" ".join(cmd.compile()))
    cmd.run()


def cmd_resize(args):
    (name, ext) = path.splitext(args.filename)
    out = f"{name}-resized{ext}"
    cmd = ffmpeg.input(
        args.filename, hwaccel="cuda", hwaccel_output_format="cuda"
    ).output(
        out,
        vf=f"scale_cuda=-1:{args.scale}:interp_algo=lanczos",
        vcodec="h264_nvenc",
        preset="p2",
        cq=23,
        acodec="copy",
    )
    print(" ".join(cmd.compile()))
    if args.dry_run:
        sys.exit(0)
    cmd.run()


def cmd_slomo(args):
    (name, ext) = path.splitext(args.filename)
    out = args.name if args.name else f"{name}-slow{ext}"
    factor = args.rate_in / args.rate_out
    cmd = ffmpeg.input(args.filename, hwaccel="cuda").output(
        out,
        vf=f"setpts={factor}*PTS",
        r="30",
        vcodec="h264_nvenc",
        preset="p2",
        cq=23,
        acodec="copy",
    )
    print(" ".join(cmd.compile()))
    if args.dry_run:
        sys.exit(0)
    cmd.run()


def main():
    parser = argparse.ArgumentParser(description="Unified ffmpeg video processing tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    # clipify subcommand
    parser_clipify = subparsers.add_parser(
        "clipify", help="Reduce framerate if over 45fps"
    )
    parser_clipify.add_argument("filename", type=str)
    # convert subcommand
    parser_convert = subparsers.add_parser(
        "convert", help="Convert video container format"
    )
    parser_convert.add_argument("filenames", type=str, nargs="+")
    parser_convert.add_argument("--extension", "-e", type=str, default="mkv")
    parser_convert.add_argument(
        "--dry-run",
        help="simulate actions without touching filesystem",
        action="store_true",
    )
    # cut subcommand
    parser_cut = subparsers.add_parser(
        "cut", help="Cut/trim video between start and end times"
    )
    parser_cut.add_argument("filename", type=str)
    parser_cut.add_argument("--start", type=time_validator, default="00:00:00")
    parser_cut.add_argument("--end", type=time_validator, default="23:59:59")
    parser_cut.add_argument("--name", type=str)
    parser_cut.add_argument(
        "--dry-run",
        help="simulate actions without touching filesystem",
        action="store_true",
    )
    # gif subcommand
    parser_gif = subparsers.add_parser(
        "gif", help="Convert video segment to optimized GIF"
    )
    parser_gif.add_argument("filename", type=str)
    parser_gif.add_argument("--start", type=time_validator, default="00:00:00")
    parser_gif.add_argument("--end", type=time_validator, default="23:59:59")
    parser_gif.add_argument("--fps", "-f", type=int, default=10)
    parser_gif.add_argument("--scale", type=int, default=DEFAULT_SCALE_GIF)
    parser_gif.add_argument("--name", type=str)
    # reencode subcommand
    parser_reencode = subparsers.add_parser(
        "reencode", help="Re-encode video using NVENC H.264"
    )
    parser_reencode.add_argument("filenames", type=str, nargs="+")
    parser_reencode.add_argument(
        "--reencode-audio",
        action="store_true",
        help="Re-encode audio to AAC (default: copy audio)",
    )
    parser_reencode.add_argument("--name", type=str)
    parser_reencode.add_argument(
        "--dry-run",
        help="simulate actions without touching filesystem",
        action="store_true",
    )
    # remove-audio subcommand
    parser_remove_audio = subparsers.add_parser(
        "silence", help="Remove audio track from video"
    )
    parser_remove_audio.add_argument("filename", type=str)
    parser_remove_audio.add_argument("--name", type=str)
    # resize subcommand
    parser_resize = subparsers.add_parser(
        "resize", help="Resize video to specified width"
    )
    parser_resize.add_argument("filename", type=str)
    parser_resize.add_argument("--scale", type=int, default=DEFAULT_SCALE_RESIZE)
    parser_resize.add_argument(
        "--dry-run",
        help="Simulate actions without touching filesystem",
        action="store_true",
    )
    # slomo subcommand
    parser_slomo = subparsers.add_parser("slomo", help="Create slow motion video")
    parser_slomo.add_argument("filename", type=str)
    parser_slomo.add_argument("--rate-in", type=int, required=True)
    parser_slomo.add_argument("--rate-out", type=int, default=30)
    parser_slomo.add_argument("--name", type=str)
    parser_slomo.add_argument(
        "--dry-run",
        help="simulate actions without touching filesystem",
        action="store_true",
    )
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    # Dispatch to appropriate function
    command_map = {
        "clipify": cmd_clipify,
        "convert": cmd_convert,
        "cut": cmd_cut,
        "gif": cmd_gif,
        "reencode": cmd_reencode,
        "silence": cmd_remove_audio,
        "resize": cmd_resize,
        "slomo": cmd_slomo,
    }
    command_map[args.command](args)


if __name__ == "__main__":
    main()
