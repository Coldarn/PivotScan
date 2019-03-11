using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Xml.Serialization;
using System.Xml;

namespace PivotScan2
{
    [Serializable]
    public class Settings
    {
        internal static string AppDataPath
        {
            get { return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "PivotScan"); }
        }
        private static string SettingsPath
        {
            get { return Path.Combine(AppDataPath, "Settings.xml"); }
        }


        public string Scanner { get; set; }
        public string PaperSize { get; set; }


        private Settings() { }

        private static Settings instance;
        public static Settings Instance
        {
            get
            {
                if (instance == null)
                {
                    Directory.CreateDirectory(Settings.AppDataPath);
                    if (File.Exists(Settings.SettingsPath))
                    {
                        var serializer = new XmlSerializer(typeof(Settings));
                        using (var stream = File.OpenRead(Settings.SettingsPath))
                        using (var reader = XmlReader.Create(stream))
                        {
                            instance = (Settings)serializer.Deserialize(reader);
                        }
                    }
                    else
                    {
                        instance = new Settings();
                    }
                }
                return instance;
            }
        }

        public void Save()
        {
            Directory.CreateDirectory(Settings.AppDataPath);
            var serializer = new XmlSerializer(typeof(Settings));
            using (var stream = File.Create(Settings.SettingsPath))
            {
                serializer.Serialize(stream, this);
            }
        }
    }
}
