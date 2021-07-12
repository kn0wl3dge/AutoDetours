# AgentService

This is the agent running on windows sandbox where the malware are executed.  
It is runnning in a Service as LocalSystem.  

The agent is linked to the wokers API so it can resgiter, find a task and submit the results.

# Build

* Load the project to Visual Studio
* Build the solution

# Install

* Open VS Console as Administrator
* Run the following command ```InstallUtil AutoDetoursAgent.exe```

# Uninstall

* Open VS Console as Administrator
* Run the following command ```InstallUtil /u AutoDetoursAgent.exe```