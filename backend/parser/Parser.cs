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
        public long time_ms { get; set; }

        public int thread { get; set; }
        public string func_name { get; set; }
        public string[] func_params { get; set; }
        public string func_output { get; set; }

    }

    class Parser
    {
        private static bool is_valid_length_for_items(String[] items)
        {
            return items.Length >= 5;
        }

        private static bool is_thread_valid(String thread_string)
        {
            long thread_int; 
            return Int64.TryParse(thread_string, out thread_int);
        }

        private static long convert_to_timestamp(string timestamp_8601)
        {
            DateTime value = DateTime.Parse(timestamp_8601);
            DateTime epoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);

            TimeSpan elapsedTime = value - epoch;
            return (long)elapsedTime.TotalMilliseconds;
        }

        private static Tuple<string, long> reformat_timestamp(String timestamp)
        {
            string year = timestamp.Substring(0, 4);
            string month = timestamp.Substring(4, 2);
            string day = timestamp.Substring(6, 2);
            string hour = timestamp.Substring(8, 2);
            string min = timestamp.Substring(10, 2);
            string sec = timestamp.Substring(12, 2);
            string ms = timestamp.Substring(14);

            string timestamp_8601 = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec + "." + ms + "+00";
            
            DateTime datetime = DateTime.Parse(timestamp_8601);
            long epoch = convert_to_timestamp(timestamp_8601);

            var result = Tuple.Create<string, long>(timestamp_8601, epoch);

            return result;
        }

        private static int is_entry(String function_call)
        {
            if (function_call.Length == 0)
                return -1;
            if (function_call[0] == '+')
                return 1;
            return 0;
        }

        private static string[] get_func_params(string function_call)
        {
            string start = function_call.Split('(')[1];
            string params_string = start.Split(')')[0];
            return params_string.Split(',');
        }

        private static string get_func(string function_call)
        {
            string start = function_call.Substring(1);
            return start.Split('(')[0];            
        }
        
        private static string get_func_output(int i, string[] lines, string func_name)
        {
            for (; i < lines.Length; i++)
            {
                string[] items = lines[i].Split();
                if (is_valid_length_for_items(items))
                {
                    if (is_thread_valid(items[4]))
                    {
                        int index_func_name = 5;

                        while (is_entry(items[index_func_name]) == -1)
                            index_func_name++;

                        if (is_entry(items[index_func_name]) == 0)
                        {
                            if (string.Compare(get_func(items[index_func_name]), func_name) == 0)
                            {
                                if (items.Length == index_func_name + 3)
                                    return items[index_func_name + 2]; //Check if several return
                                return "";
                            }
                        }

                    }
                }
            }

            return null;
        }

        private static void write_json(List<string> json_list)
        {
            FileStream stream = null;
            stream = new FileStream("log.json", FileMode.OpenOrCreate);
            using (StreamWriter writer = new StreamWriter(stream, Encoding.UTF8))
            {
                writer.WriteLine('[');
                writer.Write(json_list[0]);
                for (int i = 1; i < json_list.Count; i ++)
                    writer.WriteLine(',' + json_list[i]);
                writer.WriteLine(']');
                    
            }
        }
        
        public static void parse_logs(string filename)
        {
            StreamReader reader = File.OpenText(filename);
            string[] lines = reader.ReadToEnd().Split('\n');
            List<string> json_list = new List<string>();

            long start_time = reformat_timestamp(lines[0].Split(' ')[0]).Item2;
            
            for (int i = 0; i < lines.Length; i++)
            {
                string[] items = lines[i].Split(' ');
                if (is_valid_length_for_items(items))
                {
                    
                    if (is_thread_valid(items[4]))
                    {
                        int index_func_name = 5;
                        while (is_entry(items[index_func_name]) == -1)
                            index_func_name++;

                        if (is_entry(items[index_func_name]) == 1)
                        {
                            Log log = new Log();

                            Tuple<string, long> timestamps = reformat_timestamp(items[0]);
                            log.timestamp = timestamps.Item1;
                            log.epoch = timestamps.Item2;
                            log.time_ms = log.epoch - start_time;

                            log.thread = int.Parse(items[4]);

                            log.func_name = get_func(items[index_func_name]);
                            log.func_params = get_func_params(items[index_func_name]);
                            log.func_output = get_func_output(i + 1, lines, log.func_name);

                            try
                            {
                                json_list.Add(JsonConvert.SerializeObject(log, Formatting.Indented));
                            }
                            catch (JsonException) 
                            {
                                Console.WriteLine("Didn't work for " + log.func_name);
                                Thread.Sleep(100);
                            }
                                                                
                        }
                    }
                }
            }

            write_json(json_list);
            reader.Close();
        }
        
        static void Main(string[] args)
        {
            string filename = "traces2.txt";
            parse_logs(filename);
            
        }
    }
}
