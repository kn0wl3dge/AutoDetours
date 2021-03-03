using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Threading;
using Newtonsoft.Json;

namespace Parser
{
    public class Log
    {
        public string timestamp { get; set; }
        public long epoch { get; set; }
        public long timeMs { get; set; }
        public int thread { get; set; }
        public string funcName { get; set; }
        public string[] funcParams { get; set; }
        public string funcOutput { get; set; }
    }

    class Parser
    {
        private static bool isValidLengthForItems(String[] items)
        {
            return items.Length >= 5;
        }

        private static bool isThreadValid(String threadString)
        {
            long threadInt; 
            return Int64.TryParse(threadString, out threadInt);
        }

        private static long convertToTimestamp(string timestamp8601)
        {
            DateTime value = DateTime.Parse(timestamp8601);
            DateTime epoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);

            TimeSpan elapsedTime = value - epoch;
            return (long)elapsedTime.TotalMilliseconds;
        }

        private static Tuple<string, long> reformatTimestamp(String timestamp)
        {
            string year = timestamp.Substring(0, 4);
            string month = timestamp.Substring(4, 2);
            string day = timestamp.Substring(6, 2);
            string hour = timestamp.Substring(8, 2);
            string min = timestamp.Substring(10, 2);
            string sec = timestamp.Substring(12, 2);
            string ms = timestamp.Substring(14);

            string timestamp8601 = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec + "." + ms + "+00";
            
            DateTime datetime = DateTime.Parse(timestamp8601);
            long epoch = convertToTimestamp(timestamp8601);

            var result = Tuple.Create<string, long>(timestamp8601, epoch);

            return result;
        }

        private static int isEntry(String functionCall)
        {
            if (functionCall.Length == 0)
                return -1;
            if (functionCall[0] == '+')
                return 1;
            return 0;
        }

        private static string[] getFuncParams(string functionCall)
        {
            string start = functionCall.Split('(')[1];
            string paramsString = start.Split(')')[0];
            return paramsString.Split(',');
        }

        private static string getFunc(string functionCall)
        {
            string start = functionCall.Substring(1);
            return start.Split('(')[0];            
        }
        
        private static string getFuncOutput(int i, string[] lines, string funcName)
        {
            for (; i < lines.Length; i++)
            {
                string[] items = lines[i].Split();
                if (isValidLengthForItems(items))
                    if (isThreadValid(items[4]))
                    {
                        int indexFuncName = 5;
                        while (isEntry(items[indexFuncName]) == -1)
                            indexFuncName++;

                        if (isEntry(items[indexFuncName]) == 0)
                            if (string.Compare(getFunc(items[indexFuncName]), funcName) == 0)
                            {
                                if (items.Length == indexFuncName + 3)
                                    return items[indexFuncName + 2]; //Check if several return
                                return "";
                            }
                    }
            }
            return null;
        }

        private static void writeJson(List<string> jsonList)
        {
            FileStream stream = null;
            stream = new FileStream("log.json", FileMode.OpenOrCreate);
            using (StreamWriter writer = new StreamWriter(stream, Encoding.UTF8))
            {
                writer.WriteLine('[');
                writer.Write(jsonList[0]);
                for (int i = 1; i < jsonList.Count; i ++)
                    writer.WriteLine(',' + jsonList[i]);
                writer.WriteLine(']');      
            }
        }
        
        public static void parseLogs(string filename)
        {
            StreamReader reader = File.OpenText(filename);
            string[] lines = reader.ReadToEnd().Split('\n');
            List<string> jsonList = new List<string>();
            long start_time = reformatTimestamp(lines[0].Split(' ')[0]).Item2;
            
            for (int i = 0; i < lines.Length; i++)
            {
                string[] items = lines[i].Split(' ');
                if (isValidLengthForItems(items))
                { 
                    if (isThreadValid(items[4]))
                    {
                        int indexFuncName = 5;
                        while (isEntry(items[indexFuncName]) == -1)
                            indexFuncName++;

                        if (isEntry(items[indexFuncName]) == 1)
                        {
                            Log log = new Log();
                            Tuple<string, long> timestamps = reformatTimestamp(items[0]);
                            log.timestamp = timestamps.Item1;
                            log.epoch = timestamps.Item2;
                            log.timeMs = log.epoch - start_time;

                            log.thread = int.Parse(items[4]);

                            log.funcName = getFunc(items[indexFuncName]);
                            log.funcParams = getFuncParams(items[indexFuncName]);
                            log.funcOutput = getFuncOutput(i + 1, lines, log.funcName);

                            try
                            {
                                jsonList.Add(JsonConvert.SerializeObject(log, Formatting.Indented));
                            }
                            catch (JsonException) 
                            {
                                Console.WriteLine("Didn't work for " + log.funcName);
                                Thread.Sleep(100);
                            }
                                                                
                        }
                    }
                }
            }
            writeJson(jsonList);
            reader.Close();
        }
        
        static void Main(string[] args)
        {
            string filename = "traces.txt";
            parseLogs(filename);       
        }
    }
}
