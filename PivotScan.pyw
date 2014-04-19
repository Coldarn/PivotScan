
# Dependencies:
#
# python-cjson - http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-cjson
# twain - https://pypi.python.org/pypi/twain/
# pip install python-imagescanner
# pip install reportlab
# wxpython - http://www.wxpython.org/download.php#msw
#

import os, sys, subprocess, json, wx
from imagescanner import ImageScanner
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch

os.chdir(os.path.dirname(sys.argv[0]))

SKIP_SCAN = True
SAVE_DIR = os.path.join(os.environ['APPDATA'], 'PivotScan')

WINDOW_SIZE = (600, 600)
PADDING = 8
IMAGE_SIZE = WINDOW_SIZE[0] - 40
SCAN_DPI = 300.
PAPER_SIZES = (
    ('Letter (Portrait)', (8.5, 11)),
    ('Letter (Landscape)', (11, 8.5)),
    ('Legal (Portrait)', (8.5, 14)),
    ('Legal (Landscape)', (14, 8.5)),
    ('Ledger (Portrait)', (11, 17)),
    ('Ledger (Landscape)', (17, 11)),
)

iscan = ImageScanner(remote_search=False)
scanners = iscan.list_scanners()
scannerNames = ['Scanner 1', 'Larger Scanner Name 2'] if SKIP_SCAN else [s.name for s in scanners]

def clamp(left, right, value):
    return max(left, min(right, value))



SETTINGS_PATH = os.path.join(SAVE_DIR, 'settings.json')
SETTINGS = None

def _loadSettings():
    global SETTINGS
    if not SETTINGS:
        try:
            with open(SETTINGS_PATH, 'r') as fp:
                SETTINGS = json.load(fp)
        except:
            SETTINGS = {}

def GetSetting(**kwargs):
    global SETTINGS
    _loadSettings()
    prop = kwargs.items()[0]
    return SETTINGS.get(prop[0], prop[1])

def SetSetting(**kwargs):
    global SETTINGS
    _loadSettings()
    for k, v in kwargs.iteritems():
        SETTINGS[k] = v
    with open(SETTINGS_PATH, 'w') as fp:
        json.dump(SETTINGS, fp, sort_keys=True, indent=2, separators=(',', ': '))



