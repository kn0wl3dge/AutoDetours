using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;
using System.Timers;

namespace AutoDetoursAgent
{
    public partial class AgentService : ServiceBase
    {
        private Timer timer_agent = new Timer();
        private Timer timer_trace = new Timer();

        private HttpClient client = new HttpClient();
        private Worker worker = new Worker();

        private bool readyForTracing = false;
        private bool isTracing = false;

        private Process syelogd = new Process();
        private Process withdll = new Process();

        private int traceCheckPeriod;


        public AgentService()
        {
            InitializeComponent();

            // Logging Set up
            if (!EventLog.SourceExists("AutoDetoursSource"))
            {
                EventLog.CreateEventSource(
                    "AutoDetoursSource", "AutoDetoursLog");
            }
            eventLog1.Source = "AutoDetoursSource";
            eventLog1.Log = "AutoDetoursLog";
        }

        protected override void OnStart(string[] args)
        {
            // Set up a timer
            //apiCheckPeriod = int.Parse(JsonConvert.DeserializeObject<WorkerTask>(resp).time) * 100;
            timer_agent.Interval = Constants.agentCheckPeriod;
            timer_agent.Elapsed += new ElapsedEventHandler(OnTimerCheckAgent);
            timer_agent.Start();
            //eventLog1.WriteEntry("Timer set to : " + apiCheckPeriod / 100 + "s");

            // Set up HTTP Client
            client.BaseAddress = new Uri(Constants.apiBaseURL);
            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            client.Timeout = TimeSpan.FromSeconds(5);

            // Init Worker
            worker.id = "";
            worker.state = "";
            worker.malware = "";

            // Logging
            eventLog1.WriteEntry("AutoDetours service started.");
        }

        protected override void OnStop()
        {
            // Logging
            eventLog1.WriteEntry("AutoDetours service stopped.");
        }

        private async Task<bool> RegisterWorker()
        {
            eventLog1.WriteEntry("Trying to register");
            HttpResponseMessage response = null;
            // Make post request to /workers/
            try
            {
                response = await client.PostAsync(
                    "workers/",
                    new StringContent("{}", Encoding.UTF8, "application/json")
                );
            }
            catch (Exception)
            {

            }
            
            // If everything is okay
            if (response != null && response.IsSuccessStatusCode)
            {
                // Get response data as a String
                String resp = await response.Content.ReadAsStringAsync();

                // Deserialize the JSON to get a Worker obejct
                worker = JsonConvert.DeserializeObject<Worker>(resp);
                worker.malware = "";

                eventLog1.WriteEntry("Successfully registered as worker : " + worker.id);

                return true;
            }
            eventLog1.WriteEntry("Wasn't able to register worker");
            return false;
        }

        private async Task<bool> GetTask()
        {
            eventLog1.WriteEntry("Trying to get task");
            HttpResponseMessage response = null;
            // Make get request to /workers/{id}
            try
            {
                response = await client.GetAsync("workers/" + worker.id + "/get_task/");
            }
            catch (Exception)
            {

            }

            // If everything is okay
            if (response != null && response.IsSuccessStatusCode)
            {
                // Get response data as a String
                String resp = await response.Content.ReadAsStringAsync();

                if (!resp.Contains("error"))
                {
                    // Deserialize the JSON to get a Worker obejct
                    worker.malware = JsonConvert.DeserializeObject<WorkerTask>(resp).malware;
                    eventLog1.WriteEntry("Agent is now tasked with sample : " + worker.malware);

                    traceCheckPeriod = int.Parse(JsonConvert.DeserializeObject<WorkerTask>(resp).time) * 100;
                    timer_trace.Interval = traceCheckPeriod;
                    timer_trace.Elapsed += new ElapsedEventHandler(OnTimerCheckTrace);
                    timer_trace.Start();
                    eventLog1.WriteEntry("Trace duration set to : " + traceCheckPeriod / 100 + "s");
                    return true;
                }
            }
            eventLog1.WriteEntry("No task available");
            return false;
        }

