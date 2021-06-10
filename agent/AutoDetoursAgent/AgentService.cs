using Newtonsoft.Json;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;
using System.Timers;
using st = System.Threading;

namespace AutoDetoursAgent
{
    public partial class AgentService : ServiceBase
    {
        private Timer timer_agent = new Timer();

        private HttpClient client = new HttpClient();
        private Worker worker = new Worker();
        private WorkerTask workerTask = new WorkerTask();
        private AgentState state = AgentState.INIT;

        private bool customMutex = true;
        private bool isVM;

        private String apiBaseURL;

        private Job job;

        private Logger logger;

        public AgentService()
        {
            InitializeComponent();

            // Logging Set up
            if (!EventLog.SourceExists("AutoDetoursSource"))
            {
                EventLog.CreateEventSource(
                    "AutoDetoursSource", "AutoDetoursLog");
            }
            eventLog.Source = "AutoDetoursSource";
            eventLog.Log = "AutoDetoursLog";
            logger = new Logger(eventLog);
        }

        public void OnDebug()
        {
            OnStart(null);
        }

        protected override void OnStart(string[] args)
        {
            // Set up a timer
            timer_agent.Interval = 10000;
            timer_agent.Elapsed += new ElapsedEventHandler(OnTimerCheckAgent);
            timer_agent.Start();

            // Easier to edit a txt file than rebuild all the agent
            string path = @"C:\Temp\agent\api.txt";
            if (File.Exists(path))
            {
                apiBaseURL = File.ReadAllText(path).Replace("\r", "").Replace("\n", "");
                if (apiBaseURL.Last() != '/')
                {
                    apiBaseURL += '/';
                }
            }
            else
            {
                apiBaseURL = "http://172.20.0.10/api/"; // Don't change me! Check out api.txt
            }
            logger.Log("AutoDetours API is located at : " + apiBaseURL);

            // Check if it's a VM
            if (File.Exists(@"C:\Temp\agent\vm.txt"))
            {
                isVM = true;
            }

            // Set up HTTP Client
            client.BaseAddress = new Uri(apiBaseURL);
            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            client.Timeout = TimeSpan.FromSeconds(5);

            // Init Worker
            worker.id = "";
            worker.malware = "";

            // Logging
            logger.Log("AutoDetours service started.");
        }

        protected override void OnStop()
        {
            // Logging
            logger.Log("AutoDetours service stopped.");
        }

        private async Task<bool> RegisterWorker()
        {
            logger.Log("Trying to register");
            String uuid = Guid.NewGuid().ToString();
            HttpResponseMessage response = null;
            // Make post request to /workers/
            try
            {
                response = await client.PostAsync(
                    "workers/",
                    new StringContent("{\"id\":\"" + uuid +"\"}", Encoding.UTF8, "application/json")
                );
            }
            catch (Exception)
            {

            }

            // If everything is okay
            if (response != null && response.IsSuccessStatusCode)
            {
                worker.id = uuid;
                logger.Log("Successfully registered as worker : " + worker.id);
                return true;
            }
            logger.Log("Wasn't able to register worker");
            return false;
        }

