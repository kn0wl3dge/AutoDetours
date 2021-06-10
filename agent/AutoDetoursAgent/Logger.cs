using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AutoDetoursAgent
{
    public class Logger
    {
        private EventLog eventLog;
        public Logger(EventLog _eventLog)
        {
            eventLog = _eventLog;
        }

        public void Log(String msg)
        {
            eventLog.WriteEntry(msg);
            // For debugging inside VS
            Console.WriteLine(msg);
        }
    }
}
