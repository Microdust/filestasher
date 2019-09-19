using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace CSharpReader
{
    class Program
    {
        
        private static string ReadString(byte[] bytes, ref int index)
        {
            var stringLength = ReadInteger(bytes, ref index);
            var str = Encoding.UTF8.GetString(bytes, index, stringLength);
            index += stringLength;

            return str;
        }

        private static int ReadInteger(byte[] bytes, ref int index)
        {    
            var val = (int)BitConverter.ToUInt32(bytes, index);
            index += 4;
            return val;
        }

        private static (string, byte[]) ReadBlob(byte[] bytes, ref int index)
        {
            var path = ReadString(bytes, ref index);
            var size = ReadInteger(bytes, ref index);            
            
            byte[] data = new byte[size];
            Buffer.BlockCopy(bytes, index, data, 0, size);

            index += size;
            
            return (path, data);
        }

        static void Main(string[] args)
        {
            int index = 0;
            var bytes = File.ReadAllBytes("test.bin");
            var name = ReadString(bytes, ref index);
            var entries = ReadInteger(bytes, ref index);

            Console.WriteLine($"Name: {name}, entries: {entries}");

            var dict = new Dictionary<string, byte[]>();

            for (int i = 0; i < entries; i++)
            {
                var blob = ReadBlob(bytes, ref index);
                dict.Add(blob.Item1, blob.Item2);
            }

            foreach(KeyValuePair<string, byte[]> entry in dict)
            {
                Console.WriteLine($"Entry: {entry.Key}");
            }

        }
    }
}
