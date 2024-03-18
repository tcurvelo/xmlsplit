# xmlsplit

Cli utility for spliting a big XML file into smaller parts.

The breakpoint will be the element of depth one (below root) that does not
fit in the specified maximum size. Each part created will have the same
root element.

Usage:

    xmsplit size prefix [filename]

Eg:

    xmlsplit 1000000 part_ mydata.xml

or:

    cat mydata.xml | xmlsplit 1000000 part_