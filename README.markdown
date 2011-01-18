#### python FFmpeg wrapper based on rVideo

*Sample usage (VideoInspector):*

    from video_inspector import VideoInspector
    video = VideoInspector("/path/to/video.mov")
    print video.duration()
    print video.fps()


*Sample usage (VideoEncoder):*

    from video_encoder import VideoEncoder
    video = VideoEncoder("/path/to/video_input.mov")
    def print_progress(por):
        print "%s%%" % por
    video.execute(
        "%(ffmpeg_bin)s -y -i %(input_file)s %(output_file)s",
        "/path/to/output.mp4",
        print_progress
    )