        private void DownloadMalware()
        {
            // Compute download URL
            StringBuilder url = new StringBuilder();
            url.Append(Constants.apiBaseURL);
            url.Append("malwares/");
            url.Append(worker.malware);
            url.Append("/download/");

            eventLog1.WriteEntry("Downloading file at " + url.ToString());

            // Download and save sample to C:/Temp/sample.exe
            // TODO : Maybe add a try/catch in case the API go down
            WebClient downloader = new WebClient();
            downloader.DownloadFile(url.ToString(), "C:\\Temp\\sample.exe");

            eventLog1.WriteEntry("Sample " + worker.malware + "has been downloaded.");
        }

        private void StartTracing()
        {
            // Run Syelog Deamon to extract logs from traceapi32
            syelogd.StartInfo.FileName = "C:\\Temp\\syelogd.exe";
            syelogd.StartInfo.Arguments = "/o C:\\Temp\\traces.txt";
            syelogd.Start();

            // We inject Traceapi DLL into the malware process using withdll.exe
            withdll.StartInfo.FileName = "C:\\Temp\\withdll.exe";
            withdll.StartInfo.Arguments = "/d:C:\\Temp\\trcapi32.dll C:\\Temp\\sample.exe";
            withdll.Start();
        }

        private void StopTracing()
        {
            //if (!withdll.HasExited)
            withdll.Kill();
            if (!syelogd.HasExited)
                syelogd.Kill();
        }

        private string ParseResults()
        {
            string inputFilename = "C:\\Temp\\traces.txt";
            string outputFilename = "C:\\Temp\\logs.json";
            string logs = Parser.ParseLogs(inputFilename, outputFilename);
            eventLog1.WriteEntry(logs);
            return logs;
        }

        private async Task SubmitTask(string jsonLogs)
        {
            string url = "workers/" + worker.id + "/submit_task/";
            HttpResponseMessage response = null;
            try
            {
                response = await client.PostAsync(url, new StringContent(jsonLogs, Encoding.UTF8, "application/json"));
            }
            catch (Exception ex)
            {

            }

            if (response != null && response.IsSuccessStatusCode)
                eventLog1.WriteEntry("Task successfully submitted.");
        }

        private async void OnTimerCheckAgent(object source, ElapsedEventArgs e)
        {
            if (!readyForTracing)
            {
                // If no task are defined, check if agent is registered and request a task
                if (worker.malware == "")
                {
                    // If worker isn't registered
                    if (worker.id == "")
                        await RegisterWorker();

                    // If worker is now registered (or previously)
                    if (worker.id != "")
                        await GetTask();
                }
                // Not an else because task could be assigned in the previous condition
                if (worker.malware != "")
                {
                    DownloadMalware();
                    readyForTracing = true;
                }
            }
        }

        private async void OnTimerCheckTrace(object source, ElapsedEventArgs e)
        { 
            // Launch the process the first time
            if (readyForTracing && !isTracing)
            {
                StartTracing();
                isTracing = true;
            }
            // Kill it at the second timer iteration(after 30 sec)
            else if (isTracing) {
                StopTracing();
                string logs = ParseResults();
                await SubmitTask(logs);
                ServiceController control = new ServiceController(ServiceName);
                control.Stop();
                // /!\ We should poweroff the VM instead of stopping the service /!\
            }
        }
    }

    public class Constants
    {
        static public string apiBaseURL = "http://192.168.208.1/api/"; // CHANGE ME to docker host address. Maybe this will be fixed with container DNS
        static public int agentCheckPeriod = 30000;
    }

    public class Worker
    {
        public String id { get; set; }
        public String state { get; set; }
        public String malware { get; set; }
    }

    public class WorkerTask
    {
        public String malware { get; set; }
        public String time { get; set; }
    }
}
