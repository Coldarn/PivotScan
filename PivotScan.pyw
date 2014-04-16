
# Dependencies:
#
# python-cjson - http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-cjson
# twain - https://pypi.python.org/pypi/twain/
# pip install python-imagescanner
# pip install reportlab
# wxpython - http://www.wxpython.org/download.php#msw
#

import os, datetime, wx
from imagescanner import ImageScanner

os.chdir(os.path.dirname(__file__))

SKIP_SCAN = True
SAVE_DIR = os.path.join(os.environ['APPDATA'], 'PivotScan')

WINDOW_SIZE = (700, 800)
IMAGE_SIZE = WINDOW_SIZE[0] - 40
SCAN_DPI = 200
PAPER_SIZES = {
    'Letter': (8.5, 11),
    'Legal': (8.5, 14),
    'Ledger': (11, 17),
}


iscan = ImageScanner()
scanners = iscan.list_scanners()
scannerNames = ['Scanner 1', 'Larger Scanner Name 2'] if SKIP_SCAN else [s.name for s in scanners]

class ImagePanel(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.pendingRepaint = False
        self.imagePanel = None
        self.paperPicker = None

        self.Parent.Bind(wx.EVT_IDLE, self.OnIdle)

    def OnResize(self, evt):
        if self.imagePanel:
            self.pendingRepaint = True

    def OnIdle(self, evt):
        if self.pendingRepaint:
            self.Parent.Layout()
            self.RefreshBitmap()
            self.pendingRepaint = False

    def RefreshBitmap(self):
        oldSize = self.image.GetSize()
        windowSize = (self.imagePanel.GetSize()[0] - 40, self.imagePanel.GetSize()[1] - 40)
        scale = min(windowSize[0] / float(oldSize[0]), windowSize[1] / float(oldSize[1]))
        newSize = (oldSize[0] * scale, oldSize[1] * scale)

        bitmap = self.image.Scale(newSize[0], newSize[1], wx.IMAGE_QUALITY_HIGH).ConvertToBitmap();
        self.imagePanel.DestroyChildren()
        imgControl = wx.StaticBitmap(self.imagePanel, bitmap=bitmap)
        imgControl.SetPosition((windowSize[0] / 2 - newSize[0] / 2 + 20, windowSize[1] / 2 - newSize[1] / 2 + 20))
        self.Parent.Layout()

    def SetImage(self, imgPath):
        if not self.imagePanel:
            controlsPanel = wx.Window(self, size=(WINDOW_SIZE[0], 50))

            controlsSizer = wx.BoxSizer()
            controlsSizer.AddStretchSpacer()
            
            controlsSizer.Add(wx.StaticText(controlsPanel, label='Paper Size'), flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer((10, 50))

            self.paperPicker = wx.ComboBox(controlsPanel, style=wx.CB_DROPDOWN | wx.CB_READONLY, choices=[n for n in PAPER_SIZES])
            controlsSizer.Add(self.paperPicker, flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(10)


            rotateLeftButton = wx.Button(controlsPanel)
            rotateLeftButton.SetBitmap(wx.Bitmap('RotateLeft.png'))
            self.Bind(wx.EVT_BUTTON, lambda _: self.Rotate(False), rotateLeftButton)
            controlsSizer.Add(rotateLeftButton, flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(10)

            rotateRightButton = wx.Button(controlsPanel)
            rotateRightButton.SetBitmap(wx.Bitmap('RotateRight.png'))
            self.Bind(wx.EVT_BUTTON, lambda _: self.Rotate(True), rotateRightButton)
            controlsSizer.Add(rotateRightButton, flag=wx.ALIGN_CENTER)
            controlsSizer.AddStretchSpacer()

            controlsPanel.SetSizer(controlsSizer)

            self.imagePanel = wx.Window(self)
            self.imagePanel.SetBackgroundColour(wx.Colour(255, 255, 255))
            imgPanelSizer = wx.BoxSizer(orient=wx.VERTICAL)
            imgPanelSizer.Add(self.imagePanel, 1, flag=wx.EXPAND)
            imgPanelSizer.Add(controlsPanel, 0, flag=wx.EXPAND)
            self.SetSizer(imgPanelSizer)
            self.Parent.Layout()
            self.Parent.Bind(wx.EVT_SIZE, self.OnResize)

        self.paperPicker.Value = 'Letter'

        self.image = wx.Image(imgPath)
        self.RefreshBitmap()

    def Rotate(self, clockwise):
        self.image = self.image.Rotate90(clockwise)
        self.RefreshBitmap()

def OnScan(evt):
    if SKIP_SCAN:
        imagePanel.SetImage(r"C:\Users\Collin\AppData\Roaming\PivotScan\2014-04-14_20-20-14.png")
    else:
        scanner = [s for s in scanners if s.name == scannerPicker.Value][0]
        img = scanner.scan(SCAN_DPI)
    
        if not os.path.isdir(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        dt = datetime.datetime.now()
        path = os.path.join(SAVE_DIR, 'scan.png') #dt.strftime('%Y-%m-%d_%H-%M-%S.png'))
        img.save(path)
        imagePanel.SetImage(path)

app = wx.App()
frame = wx.Frame(None, wx.ID_ANY, 'PivotScan')
frame.SetClientSize(WINDOW_SIZE)
frame.SetMinClientSize(WINDOW_SIZE)

topPanel = wx.Window(frame)
topRow = wx.BoxSizer()
topRow.AddSpacer((10, 50))
topRow.Add(wx.StaticText(topPanel, label='Scanner'), flag=wx.ALIGN_CENTER)
topRow.AddSpacer(10)

scannerPicker = wx.ComboBox(topPanel, style=wx.CB_DROPDOWN | wx.CB_READONLY, choices=scannerNames, value=scannerNames[0])
topRow.Add(scannerPicker, flag=wx.ALIGN_CENTER)
topRow.AddStretchSpacer()

scanButton = wx.Button(topPanel, label='Scan')
frame.Bind(wx.EVT_BUTTON, OnScan, scanButton)
topRow.Add(scanButton, flag=wx.ALIGN_CENTER)
topRow.AddSpacer(10)

topPanel.SetSizer(topRow)

contentSizer = wx.BoxSizer(orient=wx.VERTICAL)
contentSizer.Add(topPanel, flag=wx.EXPAND)

imagePanel = ImagePanel(frame)
contentSizer.Add(imagePanel, 1, flag=wx.EXPAND)

frame.SetSizer(contentSizer)
frame.Show(True)
app.MainLoop()
