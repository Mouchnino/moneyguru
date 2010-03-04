/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSWindowController.h"
#import "PyAccountLookup.h"

@interface MGAccountLookup : HSWindowController {
    IBOutlet NSSearchField *searchField;
    IBOutlet NSTableView *namesTable;
    
    NSArray *currentNames;
}
- (id)initWithPyParent:(id)aPyParent;
- (PyAccountLookup *)py;

- (IBAction)go:(id)sender;
- (IBAction)updateQuery:(id)sender;
@end