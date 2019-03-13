using PdfSharp;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WIA;

namespace PivotScan2
{
    internal class Scanner
    {
        public DeviceInfo Device { get; set; }

        public string Name { get { return Device.Properties["Description"].get_Value(); } }
    }

    internal class PaperSize
    {
        public static readonly PaperSize[] Defaults = new[]
        {
            new PaperSize { Name = "Letter (Portrait)", Width = 8.5f, Height = 11f, PdfSize = PageSize.Letter, Orientation = PageOrientation.Portrait },
            new PaperSize { Name = "Letter (Landscape)", Width = 11f, Height = 8.5f, PdfSize = PageSize.Letter, Orientation = PageOrientation.Landscape },
            new PaperSize { Name = "Legal (Portrait)", Width = 8.5f, Height = 14f, PdfSize = PageSize.Legal, Orientation = PageOrientation.Portrait },
            new PaperSize { Name = "Legal (Landscape)", Width = 14f, Height = 8.5f, PdfSize = PageSize.Legal, Orientation = PageOrientation.Landscape },
            new PaperSize { Name = "Ledger (Portrait)", Width = 11f, Height = 17f, PdfSize = PageSize.Ledger, Orientation = PageOrientation.Landscape },
            new PaperSize { Name = "Ledger (Landscape)", Width = 17f, Height = 11f, PdfSize = PageSize.Ledger, Orientation = PageOrientation.Portrait },
        };


        public string Name { get; set; }
        public float Width { get; set; }
        public float Height { get; set; }
        public PageSize PdfSize { get; set; }
        public PageOrientation Orientation { get; set; }

        public float AspectRatio { get { return this.Width / this.Height; } }
    }

    internal class ScannedImageSize
    {
        public double HorizontalResolution { get; set; }
        public double VerticalResolution { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
    }
}
