using System;
using System.Diagnostics;
using System.Net.Http;
using System.Threading.Tasks;

namespace AutoDetoursAgent
{
	public abstract class Job
	{
		protected Logger logger;
		protected WorkerTask workerTask;
		public Job(Logger _logger, WorkerTask _workerTask)
		{
			logger = _logger;
			workerTask = _workerTask;
		}

		public abstract void StartJob();
		public abstract void StopJob();

		public abstract void TreatResults();

		// Must be async when implementing this method
		public abstract Task<bool> SubmitResults(String workerId, HttpClient client);
	}
}