class ImagePanel(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.pendingRepaint = False
        self.imagePanel = None
        self.paperPicker = None
        self.isDragging = False

        # Used when dragging the image around
        self.screenToPageScale = 1.0
        self.imageOffset = wx.Point2D(0, 0)
        self.lastPos = None

        self.Parent.Bind(wx.EVT_IDLE, self.OnIdle)

    def OnResize(self, evt):
        if self.imagePanel:
            self.pendingRepaint = True

    def OnIdle(self, evt):
        if self.pendingRepaint:
            self.Parent.Layout()
            self.RefreshBitmap()
            self.pendingRepaint = False

    def SetDragging(self, dragging):
        self.isDragging = dragging
        self.lastPos = None

    def OnMouseMove(self, evt):
        if not evt.leftIsDown or not self.isDragging:
            if self.isDragging:
                self.SetDragging(False)
            return

        if self.lastPos:
            delta = evt.Position - self.lastPos
            self.imageOffset = self.imageOffset + wx.Point2D(delta.x, delta.y) * self.screenToPageScale
            self.RefreshBitmap()
        self.lastPos = evt.Position

    def GetPaperSize(self):
        return [size for name, size in PAPER_SIZES if name == self.paperPicker.Value][0]

    def RefreshBitmap(self):
        oldSize = self.image.GetSize()
        windowSize = (self.imagePanel.GetSize()[0] - 40, self.imagePanel.GetSize()[1] - 40)
        imgScale = min(windowSize[0] / float(oldSize[0]), windowSize[1] / float(oldSize[1]))

        self.imageOffset = wx.Point2D(clamp(-oldSize.x / 2, oldSize.x / 2, self.imageOffset.x), clamp(-oldSize.y / 2, oldSize.y / 2, self.imageOffset.y))

        paperSize = self.GetPaperSize()
        paperWidth = float(paperSize[0] * SCAN_DPI)
        paperHeight = float(paperSize[1] * SCAN_DPI)
        paperScale = min(windowSize[0] / paperWidth, windowSize[1] / paperHeight)
        scale = min(imgScale, paperScale)
        self.screenToPageScale = 1. / scale

        newImgSize = (oldSize[0] * scale, oldSize[1] * scale)
        newPaperSize = (paperWidth * scale, paperHeight * scale)
        bitmap = self.image.Scale(newImgSize[0], newImgSize[1], wx.IMAGE_QUALITY_HIGH).ConvertToBitmap();

        # Draw the image
        dc = wx.ClientDC(self.imagePanel)
        dc.Clear()
        dc.DrawBitmap(bitmap, windowSize[0] / 2 - newImgSize[0] / 2 + 20 + self.imageOffset[0] * scale,
                      windowSize[1] / 2 - newImgSize[1] / 2 + 20 + self.imageOffset[1] * scale)

        # Draw the paper size/orientation overlay
        dc.Pen = wx.Pen(wx.Colour(0, 0, 0), 3)
        dc.Brush = wx.Brush(None, wx.TRANSPARENT)
        dc.DrawRectangle(windowSize[0] / 2 - newPaperSize[0] / 2 + 20, windowSize[1] / 2 - newPaperSize[1] / 2 + 20, newPaperSize[0], newPaperSize[1])
        dc.Pen = wx.Pen(wx.Colour(255, 255, 255), 3, wx.PENSTYLE_FDIAGONAL_HATCH)
        dc.DrawRectangle(windowSize[0] / 2 - newPaperSize[0] / 2 + 20, windowSize[1] / 2 - newPaperSize[1] / 2 + 20, newPaperSize[0], newPaperSize[1])

    def SetImage(self, imgPath):
        # Construct the bottom panel controls if this is the first time through
        if not self.imagePanel:
            # Bottom panel full of edit controls
            controlsPanel = wx.Window(self, size=(WINDOW_SIZE[0], 50))

            controlsSizer = wx.BoxSizer()
            
            controlsSizer.AddSpacer((PADDING, 50))
            controlsSizer.Add(wx.StaticText(controlsPanel, label='Paper Size'), flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(PADDING)

            self.paperPicker = wx.ComboBox(controlsPanel, style=wx.CB_DROPDOWN | wx.CB_READONLY, choices=[n[0] for n in PAPER_SIZES])
            self.paperPicker.Value = GetSetting(paperSize=PAPER_SIZES[0][0])
            self.paperPicker.Bind(wx.EVT_COMBOBOX, self.SetPaperSize)
            controlsSizer.Add(self.paperPicker, flag=wx.ALIGN_CENTER)
            controlsSizer.AddStretchSpacer()

            rotateLeftButton = wx.Button(controlsPanel, size=(42, 36))
            rotateLeftButton.SetBitmap(wx.Bitmap('RotateLeft.png'))
            self.Bind(wx.EVT_BUTTON, lambda _: self.Rotate(False), rotateLeftButton)
            controlsSizer.Add(rotateLeftButton, flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(PADDING)

            centerButton = wx.Button(controlsPanel, size=(42, 36))
            centerButton.SetBitmap(wx.Bitmap('Center.png'))
            self.Bind(wx.EVT_BUTTON, self.Center, centerButton)
            controlsSizer.Add(centerButton, flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(PADDING)

            rotateRightButton = wx.Button(controlsPanel, size=(42, 36))
            rotateRightButton.SetBitmap(wx.Bitmap('RotateRight.png'))
            rotateRightButton.Bind(wx.EVT_BUTTON, lambda _: self.Rotate(True))
            controlsSizer.Add(rotateRightButton, flag=wx.ALIGN_CENTER)
            controlsSizer.AddStretchSpacer()

            self.openAfterSaveCheckbox = wx.CheckBox(controlsPanel, label='Open after save')
            self.openAfterSaveCheckbox.Value = GetSetting(openAfterSave=True)
            controlsSizer.Add(self.openAfterSaveCheckbox, flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(PADDING)

            saveToPdfButton = wx.Button(controlsPanel, label='Save to PDF', size=(-1, 36))
            saveToPdfButton.Bind(wx.EVT_BUTTON, lambda _: self.SaveToPDF())
            controlsSizer.Add(saveToPdfButton, flag=wx.ALIGN_CENTER)
            controlsSizer.AddSpacer(PADDING)

            controlsPanel.SetSizer(controlsSizer)

            self.imagePanel = wx.Window(self)
            self.imagePanel.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.imagePanel.Bind(wx.EVT_LEFT_DOWN, lambda _: self.SetDragging(True))
            self.imagePanel.Bind(wx.EVT_LEFT_UP, lambda _: self.SetDragging(False))
            self.imagePanel.Bind(wx.EVT_MOTION, self.OnMouseMove)

            imgPanelSizer = wx.BoxSizer(orient=wx.VERTICAL)
            imgPanelSizer.Add(self.imagePanel, 1, flag=wx.EXPAND)
            imgPanelSizer.Add(controlsPanel, 0, flag=wx.EXPAND)
            self.SetSizer(imgPanelSizer)

            # Kick off an initial layout so that our imagePanel knows how big it is
            self.Parent.Layout()
            self.Parent.Bind(wx.EVT_SIZE, self.OnResize)

        # Load up the image and kick off a paint and layout to refresh everything as necessary
        self.image = wx.Image(imgPath)
        self.RefreshBitmap()
        self.Parent.Layout()

    def SetPaperSize(self, evt):
        SetSetting(paperSize=self.paperPicker.Value)
        self.RefreshBitmap()

    def Rotate(self, clockwise):
        self.image = self.image.Rotate90(clockwise)
        self.RefreshBitmap()

    def Center(self, evt):
        self.imageOffset = wx.Point2D()
        self.RefreshBitmap()

    def SaveToPDF(self):
        SetSetting(openAfterSave=self.openAfterSaveCheckbox.Value)
        fd = wx.FileDialog(self.Parent, 'Save to PDF', wildcard='PDF Files (*.pdf)|*.pdf', style=wx.FD_SAVE)
        saveDirectory = GetSetting(saveDirectory=None)
        if saveDirectory:
            fd.Directory = saveDirectory
        if fd.ShowModal() == wx.ID_CANCEL:
            return

        path = os.path.join(SAVE_DIR, 'pdfImage.png')
        self.image.SaveFile(path, wx.BITMAP_TYPE_PNG)

        with open(fd.Path, 'wb') as fp:
            paperSize = self.GetPaperSize()
            paperSize = (paperSize[0] * inch, paperSize[1] * inch)
            canvas = Canvas(fp, paperSize)
            imgPdfSize = (self.image.GetSize().x / SCAN_DPI * inch, self.image.GetSize().y / SCAN_DPI * inch)
            canvas.drawImage(path, paperSize[0] / 2 - imgPdfSize[0] / 2 + self.imageOffset.x / SCAN_DPI * inch,
                                   paperSize[1] / 2 - imgPdfSize[1] / 2 - self.imageOffset.y / SCAN_DPI * inch, imgPdfSize[0], imgPdfSize[1])
            canvas.save()
        
        SetSetting(saveDirectory=os.path.dirname(fd.Path))

        if self.openAfterSaveCheckbox.Value:
            subprocess.Popen(fd.Path, shell=True)

def OnScan(evt):
    path = os.path.join(SAVE_DIR, 'scan.png')
    if SKIP_SCAN:
        imagePanel.SetImage(path)
    else:
        scanner = [s for s in scanners if s.name == scannerPicker.Value][0]
        img = scanner.scan(SCAN_DPI)
    
        if not os.path.isdir(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        img.save(path)
        imagePanel.SetImage(path)

app = wx.App()

if not SKIP_SCAN and len(scanners) < 1:
    wx.MessageBox('ERROR: No scanners detected!', 'PivotScan', style=wx.OK | wx.CENTER | wx.ICON_ERROR)
else:
    frame = wx.Frame(None, wx.ID_ANY, 'PivotScan')
    frame.SetClientSize(WINDOW_SIZE)
    frame.SetMinClientSize(WINDOW_SIZE)
    frame.SetIcon(wx.Icon('PivotScan.ico', wx.BITMAP_TYPE_ICO))

    # Build up the top UI panel
    topPanel = wx.Window(frame)
    topRow = wx.BoxSizer()
    topRow.AddSpacer((PADDING, 50))
    topRow.Add(wx.StaticText(topPanel, label='Scanner'), flag=wx.ALIGN_CENTER)
    topRow.AddSpacer(PADDING)

    # Dropdown to choose which scanner to use
    scannerPicker = wx.ComboBox(topPanel, style=wx.CB_DROPDOWN | wx.CB_READONLY, choices=scannerNames)
    scannerPicker.Value = GetSetting(scanner=scannerNames[0])
    scannerPicker.Bind(wx.EVT_COMBOBOX, lambda _: SetSetting(scanner=scannerPicker.Value))
    topRow.Add(scannerPicker, flag=wx.ALIGN_CENTER)
    topRow.AddStretchSpacer()

    # Button that kicks off a scan and population of the image panel UI
    scanButton = wx.Button(topPanel, label='Scan', size=(-1, 36))
    frame.Bind(wx.EVT_BUTTON, OnScan, scanButton)
    topRow.Add(scanButton, flag=wx.ALIGN_CENTER)
    topRow.AddSpacer(PADDING)

    topPanel.SetSizer(topRow)

    contentSizer = wx.BoxSizer(orient=wx.VERTICAL)
    contentSizer.Add(topPanel, flag=wx.EXPAND)

    imagePanel = ImagePanel(frame)
    contentSizer.Add(imagePanel, 1, flag=wx.EXPAND)

    frame.SetSizer(contentSizer)
    frame.Show(True)

app.MainLoop()
