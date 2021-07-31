# Hooking

We are using Microsoft Detours framework to easily hook the Win32 API.
Detours is imported as a submodule and traceapi is providing a DLL using the Detours framework.

# Build

Just use the following command to build the hooking module dependancies:  
```
nmake
```