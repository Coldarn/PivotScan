using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using WIA;
using System.IO;
using System.Windows.Media;

namespace PivotScan2
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private const string WiaFormatPNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}";

        private Scanner scanner;
        private PaperSize paperSize;
        private ScannedImageSize imageSize;
        private Point imageOffset = new Point();

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
            if (this.scanner == null)
                return;
            Device device = this.scanner.Device.Connect();
            ICommonDialog wiaCommonDialog = new WIA.CommonDialog();
            ImageFile image = (ImageFile)wiaCommonDialog.ShowTransfer(device.Items[1], WiaFormatPNG);
            var imagePath = Path.Combine(Settings.AppDataPath, "image." + image.FileExtension);
            File.Delete(imagePath);
            image.SaveFile(imagePath);
            this.imageSize = new ScannedImageSize
            {
                Width = image.Width,
                Height = image.Height,
                HorizontalResolution = image.HorizontalResolution,
                VerticalResolution = image.VerticalResolution,
            };
            this.imageOffset = new Point();

            this.ScannedImage.Source = new ImageSourceConverter().ConvertFromString(imagePath) as ImageSource;
            this.UpdateCanvas();
        }

        private void PickPaperSize_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var paperSize = e.AddedItems[0] as PaperSize;
            this.paperSize = paperSize;
            this.UpdateCanvas();
            Settings.Instance.PaperSize = paperSize.Name;
            Settings.Instance.Save();
        }

        private void AutoOpen_Checked(object sender, RoutedEventArgs e)
        {

        }

        private void RotateLeft_Click(object sender, RoutedEventArgs e)
        {

        }

        private void Center_Click(object sender, RoutedEventArgs e)
        {

        }

        private void RotateRight_Click(object sender, RoutedEventArgs e)
        {

        }

        private void Save_Click(object sender, RoutedEventArgs e)
        {

        }

        private void Window_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            this.UpdateCanvas();
        }

        private void UpdateCanvas()
        {
            double canvasAspectRatio = this.Canvas.ActualWidth / this.Canvas.ActualHeight;
            if (canvasAspectRatio <= this.paperSize.AspectRatio)
            {
                this.PageBackground.Width = this.Canvas.ActualWidth;
                this.PageBackground.Height = this.Canvas.ActualWidth / this.paperSize.AspectRatio;
            }
            else
            {
                this.PageBackground.Width = this.Canvas.ActualHeight * this.paperSize.AspectRatio;
                this.PageBackground.Height = this.Canvas.ActualHeight;
            }
            this.PageBorder.Width = this.PageBackground.Width;
            this.PageBorder.Height = this.PageBackground.Height;

            double topOffset = (this.Canvas.ActualHeight - this.PageBackground.Height) / 2;
            Canvas.SetTop(this.PageBackground, topOffset);
            Canvas.SetTop(this.PageBorder, topOffset);

            double leftOffset = (this.Canvas.ActualWidth - this.PageBackground.Width) / 2;
            Canvas.SetLeft(this.PageBackground, leftOffset);
            Canvas.SetLeft(this.PageBorder, leftOffset);

            if (this.imageSize != null)
            {
                this.ScannedImage.Width = this.imageSize.Width / this.imageSize.HorizontalResolution / this.paperSize.Width * this.PageBackground.Width;
                this.ScannedImage.Height = this.imageSize.Height / this.imageSize.VerticalResolution / this.paperSize.Height * this.PageBackground.Height;
                Canvas.SetLeft(this.ScannedImage, -this.ScannedImage.Width / 2 + this.Canvas.ActualWidth / 2 + this.imageOffset.X);
                Canvas.SetTop(this.ScannedImage, -this.ScannedImage.Height / 2 + this.Canvas.ActualHeight / 2 + this.imageOffset.Y);
            }
        }
    }
}
