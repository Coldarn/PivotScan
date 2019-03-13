using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using WIA;
using System.IO;
using System.Windows.Media;
using PdfSharp.Pdf;
using PdfSharp.Drawing;
using System.Windows.Media.Imaging;
using System.Diagnostics;

namespace PivotScan2
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private const string WiaFormatPNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}";

        private Scanner scanner;
        private PaperSize pageSizeInches;
        private ScannedImageSize imageSizePixels;
        private Point imageOffsetInches = new Point();

        // Local state for dragging the scanned image, only valid while dragging
        private bool isDragging = false;
        private Point dragStartPosition = new Point();
        private Point imageOffsetStart = new Point();

        public MainWindow()
        {
            InitializeComponent();

            PickScanner.SelectedIndex = 0;
            PickScanner.ItemsSource = this.Scanners;

            PickPaperSize.ItemsSource = PaperSize.Defaults;
            PickPaperSize.SelectedItem = PaperSize.Defaults.FirstOrDefault(p => p.Name == Settings.Instance.PaperSize) ?? PaperSize.Defaults[0];
        }

        internal IEnumerable<Scanner> Scanners
        {
            get
            {
                var dm = new DeviceManager();
                int i = 0;
                foreach (DeviceInfo deviceInfo in dm.DeviceInfos)
                {
                    if (deviceInfo.Type == WiaDeviceType.ScannerDeviceType)
                    {
                        var scanner = new Scanner { Device = deviceInfo };
                        if (scanner.Name == Settings.Instance.Scanner)
                        {
                            PickScanner.SelectedIndex = i;
                            this.scanner = scanner;
                        }
                        yield return scanner;
                        ++i;
                    }
                }
            }
        }

        private void PickScanner_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selectedScanner = e.AddedItems[0] as Scanner;
            this.scanner = selectedScanner;
            Settings.Instance.Scanner = selectedScanner.Name;
            Settings.Instance.Save();
        }

        private void Scan_Click(object sender, RoutedEventArgs e)
        {
            if (this.scanner == null) return; // No scanner selected/available

            Device device = this.scanner.Device.Connect();
            ICommonDialog wiaCommonDialog = new WIA.CommonDialog();
            ImageFile image = (ImageFile)wiaCommonDialog.ShowTransfer(device.Items[1], WiaFormatPNG);

            if (image == null) return; // Scan cancelled

            var imagePath = Path.Combine(Settings.AppDataPath, "image." + image.FileExtension);
            File.Delete(imagePath);
            image.SaveFile(imagePath);

            // Save the image dimentions for scaling computations later
            this.imageSizePixels = new ScannedImageSize
            {
                Width = image.Width,
                Height = image.Height,
                HorizontalResolution = image.HorizontalResolution,
                VerticalResolution = image.VerticalResolution,
            };

            // Center the newly-scanned image
            this.imageOffsetInches = new Point();

            // Draw the new image
            this.ScannedImage.Source = new ImageSourceConverter().ConvertFromString(imagePath) as BitmapSource;
            this.UpdateScannedImageBounds();
        }

        private void PickPaperSize_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var paperSize = e.AddedItems[0] as PaperSize;
            this.pageSizeInches = paperSize;
            this.UpdateCanvas();
            Settings.Instance.PaperSize = paperSize.Name;
            Settings.Instance.Save();
        }

        private void RotateLeft_Click(object sender, RoutedEventArgs e)
        {

        }

        private void Center_Click(object sender, RoutedEventArgs e)
        {
            this.imageOffsetInches = new Point();
            this.UpdateScannedImageBounds();
        }

        private void RotateRight_Click(object sender, RoutedEventArgs e)
        {

        }

        private void Save_Click(object sender, RoutedEventArgs e)
        {
            if (this.imageSizePixels == null) return;

            var dialog = new Microsoft.Win32.SaveFileDialog();
            dialog.DefaultExt = ".pdf";
            dialog.Filter = "PDF documents (.pdf)|*.pdf";

            if (dialog.ShowDialog() != true) return;

            var pdf = new PdfDocument();
            var page = pdf.AddPage();
            page.Size = this.pageSizeInches.PdfSize;
            page.Orientation = this.pageSizeInches.Orientation;

            var gfx = XGraphics.FromPdfPage(page);

            var encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(this.ScannedImage.Source as BitmapSource));
            using (var ms = new MemoryStream())
            {
                encoder.Save(ms);
                var image = XImage.FromStream(ms);

                XUnit width = XUnit.FromInch(this.imageSizePixels.Width / this.imageSizePixels.HorizontalResolution);
                XUnit height= XUnit.FromInch(this.imageSizePixels.Height / this.imageSizePixels.VerticalResolution);
                XUnit x = -width / 2 + page.Width / 2 + XUnit.FromInch(this.imageOffsetInches.X);
                XUnit y = -height / 2 + page.Height/ 2 + XUnit.FromInch(this.imageOffsetInches.Y);
                gfx.DrawImage(image, x, y, width, height);
            }

            try
            {
                pdf.Save(dialog.FileName);

                if (this.OpenAfterSave.IsChecked == true)
                {
                    Process.Start(dialog.FileName);
                }
            }
            catch (IOException)
            {
                MessageBox.Show("Cannot save as the given file is open - please close it and try again.");
            }
        }

        private void Window_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            this.UpdateCanvas();
        }

        private void UpdateCanvas()
        {
            double canvasAspectRatio = this.Canvas.ActualWidth / this.Canvas.ActualHeight;

            // Constrain the page rectangle to the available canvas area while maintaining aspect ratio
            if (canvasAspectRatio <= this.pageSizeInches.AspectRatio)
            {
                this.PageBackground.Width = this.Canvas.ActualWidth;
                this.PageBackground.Height = this.Canvas.ActualWidth / this.pageSizeInches.AspectRatio;
            }
            else
            {
                this.PageBackground.Width = this.Canvas.ActualHeight * this.pageSizeInches.AspectRatio;
                this.PageBackground.Height = this.Canvas.ActualHeight;
            }
            // Ensure the dashed page border mirrors the page background rectangle
            this.PageBorder.Width = this.PageBackground.Width;
            this.PageBorder.Height = this.PageBackground.Height;

            double topOffset = (this.Canvas.ActualHeight - this.PageBackground.Height) / 2;
            double leftOffset = (this.Canvas.ActualWidth - this.PageBackground.Width) / 2;

            // Center the page within the canvas area
            Canvas.SetTop(this.PageBackground, topOffset);
            Canvas.SetLeft(this.PageBackground, leftOffset);
            Canvas.SetTop(this.PageBorder, topOffset);
            Canvas.SetLeft(this.PageBorder, leftOffset);

            this.UpdateScannedImageBounds();
        }

        private void UpdateScannedImageBounds()
        {
            // Only continue if we have a scanned image
            if (this.imageSizePixels == null) return;

            // Scale the scanned image to the page
            this.ScannedImage.Width = this.imageSizePixels.Width / this.imageSizePixels.HorizontalResolution / this.pageSizeInches.Width * this.PageBackground.Width;
            this.ScannedImage.Height = this.imageSizePixels.Height / this.imageSizePixels.VerticalResolution / this.pageSizeInches.Height * this.PageBackground.Height;

            // Center it on the page, adjusting for the drag offset
            Canvas.SetLeft(this.ScannedImage, -this.ScannedImage.Width / 2 + this.Canvas.ActualWidth / 2 + this.imageOffsetInches.X * PagePixelsPerInchX);
            Canvas.SetTop(this.ScannedImage, -this.ScannedImage.Height / 2 + this.Canvas.ActualHeight / 2 + this.imageOffsetInches.Y * PagePixelsPerInchY);
        }

        private double PagePixelsPerInchX
        {
            get { return this.PageBackground.Width / this.pageSizeInches.Width; }
        }
        private double PagePixelsPerInchY
        {
            get { return this.PageBackground.Height / this.pageSizeInches.Height; }
        }

        private void Page_MouseDown(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            this.isDragging = true;
            this.dragStartPosition = e.GetPosition(this);
            this.imageOffsetStart = this.imageOffsetInches;
        }

        private void Page_MouseUp(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            this.isDragging = false;
        }

        private void Page_MouseMove(object sender, System.Windows.Input.MouseEventArgs e)
        {
            if (!this.isDragging) return;

            // Total pixel offset of the mouse from the drag start
            var dragOffsetPixels = e.GetPosition(this) - this.dragStartPosition;

            // Convert the drag offset from pixels to page inches
            var dragOffsetInches = new System.Windows.Vector(dragOffsetPixels.X / PagePixelsPerInchX, dragOffsetPixels.Y / PagePixelsPerInchY);
            this.imageOffsetInches = this.imageOffsetStart + dragOffsetInches;
            this.UpdateScannedImageBounds();
        }
    }
}
