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
            new PaperSize("Letter (Portrait)", 8.5f, 11f),
            new PaperSize("Letter (Landscape)", 11f, 8.5f),
            new PaperSize("Legal (Portrait)", 8.5f, 14f),
            new PaperSize("Legal (Landscape)", 14f, 8.5f),
            new PaperSize("Ledger (Portrait)", 11f, 17f),
            new PaperSize("Ledger (Landscape)", 17f, 11f),
        };


        public string Name { get; set; }
        public float Width { get; set; }
        public float Height { get; set; }

        public float AspectRatio { get { return this.Width / this.Height; } }

        public PaperSize(string name, float width, float height)
        {
            this.Name = name;
            this.Width = width;
            this.Height = height;
        }
    }

    internal class ScannedImageSize
    {
        public double HorizontalResolution { get; set; }
        public double VerticalResolution { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
    }
}
