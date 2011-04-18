/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSWindowController.h"
#import "PyLookup.h"

@interface MGLookup : HSWindowController {
    IBOutlet NSSearchField *searchField;
    IBOutlet NSTableView *namesTable;
    
    NSArray *currentNames;
}
- (id)initWithClassName:(NSString *)aClassName pyParent:(id)aPyParent;
- (PyLookup *)py;

- (IBAction)go:(id)sender;
- (IBAction)updateQuery:(id)sender;
@end