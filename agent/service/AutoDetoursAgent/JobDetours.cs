using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace AutoDetoursAgent
{
    public class JobDetours : Job
    {
        private Process withdll = new Process();

        private String defaultPathTraces = "C:\\Temp\\traces.jsonl";

        public JobDetours(Logger logger, WorkerTask wt) : base(logger, wt)
        {
        }

        public override void ExecuteJob()
        {
            logger.Log("Starting Tracing...");

            withdll.StartInfo.FileName = "C:\\Temp\\withdll.exe";

            // We inject Traceapi DLL into the malware process using withdll.exe
            if (workerTask.format != "dll")
                withdll.StartInfo.Arguments = "/d:C:\\Temp\\trcapi32.dll C:\\Temp\\sample.exe";

            // In case of a DLL we use RunDLL32 to launch the DLL
            else
                withdll.StartInfo.Arguments = "/d:C:\\Temp\\trcapi32.dll rundll32.exe C:\\Temp\\sample.dll," + workerTask.exportName;

            withdll.Start();

            logger.Log("Tracing started.");
            
            withdll.WaitForExit(workerTask.time * 1000);
                
            logger.Log("Tracing stopped");

            // Let's sleep a while before sending results (file is not created quickly)
            Thread.Sleep(1000);
        }

        public override void TreatResults()
        {

        }

        public override async Task<bool> SubmitResults(String workerId, HttpClient client)
        {
            logger.Log("Submitting results...");
            // Submit JSON results to the API
            string url = "workers/" + workerId + "/submit_task/";
            HttpResponseMessage response = null;
            var byteArray = File.ReadAllBytes(defaultPathTraces);
            var form = new MultipartFormDataContent();
            form.Add(new ByteArrayContent(byteArray, 0, byteArray.Length), "results", "traces.jsonl");
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
