#!/usr/bin/env python3
"""
xmlsplit - split a XML file into pieces

The breakpoint will be the element of depth one (below root) that does not
fit in the specified maximum size. Each part created will have the same
root element.

Usage:
    $ xmlsplit size prefix [filename]
"""

from xml.sax import saxutils, handler, make_parser
import sys


class SplitterContentHandler(handler.ContentHandler):
    def __init__(self, size, prefix):
        handler.ContentHandler.__init__(self)

        self._size = size
        self._prefix = prefix

        self._buffer(clean=True)
        self._part = 1
        self._out = open("{}{}.xml".format(self._prefix, self._part), "w")
        self._current_size = 0

        self._out_encoding = "utf-8"
        self._xml_declaration = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        )

        # root node will be at depth 0
        self._depth = -1
        self._root_tag = None
        self._end_tag = None

    def _buffer(self, text="", clean=False):
        self.__buffer = "" if clean else self.__buffer + text
        return self.__buffer

    def _write(self, text=None):
        if not text:
            text = self._buffer()
        self._current_size += len(text.encode(self._out_encoding))
        self._out.write(text)

    def _fits_buffer(self):
        total_required = (
            self._current_size
            + len(self._buffer().encode(self._out_encoding))
            + len(self._end_tag.encode(self._out_encoding))
        )
        return total_required < self._size

    def _rotate(self):
        self._write(self._end_tag)
        self._out.close()

        self._part += 1
        self._out = open("{}{}.xml".format(self._prefix, self._part), "w")

        self._current_size = 0
        self.startDocument()
        self._write(self._root_tag)

    def startDocument(self):
        self._write(self._xml_declaration)

    def startElement(self, name, attrs):
        self._depth += 1
        attributes = "".join(
            [
                ' {}="{}"'.format(name, saxutils.escape(value))
                for (name, value) in attrs.items()
            ]
        )
        tag = "<{}{}>".format(name, attributes)

        if self._depth == 0:  # root
            self._root_tag = tag
            self._end_tag = "</{}>".format(name)

        self._buffer(tag)

    def endElement(self, name):
        self._buffer("</{}>".format(name))
        if self._depth == 1:
            if not self._fits_buffer():
                self._rotate()
            self._write()
            self._buffer(clean=True)
        self._depth -= 1

    def endDocument(self):
        self._write()

    def characters(self, content):
        self._buffer(saxutils.escape(content))

    def ignorableWhitespace(self, content):
        self._buffer(content)

    def processingInstruction(self, target, data):
        self._buffer("<?{} {}?>".format(target, data))


def split(size, prefix, filename):
    size = int(size)

    parser = make_parser()
    parser.setContentHandler(SplitterContentHandler(size, prefix))
    parser.parse(filename)


def main():
    size = sys.argv[1]
    prefix = sys.argv[2]
    filename = sys.argv[3] if len(sys.argv) > 3 else sys.stdin
    split(size, prefix, filename)


if __name__ == "__main__":
    main()
