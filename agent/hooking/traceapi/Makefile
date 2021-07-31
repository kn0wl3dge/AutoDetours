##############################################################################
##
##  Utility to trace Win32 APIs.
##
##  Microsoft Research Detours Package
##
##  Copyright (c) Microsoft Corporation.  All rights reserved.
##

!include ..\common.mak

#BIND = bin.$(DETOURS_TARGET_PROCESSOR)$(DETOURS_CONFIG)
LIBS=$(LIBS) kernel32.lib gdi32.lib user32.lib shell32.lib advapi32.lib ole32.lib ws2_32.lib

##############################################################################

all: dirs \
    $(BIND)\trcapi$(DETOURS_BITS).dll 

##############################################################################

clean:
    -del *~ test.txt 2>nul
    -del $(BIND)\trcapi*.* 2>nul
    -rmdir /q /s $(OBJD) 2>nul

realclean: clean
    -rmdir /q /s $(OBJDS) 2>nul

dirs:
    @if not exist $(BIND) mkdir $(BIND) && echo.   Created $(BIND)
    @if not exist $(OBJD) mkdir $(OBJD) && echo.   Created $(OBJD)

$(OBJD)\trcapi.obj : trcapi.cpp _win32.cpp

$(OBJD)\trcapi.res : trcapi.rc

$(BIND)\trcapi$(DETOURS_BITS).dll: $(OBJD)\trcapi.obj $(OBJD)\trcapi.res $(DEPS)
    cl /LD $(CFLAGS) /Fe$@ /Fd$(@R).pdb \
        $(OBJD)\trcapi.obj $(OBJD)\trcapi.res \
        /link $(LINKFLAGS) /release /subsystem:console \
        /export:DetourFinishHelperProcess,@1,NONAME \
        $(LIBS)
