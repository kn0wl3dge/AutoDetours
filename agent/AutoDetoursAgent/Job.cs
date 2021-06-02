using AutoDetoursAgent;
using System;
using System.Diagnostics;
using System.Net.Http;
using System.Threading.Tasks;

public abstract class Job
{

	protected EventLog eventLog;
	protected WorkerTask workerTask;
	public Job(EventLog _eventLog, WorkerTask wt)
	{
		eventLog = _eventLog;
		workerTask = wt;
	}

	public abstract void StartJob();
	public abstract void StopJob();

	public abstract void TreatResults();

	// Must be async when implementing this method
	public abstract Task<bool> SubmitResults(String workerId, HttpClient client);
}
