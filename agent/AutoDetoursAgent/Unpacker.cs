using AutoDetoursAgent;
using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using st = System.Threading;
public class Unpacker : Job
{
	private Process malunpack = new Process();
	private Process tar = new Process();

	private String defaultPathZip = "C:\\Temp\\unpacked.zip";

	public Unpacker(EventLog eventLog, WorkerTask wt) : base(eventLog, wt)
	{
	}

    public override void StartJob()
    {
        eventLog.WriteEntry("Unpacking starting...");

        // Run Syelog Deamon to extract logs from traceapi32
        malunpack.StartInfo.FileName = "C:\\Temp\\mal_unpack.exe";
        malunpack.StartInfo.Arguments = "/exe C:\\Temp\\sample.exe /dir C:\\Temp\\unpacked /timeout " + (workerTask.time * 1000);
        malunpack.Start();
    }

    public override void StopJob()
    {
        eventLog.WriteEntry("Stopping unpacking...");
        // Stop both processes
        if (!malunpack.HasExited)
            malunpack.Kill();
    }

    // Compress mal_unpack results
    public override void TreatResults()
    {
        tar.StartInfo.FileName = "C:\\Program Files\\7-Zip\\7z.exe";
        tar.StartInfo.Arguments = "a " + defaultPathZip + " C:\\Temp\\unpacked";
        tar.Start();

        st.Thread.Sleep(3000);
        eventLog.WriteEntry("Results compressed.");
        System.Console.WriteLine("Results compressed.");
    }

    public override async Task<bool> SubmitResults(String workerId, HttpClient client)
    {
        // Submit ZIP results to the API
        string url = "workers/" + workerId + "/submit_task/";
        HttpResponseMessage response = null;
        var byteArray = File.ReadAllBytes(defaultPathZip);
        var form = new MultipartFormDataContent();
        form.Add(new ByteArrayContent(byteArray, 0, byteArray.Length), "results", "unpacked.zip");
        try
        {
            // TODO : Here send zip (modify app type + update endpoint)
            System.Console.WriteLine("Submitting zip.");
            response = await client.PostAsync(url, form);
        }
        catch (Exception)
        {

        }

        if (response != null && response.IsSuccessStatusCode)
        {
            eventLog.WriteEntry("ZIP successfully submitted.");
            System.Console.WriteLine("ZIP succesfully submitted.");
            return true;
        }
        return false;
    }
}
