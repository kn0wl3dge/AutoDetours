using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using Newtonsoft.Json;

namespace AutoDetoursAgent
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

        public void Print()
        {
            Console.WriteLine("{ timestamp : " + timestamp + ", epoch : " + epoch + ", timeMs : " + timeMs + ", thread : "
                + thread + ", funcName : " + funcName + ", funcParams " + funcParams + ", funcOutput : " + funcOutput);
        }
    }

    class Parser
    {
        private static bool isValidLengthForItems(List<string> items)
        {
            return items.Count >= 5;
        }

        private static bool isThreadValid(String threadString)
        {
            long threadInt;
            return Int64.TryParse(threadString, out threadInt);
        }

        private static bool isValidTrace(List<string> items)
        {


            if (items.Contains("Error") || items.Contains("error"))
                return false;

            // Remove indentation from line and get the 5 firsts items of traces
            DeleteSpaces(items, 5);

            return isValidLengthForItems(items)
                && isThreadValid(items[4]);
        }

        private static long ConvertToTimestamp(string timestamp8601)
        {
            DateTime value = DateTime.Parse(timestamp8601);
            DateTime epoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);

            TimeSpan elapsedTime = value - epoch;
            return (long)elapsedTime.TotalMilliseconds;
        }

        private static Tuple<string, long> FormatTimestamps(String timestamp)
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
            long epoch = ConvertToTimestamp(timestamp8601);

            return Tuple.Create<string, long>(timestamp8601, epoch);
        }

        private static int isEntry(String functionCall)
        {
            if (functionCall.Length == 0)
                return -1;
            if (functionCall[0] == '+')
                return 1;
            return 0;
        }

        private static Tuple<string, string[]> GetFuncEntryInfos(string functionCall)
        {
            functionCall = functionCall.Substring(1);
            string[] name_params_split = functionCall.Split('(');
            string funcName = name_params_split[0];
            string[] funcParams = name_params_split[1].Split(')')[0].Split(',');

            return Tuple.Create<string, string[]>(funcName, funcParams);
        }

        private static Tuple<string, string> GetFuncOutputInfos(List<string> items)
        {
            string funcName = items[5].Substring(1).Split('(')[0];

            string funcOutput = "";
            if (items.Count >= 8)
                funcOutput = items[7];

            return Tuple.Create<string, string>(funcName, funcOutput);
        }

        private static void WriteJson(List<string> jsonList, string filename)
        {
            if (File.Exists(filename))
                File.Delete(filename);

            using (StreamWriter writer = File.CreateText(filename))
            {
                writer.WriteLine('[');
                writer.Write(jsonList[0]);
                for (int i = 1; i < jsonList.Count; i++)
                    writer.WriteLine(',' + jsonList[i]);

                writer.WriteLine(']');
            }
        }

        private static string LogToJson(List<string> jsonList)
        {
            string ret = "{\"results\":[" + jsonList[0];
            for (int i = 1; i < jsonList.Count; i++)
                ret += (',' + jsonList[i]);

            ret += "]}";

            return ret;
        }

        private static void DeleteSpaces(List<string> items, int length)
        {
            int nb_items = 0;
            int i = 0;

            while (nb_items < length && i < items.Count)
            {
                if (items[i] == "")
                    items.RemoveAt(i);
                else
                    nb_items++;
                i++;
            }
        }

        private static Log FindAssociatedLog(string funcName, List<Log> waitingOutput)
        {
            for (int i = (waitingOutput.Count() - 1); i >= 0; i--)
            {
                if (waitingOutput[i].funcName == funcName)
                {
                    Log ret = waitingOutput[i];
                    waitingOutput.RemoveAt(i);
                    return ret;
                }
            }

            return null;
        }

        private static void AddNotExitingLogs(List<string> jsonList, List<Log> waitingOutput)
        {
            for (int i = (waitingOutput.Count() - 1); i >= 0; i--)
            {
                waitingOutput[i].funcOutput = "No output";
                try
                {
                    jsonList.Add(JsonConvert.SerializeObject(waitingOutput[i], Formatting.Indented));
                }
                catch (JsonException)
                {
                    jsonList.Add("Error during serialization");
                }
            }
        }

        private static Log createLog(List<string> items, long start_time)
        {
            Log log = new Log();

            Tuple<String, long> timestamps = FormatTimestamps(items[0]);
            log.timestamp = timestamps.Item1;
            log.epoch = timestamps.Item2;
            log.timeMs = log.epoch - start_time;

            log.thread = int.Parse(items[4]);

            Tuple<String, String[]> entryInfos = GetFuncEntryInfos(items[5]);
            log.funcName = entryInfos.Item1;
            log.funcParams = entryInfos.Item2;

            return log;
        }

        public static string ParseLogs(string input_filename)
        {
            List<string> jsonList = new List<string>();

            using (StreamReader file = new StreamReader(input_filename))
            {
                string line = file.ReadLine();
                if (line == null)
                    return "[]";

                long start_time = FormatTimestamps(line.Split(' ')[0]).Item2;
                List<Log> waitingOutput = new List<Log>();

                while ((line = file.ReadLine()) != null)
                {
                    List<string> items = line.Split(' ').ToList();

                    if (!isValidTrace(items))
                        continue;

                    // Check if we have the function call or output
                    int funcType = isEntry(items[5]);
                    if (funcType == 1)
                    {
                        Log log = createLog(items, start_time);
                        waitingOutput.Add(log);
                    }

                    else if (funcType == 0)
                    {
                        Tuple<String, String> outputInfos = GetFuncOutputInfos(items);
                        string funcName = outputInfos.Item1;
                        string funcOutput = outputInfos.Item2;

                        // Get associated log
                        Log log = FindAssociatedLog(funcName, waitingOutput);
                        log.funcOutput = funcOutput;

                        try
                        {
                            jsonList.Add(JsonConvert.SerializeObject(log, Formatting.Indented));
                        }
                        catch (JsonException)
                        {
                            jsonList.Add("Error during serialization");
                        }
                    }
                }

                // Add opened functions with no output
                AddNotExitingLogs(jsonList, waitingOutput);
            }

            return LogToJson(jsonList);
        }
    }
}