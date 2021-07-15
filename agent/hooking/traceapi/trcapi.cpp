//////////////////////////////////////////////////////////////////////////////
//
//  Detours Test Program (trcapi.cpp of trcapi.dll)
//
//  Microsoft Research Detours Package
//
//  Copyright (c) Microsoft Corporation.  All rights reserved.
//
#undef WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT        0x400
#define WIN32
#define NT
#define _WINSOCK_DEPRECATED_NO_WARNINGS

#define DBG_TRACE   0

#if _MSC_VER >= 1300
#include <winsock2.h>
#endif
#include <windows.h>
#include <stdio.h>
#pragma warning(push)
#if _MSC_VER > 1400
#pragma warning(disable:6102 6103) // /analyze warnings
#endif
#include <strsafe.h>
#pragma warning(pop)
#include "detours.h"
#include "syelog.h"

#if (_MSC_VER < 1299)
#define LONG_PTR    LONG
#define ULONG_PTR   ULONG
#define PLONG_PTR   PLONG
#define PULONG_PTR  PULONG
#define INT_PTR     INT
#define UINT_PTR    UINT
#define PINT_PTR    PINT
#define PUINT_PTR   PUINT
#define DWORD_PTR   DWORD
#define PDWORD_PTR  PDWORD
#endif

#pragma warning(disable:4996)   // We don't care about deprecated APIs.

//////////////////////////////////////////////////////////////////////////////
#pragma warning(disable:4127)   // Many of our asserts are constants.

