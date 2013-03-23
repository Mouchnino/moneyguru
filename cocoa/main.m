/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Python.h>
#import <wchar.h>
#import <locale.h>
#import "HSPyUtil.h"
#import "MGMainMenu_UI.h"
#import "MGAppDelegate.h"

int main(int argc, char *argv[])
{
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    setCocoaViewsModuleName(@"CocoaViews");
    /* We have to set the locate to UTF8 for mbstowcs() to correctly convert non-ascii chars in paths */
    setlocale(LC_ALL, "en_US.UTF-8");
    NSString *respath = [[NSBundle mainBundle] resourcePath];
    NSString *mainpy = [respath stringByAppendingPathComponent:@"mg_cocoa.py"];
    wchar_t wPythonPath[PATH_MAX+1];
    NSString *pypath = [respath stringByAppendingPathComponent:@"py"];
    mbstowcs(wPythonPath, [pypath fileSystemRepresentation], PATH_MAX+1);
    Py_SetPath(wPythonPath);
    Py_SetPythonHome(wPythonPath);
    Py_Initialize();
    PyEval_InitThreads();
    PyGILState_STATE gilState = PyGILState_Ensure();
    FILE* fp = fopen([mainpy UTF8String], "r");
    PyRun_SimpleFile(fp, [mainpy UTF8String]);
    fclose(fp);
    PyGILState_Release(gilState);
    if (gilState == PyGILState_LOCKED) {
        PyThreadState_Swap(NULL);
        PyEval_ReleaseLock();
    }
    
    [NSApplication sharedApplication];
    MGAppDelegate *appDelegate = [[MGAppDelegate alloc] init];
    [NSApp setDelegate:appDelegate];
    [NSApp setMainMenu:createMGMainMenu_UI(appDelegate)];
    [appDelegate finalizeInit];
    [pool release];
    [NSApp run];
    Py_Finalize();
    return 0;
}
