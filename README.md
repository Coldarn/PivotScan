PivotScan
=========

PivotScan is a minimal desktop app for collecting images from scanners, pivoting them, and exporting them to PDFs with pickable paper sizes. It has been designed for scenarios where easily and accurately storing, transferring, and printing size-sensitive diagrams is essential.

### Goals of the App

1. Ease-of-use: no nested dialogs or menus, and no confusing, unnecessary options, just what-you-see-is-what-you-get image/PDF composition and exporting
1. Precise sizing of scanned images into PDFs for 1:1 reproductions of original documents
1. Positioning of scanned images in their generated pages


### Implementation Details
Due to availiability of usable cross-platform libraries for scanning and PDF authoring, PivotScan is implemented in Python. It uses [ImageScanner](https://github.com/Coldarn/ImageScanner) for image capture from scanners, which itself relies on TWAIN on Windows and SANE on Linux, both available via easy_install/pip. UI is implemented in [wxPython](http://wxpython.org/) for its simplicity and portability, and PDF generation is implemented in the solid [reportlab](https://pypi.python.org/pypi/reportlab).