#define ASSERT_ALWAYS(x)   \
    do {                                                        \
    if (!(x)) {                                                 \
            AssertMessage(#x, __FILE__, __LINE__);              \
            DebugBreak();                                       \
    }                                                           \
    } while (0)

#ifndef NDEBUG
#define ASSERT(x)           ASSERT_ALWAYS(x)
#else
#define ASSERT(x)
#endif

#define UNUSED(c)    (c) = (c)

//////////////////////////////////////////////////////////////////////////////
static HMODULE s_hInst = NULL;
static WCHAR s_wzDllPath[MAX_PATH];
static CHAR s_szDllPath[MAX_PATH];

BOOL ProcessEnumerate();
BOOL InstanceEnumerate(HINSTANCE hInst);

CHAR *escapeStr(LPCSTR input);
CHAR* escapeStr(LPCWSTR input);
VOID _PrintHook(const CHAR *psz, ...);

VOID AssertMessage(CONST PCHAR pszMsg, CONST PCHAR pszFile, ULONG nLine);

//////////////////////////////////////////////////////////////////////////////
//
// Trampolines
//
extern "C" {
    //  Trampolines for SYELOG library.
    //
    extern HANDLE (WINAPI *Real_CreateFileW)(LPCWSTR a0, DWORD a1, DWORD a2,
                                             LPSECURITY_ATTRIBUTES a3, DWORD a4, DWORD a5,
                                             HANDLE a6);
    extern BOOL (WINAPI *Real_WriteFile)(HANDLE hFile,
                                         LPCVOID lpBuffer,
                                         DWORD nNumberOfBytesToWrite,
                                         LPDWORD lpNumberOfBytesWritten,
                                         LPOVERLAPPED lpOverlapped);
    extern BOOL (WINAPI *Real_FlushFileBuffers)(HANDLE hFile);
    extern BOOL (WINAPI *Real_CloseHandle)(HANDLE hObject);
    extern BOOL (WINAPI *Real_WaitNamedPipeW)(LPCWSTR lpNamedPipeName, DWORD nTimeOut);
    extern BOOL (WINAPI *Real_SetNamedPipeHandleState)(HANDLE hNamedPipe,
                                                       LPDWORD lpMode,
                                                       LPDWORD lpMaxCollectionCount,
                                                       LPDWORD lpCollectDataTimeout);
    extern DWORD (WINAPI *Real_GetCurrentProcessId)(VOID);
    extern VOID (WINAPI *Real_GetSystemTimeAsFileTime)(LPFILETIME lpSystemTimeAsFileTime);

    VOID ( WINAPI * Real_InitializeCriticalSection)(LPCRITICAL_SECTION lpSection)
        = InitializeCriticalSection;
    VOID ( WINAPI * Real_EnterCriticalSection)(LPCRITICAL_SECTION lpSection)
        = EnterCriticalSection;
    VOID ( WINAPI * Real_LeaveCriticalSection)(LPCRITICAL_SECTION lpSection)
        = LeaveCriticalSection;
}

#include "_win32.cpp"

////////////////////////////////////////////////////////////// Logging System.
//
static BOOL s_bLog = FALSE;
static LONG s_nTlsIndent = -1;
static LONG s_nTlsThread = -1;
static LONG s_nThreadCnt = 0;

static HANDLE logFileHandle = NULL;

size_t to_narrow(const wchar_t* src, LPSTR dest, size_t dest_len) {
    size_t i;
    wchar_t code;

    i = 0;

    while (src[i] != '\0' && i < (dest_len - 1)) {
        code = src[i];
        if (code < 128)
            dest[i] = char(code);
        else {
            dest[i] = '?';
            if (code >= 0xD800 && code <= 0xD8FF)
                // lead surrogate, skip the next code unit, which is the trail
                i++;
        }
        i++;
    }

    dest[i] = '\0';

    return i - 1;

}

/* Adapted from https://github.com/DaveGamble/cJSON/blob/master/cJSON.c */
CHAR* escapeStr(LPCWSTR input)
{
    size_t len = wcslen(input) + 1;
    LPSTR dest = (LPSTR)malloc(len);
    to_narrow(input, dest, len);
    CHAR *r = escapeStr(dest);
    free(dest);
    return r;
}

/* Adapted from https://github.com/DaveGamble/cJSON/blob/master/cJSON.c */
CHAR *escapeStr(LPCSTR input)
{
    const char* input_pointer = NULL;
    char* output = NULL;
    char* output_pointer = NULL;
    size_t output_length = 0;
    /* numbers of additional characters needed for escaping */
    size_t escape_characters = 0;

    CHAR* output_buffer = (char*)malloc(1024);

    if (output_buffer == NULL)
    {
        return NULL;
    }

    /* empty string */
    if (input == NULL)
    {
        strcpy((char*)output_buffer, "\0");
        return output_buffer;
    }

    /* set "flag" to 1 if something needs to be escaped */
    for (input_pointer = input; *input_pointer; input_pointer++)
    {
        switch (*input_pointer)
        {
        case '\"':
        case '\\':
        case '\b':
        case '\f':
        case '\n':
        case '\r':
        case '\t':
            /* one character escape sequence */
            escape_characters++;
            break;
        default:
            if (*input_pointer < 32)
            {
                /* UTF-16 escape sequence uXXXX */
                escape_characters += 5;
            }
            break;
        }
    }
    output_length = (size_t)(input_pointer - input) + escape_characters;

    output = (char*)realloc(output_buffer, output_length + 1);
    if (output == NULL)
    {
        return NULL;
    }

    /* no characters have to be escaped */
    if (escape_characters == 0)
    {
        memcpy(output, input, output_length);
        output[output_length] = '\0';
        return output;
    }

    output_pointer = output;
    /* copy the string */
    for (input_pointer = input; *input_pointer != '\0'; (void)input_pointer++, output_pointer++)
    {
        if ((*input_pointer > 31) && (*input_pointer != '\"') && (*input_pointer != '\\'))
        {
            /* normal character, copy */
            *output_pointer = *input_pointer;
        }
        else
        {
            /* character needs to be escaped */
            *output_pointer++ = '\\';
            switch (*input_pointer)
            {
            case '\\':
                *output_pointer = '\\';
                break;
            case '\"':
                *output_pointer = '\"';
                break;
            case '\b':
                *output_pointer = 'b';
                break;
            case '\f':
                *output_pointer = 'f';
                break;
            case '\n':
                *output_pointer = 'n';
                break;
            case '\r':
                *output_pointer = 'r';
                break;
            case '\t':
                *output_pointer = 't';
                break;
            default:
                /* escape and print as unicode codepoint */
                sprintf((char*)output_pointer, "u%04x", *input_pointer);
                output_pointer += 4;
                break;
            }
        }
    }
    output[output_length] = '\0';

    return output;
}

VOID _PrintHook(const CHAR* psz, ...)
{
    DWORD dwErr = GetLastError();

    LONG nThread = 0;
    if (s_nTlsThread >= 0) {
        nThread = (LONG)(LONG_PTR)TlsGetValue(s_nTlsThread);
    }

    if (s_bLog && psz) {
        FILETIME ft;
        LARGE_INTEGER li;

        /* Get the amount of 100 nano seconds intervals elapsed since January 1, 1601 (UTC) and copy it
         * to a LARGE_INTEGER structure. */
        Real_GetSystemTimeAsFileTime(&ft);
        li.LowPart = ft.dwLowDateTime;
        li.HighPart = ft.dwHighDateTime;

        UINT64 timestamp = li.QuadPart;
        timestamp -= 116444736000000000LL; /* Convert from file time to UNIX epoch time. */
        timestamp /= 10000; /* From 100 nano seconds (10^-7) to 1 millisecond (10^-3) intervals */

        CHAR szBuf[2048] = { 0 };
        CHAR fmt_s[] = "{\"type\": \"hook\", \"timestamp\": %lld, \"thread\": %ld, ";
        sprintf(szBuf, fmt_s, timestamp, nThread);


        PCHAR pszEnd = szBuf + ARRAYSIZE(szBuf) - 1;
        PCHAR pszBuf = szBuf + strlen(szBuf);

        va_list  args;
        va_start(args, psz);

        while ((*pszBuf++ = *psz++) != 0 && pszBuf < pszEnd) {
            // Copy characters.
        }
        *pszEnd = '\0';
        //SyelogV(SYELOG_SEVERITY_INFORMATION, szBuf, args);
        CHAR finalBuf[2048] = { 0 };
        vsprintf(finalBuf, szBuf, args);

        va_end(args);

        DWORD dwBytesWritten = 0;

        Real_WriteFile(
            logFileHandle,           // open file handle
            finalBuf,      // start of data to write
            strlen(finalBuf),  // number of bytes to write
            &dwBytesWritten, // number of bytes that were written
            NULL);            // no overlapped structure
    }
    SetLastError(dwErr);
}

VOID AssertMessage(CONST PCHAR pszMsg, CONST PCHAR pszFile, ULONG nLine)
{
    Syelog(SYELOG_SEVERITY_FATAL,
           "ASSERT(%s) failed in %s, line %d.\n", pszMsg, pszFile, nLine);
}

//////////////////////////////////////////////////////////////////////////////
//
PIMAGE_NT_HEADERS NtHeadersForInstance(HINSTANCE hInst)
{
    PIMAGE_DOS_HEADER pDosHeader = (PIMAGE_DOS_HEADER)hInst;
    __try {
        if (pDosHeader->e_magic != IMAGE_DOS_SIGNATURE) {
            SetLastError(ERROR_BAD_EXE_FORMAT);
            return NULL;
        }

        PIMAGE_NT_HEADERS pNtHeader = (PIMAGE_NT_HEADERS)((PBYTE)pDosHeader +
                                                          pDosHeader->e_lfanew);
        if (pNtHeader->Signature != IMAGE_NT_SIGNATURE) {
            SetLastError(ERROR_INVALID_EXE_SIGNATURE);
            return NULL;
        }
        if (pNtHeader->FileHeader.SizeOfOptionalHeader == 0) {
            SetLastError(ERROR_EXE_MARKED_INVALID);
            return NULL;
        }
        return pNtHeader;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
    }
    SetLastError(ERROR_EXE_MARKED_INVALID);

    return NULL;
}

BOOL InstanceEnumerate(HINSTANCE hInst)
{
    WCHAR wzDllName[MAX_PATH];

    PIMAGE_NT_HEADERS pinh = NtHeadersForInstance(hInst);
    if (pinh && Real_GetModuleFileNameW(hInst, wzDllName, ARRAYSIZE(wzDllName))) {
        Syelog(SYELOG_SEVERITY_INFORMATION, "### %p: %ls\n", hInst, wzDllName);
        return TRUE;
    }
    return FALSE;
}

BOOL ProcessEnumerate()
{
    DWORD dwBytesWritten = 0;

    PBYTE pbNext;
    for (PBYTE pbRegion = (PBYTE)0x10000;; pbRegion = pbNext) {
        MEMORY_BASIC_INFORMATION mbi;
        ZeroMemory(&mbi, sizeof(mbi));

        if (VirtualQuery((PVOID)pbRegion, &mbi, sizeof(mbi)) <= 0) {
            break;
        }
        pbNext = (PBYTE)mbi.BaseAddress + mbi.RegionSize;

        // Skip free regions, reserver regions, and guard pages.
        //
        if (mbi.State == MEM_FREE || mbi.State == MEM_RESERVE) {
            continue;
        }
        if (mbi.Protect & PAGE_GUARD || mbi.Protect & PAGE_NOCACHE) {
            continue;
        }
        if (mbi.Protect == PAGE_NOACCESS) {
            continue;
        }

        // Skip over regions from the same allocation...
        {
            MEMORY_BASIC_INFORMATION mbiStep;

            while (VirtualQuery((PVOID)pbNext, &mbiStep, sizeof(mbiStep)) > 0) {
                if ((PBYTE)mbiStep.AllocationBase != pbRegion) {
                    break;
                }
                pbNext = (PBYTE)mbiStep.BaseAddress + mbiStep.RegionSize;
                mbi.Protect |= mbiStep.Protect;
            }
        }

        WCHAR wzDllName[MAX_PATH];
        PIMAGE_NT_HEADERS pinh = NtHeadersForInstance((HINSTANCE)pbRegion);

        CHAR szBuf[2048] = { 0 };

        if (pinh &&
            Real_GetModuleFileNameW((HINSTANCE)pbRegion,wzDllName,ARRAYSIZE(wzDllName))) {

            CHAR* filename = escapeStr(wzDllName);
            sprintf(szBuf,
                   "{\"type\": \"memory_map\", \"begin_addr\":\"%p\", \"end_addr\": \"%p\", \"filename\": \"%hs\", \"state\": \"%04lx\", \"protect\": \"%08lx\"}\n", pbRegion, pbNext, filename, mbi.State, mbi.Protect);
            free(filename);
        }
        else {
            sprintf(szBuf,
                   "{\"type\": \"memory_map\", \"begin_addr\":\"%p\", \"end_addr\": \"%p\", \"filename\": \"\", \"state\": \"%04lx\", \"protect\": \"%08lx\"}\n",
                   pbRegion, pbNext, mbi.State, mbi.Protect);
        }

        Real_WriteFile(
            logFileHandle,           // open file handle
            szBuf,      // start of data to write
            strlen(szBuf),  // number of bytes to write
            &dwBytesWritten, // number of bytes that were written
            NULL);            // no overlapped structure
    }

    return TRUE;
}

//////////////////////////////////////////////////////////////////////////////
//
// DLL module information
//
BOOL ThreadAttach(HMODULE hDll)
{
    (void)hDll;

    if (s_nTlsIndent >= 0) {
        TlsSetValue(s_nTlsIndent, (PVOID)0);
    }
    if (s_nTlsThread >= 0) {
        LONG nThread = InterlockedIncrement(&s_nThreadCnt);
        TlsSetValue(s_nTlsThread, (PVOID)(LONG_PTR)nThread);
    }
    return TRUE;
}

BOOL ThreadDetach(HMODULE hDll)
{
    (void)hDll;

    if (s_nTlsIndent >= 0) {
        TlsSetValue(s_nTlsIndent, (PVOID)0);
    }
    if (s_nTlsThread >= 0) {
        TlsSetValue(s_nTlsThread, (PVOID)0);
    }
    return TRUE;
}

BOOL ProcessAttach(HMODULE hDll)
{
    s_bLog = FALSE;
    s_nTlsIndent = TlsAlloc();
    s_nTlsThread = TlsAlloc();
    ThreadAttach(hDll);

    WCHAR wzExeName[MAX_PATH];

    s_hInst = hDll;
    Real_GetModuleFileNameW(hDll, s_wzDllPath, ARRAYSIZE(s_wzDllPath));
    Real_GetModuleFileNameW(NULL, wzExeName, ARRAYSIZE(wzExeName));
    StringCchPrintfA(s_szDllPath, ARRAYSIZE(s_szDllPath), "%ls", s_wzDllPath);

    SyelogOpen("trcapi" DETOURS_STRINGIFY(DETOURS_BITS), SYELOG_FACILITY_APPLICATION);
    ProcessEnumerate();

    LONG error = AttachDetours();
    if (error != NO_ERROR) {
        Syelog(SYELOG_SEVERITY_FATAL, "### Error attaching detours: %d\n", error);
    }

    s_bLog = TRUE;
    return TRUE;
}

BOOL ProcessDetach(HMODULE hDll)
{
    ThreadDetach(hDll);
    s_bLog = FALSE;

    LONG error = DetachDetours();
    if (error != NO_ERROR) {
        Syelog(SYELOG_SEVERITY_FATAL, "### Error detaching detours: %d\n", error);
    }

    Syelog(SYELOG_SEVERITY_NOTICE, "### Closing.\n");
    SyelogClose(FALSE);

    if (s_nTlsIndent >= 0) {
        TlsFree(s_nTlsIndent);
    }
    if (s_nTlsThread >= 0) {
        TlsFree(s_nTlsThread);
    }
    return TRUE;
}

BOOL APIENTRY DllMain(HINSTANCE hModule, DWORD dwReason, PVOID lpReserved)
{
    (void)hModule;
    (void)lpReserved;
    BOOL ret;

    logFileHandle = Real_CreateFileW(L"traces.json", // name of the write
        GENERIC_WRITE,          // open for writing
        0,                      // do not share
        NULL,                   // default security
        CREATE_ALWAYS,          // create always
        FILE_ATTRIBUTE_NORMAL,  // normal file
        NULL);                  // no attr. template

    if (DetourIsHelperProcess()) {
        return TRUE;
    }

    switch (dwReason) {
      case DLL_PROCESS_ATTACH:
        DetourRestoreAfterWith();
        OutputDebugStringA("trcapi" DETOURS_STRINGIFY(DETOURS_BITS) ".dll:"
                           " DllMain DLL_PROCESS_ATTACH\n");
        return ProcessAttach(hModule);
      case DLL_PROCESS_DETACH:
        ret = ProcessDetach(hModule);
        OutputDebugStringA("trcapi" DETOURS_STRINGIFY(DETOURS_BITS) ".dll:"
                           " DllMain DLL_PROCESS_DETACH\n");
        return ret;
      case DLL_THREAD_ATTACH:
        OutputDebugStringA("trcapi" DETOURS_STRINGIFY(DETOURS_BITS) ".dll:"
                           " DllMain DLL_THREAD_ATTACH\n");
        return ThreadAttach(hModule);
      case DLL_THREAD_DETACH:
        OutputDebugStringA("trcapi" DETOURS_STRINGIFY(DETOURS_BITS) ".dll:"
                           " DllMain DLL_THREAD_DETACH\n");
        return ThreadDetach(hModule);
    }
    return TRUE;
}
//
///////////////////////////////////////////////////////////////// End of File.