        private async Task<bool> GetTask()
        {
            logger.Log("Trying to get task");
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
                    workerTask = JsonConvert.DeserializeObject<WorkerTask>(resp);
                    worker.malware = workerTask.malware;

                    // Set Job according to task
                    if (workerTask.task == "unpack")
                        job = new Unpacker(eventLog, workerTask);
                    else
                        job = new Tracer(logger, workerTask);

                    logger.Log("Agent is now tasked with sample : " + worker.malware);
                    return true;
                }
            }
            logger.Log("No task available");
            return false;
        }

        private bool DownloadMalware()
        {
            // Compute download URL
            StringBuilder url = new StringBuilder();
            url.Append(apiBaseURL);
            url.Append("malwares/");
            url.Append(worker.malware);
            url.Append("/download/");

            logger.Log("Downloading file at " + url.ToString());

            String filename = null;
            if (workerTask.format == "exe")
                filename = "C:\\Temp\\sample.exe";
            else
                filename = "C:\\Temp\\sample.dll";

            // Download and save sample to C:/Temp/sample.exe
            WebClient downloader = new WebClient();
            try
            {
                downloader.DownloadFile(url.ToString(), filename);
            }
            catch (Exception)
            {
                return false;
            }

            logger.Log("Sample " + worker.malware + "has been downloaded.");
            return true;
        }

        private async Task<bool> Cleanup()
        {
            // Make a DELETE request to remove the worker
            string url = "workers/" + worker.id + "/";
            HttpResponseMessage response = null;
            try
            {
                response = await client.DeleteAsync(url);
            }
            catch (Exception)
            {

            }

            if (response != null && response.IsSuccessStatusCode)
            {
                logger.Log("Worker cleaned up!");
                return true;
            }
            return false;
        }

        private async Task<bool> HealthCheck()
        {
            HttpResponseMessage response = null;
            try
            {
                response = await client.GetAsync("");
            }
            catch (Exception)
            {

            }

            if (response != null && response.StatusCode == HttpStatusCode.OK)
            {
                logger.Log("The API is available!");
                return true;
            }
            return false;
        }

        private async void OnTimerCheckAgent(object source, ElapsedEventArgs e)
        {
            if (customMutex)
            {
                customMutex = false;
                switch (state)
                {
                    case AgentState.INIT:
                        if (await HealthCheck())
                        {
                            state = AgentState.REGISTER;
                            goto case AgentState.REGISTER;
                        }
                        break;

                    case AgentState.REGISTER:
                        if (await RegisterWorker())
                        {
                            state = AgentState.GET_TASK;
                            goto case AgentState.GET_TASK;
                        }
                        break;

                    case AgentState.GET_TASK:
                        if (await GetTask())
                        {
                            state = AgentState.DOWNLOAD_SAMPLE;
                            goto case AgentState.DOWNLOAD_SAMPLE;
                        }
                        break;

                    case AgentState.DOWNLOAD_SAMPLE:
                        if (DownloadMalware())
                        {
                            state = AgentState.JOB;
                            goto case AgentState.JOB;
                        }
                        break;

                    case AgentState.JOB:
                        job.StartJob();
                        st.Thread.Sleep(workerTask.time * 1000);

                        job.StopJob();
                        state = AgentState.SEND_RESULTS;
                        goto case AgentState.SEND_RESULTS;

                    case AgentState.SEND_RESULTS:

                        job.TreatResults();
                        if (await job.SubmitResults(worker.id, client))
                        {
                            state = AgentState.CLEANUP;
                            goto case AgentState.CLEANUP;
                        }
                        break;

                    case AgentState.CLEANUP:
                        if (await Cleanup())
                        {
                            state = AgentState.DONE;
                            goto case AgentState.DONE;
                        }
                        break;

                    case AgentState.DONE:
                        // Quitting properly when debugging in VS
                        #if DEBUG
                            System.Environment.Exit(0);
                        #endif
                        if (isVM)
                        {
                            Process.Start("shutdown", "/s /t 0");
                        }
                        else
                        {
                            ServiceController control = new ServiceController(ServiceName);
                            control.Stop();
                        }
                        break;
                }
                customMutex = true;
            }
        }
    }

    enum AgentState
    {
        INIT,
        REGISTER,
        GET_TASK,
        DOWNLOAD_SAMPLE,
        JOB,
        SEND_RESULTS,
        CLEANUP,
        DONE
    }

    public class Worker
    {
        public String id { get; set; }
        public String malware { get; set; }
    }

    public class WorkerTask
    {
        public String malware { get; set; }
        public int time { get; set; }
        public string format { get; set; }
        public string task { get; set; }
        public string exportName { get; set; }
    }
}

