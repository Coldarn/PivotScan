PivotScan
=========

PivotScan is a minimal desktop app for collecting images from scanners, pivoting them, and exporting them to PDFs with pickable paper sizes, all while maintaining their correct sizes and aspect ratios.

### The goals of the app are humble:

1. Ease-of-use: no nested dialogs or menus, and no confusing, unnecessary options, just what-you-see-is-what-you-get image/PDF composition and exporting
1. Precise sizing of scanned images into PDFs for 1:1 reproductions of original documents


### Implementation Details
Due to availiability of usable cross-platform libraries for scanning and PDF authoring, PivotScan is implemented in Python. It uses [imagescanner](https://code.google.com/p/imagescanner/) for image capture from scanners, which itself relies on several other platform-specific libraries for communications. UI is implemented in [wxPython](http://wxpython.org/) for its simplicity and portability, and PDF generation is implemented in the ubiquitous [reportlab](https://pypi.python.org/pypi/reportlab).
