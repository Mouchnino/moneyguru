/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyLookup.h"

@interface MGLookup : NSWindowController {
    IBOutlet NSSearchField *searchField;
    IBOutlet NSTableView *namesTable;
    
    PyLookup *model;
    NSArray *currentNames;
}
- (id)initWithPyRef:(PyObject *)aPyRef;

- (IBAction)go:(id)sender;
- (IBAction)updateQuery:(id)sender;
@end