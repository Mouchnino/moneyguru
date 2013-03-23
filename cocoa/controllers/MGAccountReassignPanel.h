/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGPanel.h"
#import "HSPopUpList.h"
#import "PyAccountReassignPanel.h"

@class MGMainWindowController;

@interface MGAccountReassignPanel : MGPanel {
    NSPopUpButton *accountSelector;
    
    HSPopUpList *accountPopUp;
}

@property (readwrite, retain) NSPopUpButton *accountSelector;

- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyAccountReassignPanel *)model;
@end