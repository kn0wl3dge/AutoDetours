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
        public int time { get; set; }
        public string func_name { get; set; }
        public string[] func_params { get; set; }
        public string func_output { get; set; }

    }

    class Parser
    {
        static bool is_valid_length_for_items(String[] items)
        {
            return items.Length >= 5;
        }

        static bool is_thread_valid(String thread_string)
        {
            long thread_int; 
            return Int64.TryParse(thread_string, out thread_int);
        }

        static Tuple<string, long> reformat_timestamp(String timestamp)
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
            long epoch = (datetime.Ticks - 621355968000000000) / 10000000;

            var result = Tuple.Create<string, long>(timestamp_8601, epoch);

            return result;
        }

        static bool is_entry(String function_call)
        {
            return function_call[0] == '+';
        }

        static string[] get_func_params(string function_call)
        {
            string start = function_call.Split('(')[1];
            string params_string = start.Split(')')[0];
            return params_string.Split(',');
        }

        static string get_func(string function_call)
        {
            string start = function_call.Substring(1);
            return start.Split('(')[0];            
        }
        
        static string get_func_output(int i, string[] lines, string func_name)
        {
            for (; i < lines.Length; i++)
            {
                string[] items = lines[i].Split();
                if (is_valid_length_for_items(items))
                {
                    if (is_thread_valid(items[4]))
                    {
                        if (!is_entry(items[5]))
                        {
                            if (string.Compare(get_func(items[5]), func_name) == 0)
                            {
                                if (items.Length >= 8)
                                    return items[7]; //Check if several return
                                return "";
                            }
                        }

                    }
                }
            }

            return null;
        }

        static void write_json(List<string> json_list)
        {
            FileStream stream = null;
            stream = new FileStream("log.json", FileMode.OpenOrCreate);
            using (StreamWriter writer = new StreamWriter(stream, Encoding.UTF8))
            {
                writer.WriteLine('[');
                json_list.ForEach(delegate (string json)
                { 
                    writer.WriteLine(json + ','); 
                });
                writer.WriteLine(']');
                    
            }
        }

        static void parse_logs(string filename)
        {
            StreamReader reader = File.OpenText(filename);
            string[] lines = reader.ReadToEnd().Split('\n');
            List<string> json_list = new List<string>();
            
            for (int i = 0; i < lines.Length; i++)
            {
                string[] items = lines[i].Split(' ');

                if (is_valid_length_for_items(items))
                {
                    if (is_thread_valid(items[4])) //Check if it is a thread 
                    {
                        if (is_entry(items[5]))
                        {
                            Log log = new Log();

                            Tuple<string, long> timestamps = reformat_timestamp(items[0]);
                            log.timestamp = timestamps.Item1;
                            log.epoch = timestamps.Item2;

                            log.func_name = get_func(items[5]);
                            log.func_params = get_func_params(items[5]);
                            log.func_output = get_func_output(i + 1, lines, log.func_name);

                            json_list.Add(JsonConvert.SerializeObject(log, Formatting.Indented));
                        }

                    }
                }
            }
            write_json(json_list);
            reader.Close();
        }
        
        static void Main(string[] args)
        {
            string filename = "traces.txt";
            parse_logs(filename);
            
        }
    }
}
