class InputFileDoesNotExist(Exception):
    pass


class CommandError(Exception):
    pass


class UnknownFormat(Exception):
    pass


class UnreadableFile(Exception):
    pass


class CantOverwrite(Exception):
    pass
