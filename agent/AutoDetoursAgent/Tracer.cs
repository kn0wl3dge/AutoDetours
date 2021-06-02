using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using st = System.Threading;

namespace AutoDetoursAgent
{
    public class Tracer : Job
    {
        private Process syelogd = new Process();
        private Process withdll = new Process();

        // Stores logs after parsing
        private string logs;

        public Tracer(Logger logger, WorkerTask wt) : base(logger, wt)
        {
        }

        public override void StartJob()
        {
            logger.Log("Starting Tracing...");
            // Run Syelog Deamon to extract logs from traceapi32
            syelogd.StartInfo.FileName = "C:\\Temp\\syelogd.exe";
            syelogd.StartInfo.Arguments = "/o C:\\Temp\\traces.txt";
            syelogd.Start();

            withdll.StartInfo.FileName = "C:\\Temp\\withdll.exe";

            // We inject Traceapi DLL into the malware process using withdll.exe
            if (workerTask.isDll == false)
                withdll.StartInfo.Arguments = "/d:C:\\Temp\\trcapi32.dll C:\\Temp\\sample.exe";

            // In case of a DLL we use RunDLL32 to launch the DLL
            else
                withdll.StartInfo.Arguments = "/d:C:\\Temp\\trcapi32.dll rundll32.exe C:\\Temp\\sample.dll," + workerTask.exportName;

            withdll.Start();

            logger.Log("Tracing started.");
        }

        public override void StopJob()
        {
            logger.Log("Stopping tracing...");
            // Stop both processes
            if (!withdll.HasExited)
                withdll.Kill();
            if (!syelogd.HasExited)
                syelogd.Kill();

            logger.Log("Tracing stopped");
        }

        public override void TreatResults()
        {
            logger.Log("Starting parsing...");
            // Convert the traces.txt to json format
            string inputFilename = "C:\\Temp\\traces.txt";
            logs = Parser.ParseLogs(inputFilename);
            logger.Log("Json output has been generated.");
        }

        public override async Task<bool> SubmitResults(String workerId, HttpClient client)
        {
            logger.Log("Submitting results...");
            // Submit JSON results to the API
            string url = "workers/" + workerId + "/submit_task/";
            HttpResponseMessage response = null;
            var form = new MultipartFormDataContent();
            var byteArray = Encoding.UTF8.GetBytes(logs);
            form.Add(new ByteArrayContent(byteArray, 0, byteArray.Length), "results", "traces.json");
            try
            {
                response = await client.PostAsync(url, form);
            }
            catch (Exception)
            {

            }

            if (response != null && response.IsSuccessStatusCode)
            {
                logger.Log("Task successfully submitted.");
                return true;
            }
            return false;
        }
    }
}