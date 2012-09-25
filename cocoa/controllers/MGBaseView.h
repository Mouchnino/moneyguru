/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "MGPrintView.h"
#import "PyBaseView.h"
#import "MGTableView.h"

@interface MGBaseView : HSGUIController
{
    NSResponder *mainResponder;
}

@property (readwrite, retain) NSResponder *mainResponder;

- (PyBaseView *)model;
- (MGPrintView *)viewToPrint;
- (NSString *)tabIconName;
- (void)applySubviewsSizeRestoration;
- (void)setupTableView:(MGTableView *)aTableView;

/* Notifications */
- (void)viewFrameChanged:(NSNotification *)aNotification;

/* model --> view */
- (void)updateVisibility;
@end
