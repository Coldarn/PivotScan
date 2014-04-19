from distutils.core import setup
import py2exe

packages = [
    'reportlab',
    'reportlab.graphics.charts',
    'reportlab.graphics.samples',
    'reportlab.graphics.widgets',
    'reportlab.graphics.barcode',
    'reportlab.graphics',
    'reportlab.lib',
    'reportlab.pdfbase',
    'reportlab.pdfgen',
    'reportlab.platypus',
    'imagescanner.backends.twain',
]

setup(
    windows=['PivotScan.pyw'],
    data_files=[
        'PivotScan.ico',
        'RotateLeft.png',
        'Center.png',
        'RotateRight.png',
        'msvcp90.dll'
    ],
    options={
        'py2exe': { 'packages': packages },
    })
