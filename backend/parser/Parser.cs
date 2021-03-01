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
        public string Timestamp { get; set; }
        public string Pid { get; set; }
        public string Hook { get; set; }
        public string Func_name { get; set; }
        public string[] Func_params { get; set; }
        public string Func_output { get; set; }

        public Log()
        {
            Timestamp = null;
            Pid = null;
            Hook = null;
            Func_name = null;
            Func_output = null;
            Func_params = null;
        }

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

        static string reformat_timestamp(String timestamp)
        {
            string year = timestamp.Substring(0, 4);
            string month = timestamp.Substring(4, 2);
            string day = timestamp.Substring(6, 2);
            string hour = timestamp.Substring(8, 2);
            string min = timestamp.Substring(10, 2);
            string sec = timestamp.Substring(12, 2);
            string ms = timestamp.Substring(14);
            string timestamp_ret = year + "/" + month + "/" + day + "-" + hour + ":" + min + ":" + sec + ":" + ms;
            return timestamp_ret;
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

        static string get_func_output(string function_call)
        {
            if (function_call.Split('>').Length < 2)
                return "";
            return function_call.Split('>')[1];
        }

        static string get_func(string function_call)
        {
            string start = function_call.Substring(1);
            return start.Split('(')[0];            
        }

        static void write_json(List<string> json_list)
        {
            FileStream stream = null;
            stream = new FileStream("log.json", FileMode.OpenOrCreate);
            using (StreamWriter writer = new StreamWriter(stream, Encoding.UTF8))
            {
                json_list.ForEach(delegate (string json)
                { 
                    writer.WriteLine(json); 
                });
                    
            }
        }

        static void parse_logs(string filename)
        {
            StreamReader reader = File.OpenText(filename);

            string line;
            List<string> json_list = new List<string>();
            while ((line = reader.ReadLine()) != null)
            {
                Log log = new Log();
                string[] items = line.Split(' ');
                if (is_valid_length_for_items(items))
                {
                    if (is_thread_valid(items[4])) //Check if it is a thread 
                    {
                        log.Timestamp = reformat_timestamp(items[0]);
                        log.Pid = items[1];
                        log.Hook = items[3].Substring(0, items[3].Length-1);

                        log.Func_name = get_func(items[5]);
                        if (is_entry(items[5]))
                            log.Func_params = get_func_params(items[5]);

                        else
                            log.Func_output = get_func_output(items[5]);

                        json_list.Add(JsonConvert.SerializeObject(log, Formatting.Indented));               

                    }
                }
            }
            write_json(json_list);
        }
        

        static void Main(string[] args)
        {
            string filename = "traces.txt";
            parse_logs(filename);
            
        }
    }
}
