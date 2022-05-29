from typing import Generator
import keyboard
import magic
import argparse


def keyboard_interrupt(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            quit()
    return inner


class Catp:
    def __init__(self, filename, chunk_size=1024) -> None:
        self._chunk_size = chunk_size

        # Get encoding
        try:
            blobf = open(file=filename, mode='rb')
        except FileNotFoundError:
            print("File not found!")
            quit()
        blob = blobf.read(24)
        m = magic.Magic(mime_encoding=True)
        self._encoding = m.from_buffer(blob)
        blobf.close()

        self.file_obj = open(file=filename, mode='r',
                             encoding=self._encoding)

    @property
    def encoding(self) -> str:
        return self._encoding

    def _chunks(self) -> Generator:
        # Returs a generator containing the text
        while True:
            data = self.file_obj.read(self._chunk_size)
            if not data:
                break
            yield data

    @keyboard_interrupt
    def _print_chunk(self) -> None:
        for ch in self._chunks():
            keyboard.wait('enter')
            print(ch)

    def print_chunks(self, line_nums=False, show_ends=False) -> None:
        try:
            Catp.line_number
        except AttributeError:
            Catp.line_number = 1
        line_number_str = f"{Catp.line_number} " if line_nums else ''
        for ch in self._chunks():
            for _line in ch.split('\n'):
                show_end = ' $' if show_ends else ''
                print(f"{line_number_str}{_line}{show_end}")
                if line_nums:
                    Catp.line_number += 1
                    line_number_str = f"{Catp.line_number} "
                else:
                    line_number_str = ''

    def __del__(self) -> None:
        if hasattr(self, "file_obj"):
            self.file_obj.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Partial implementation of cat command in Python')

    parser.add_argument("-n", "--number", action="store_true",
                        help="Add line numbers at the beginning of each line")

    parser.add_argument("-E", "--show-ends", action="store_true",
                        help="Add dollar sign at the end of each line")

    parser.add_argument('file', type=str, nargs="+",
                        help="Takes file(s) as input")

    args = parser.parse_args()
    show_ends = args.show_ends
    line_nums = args.number

    for _file in args.file:
        c = Catp(_file)
        c.print_chunks(line_nums=line_nums, show_ends=show_ends)
