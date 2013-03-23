/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "PyDateRangeSelector.h"

@interface MGDateRangeSelector : HSGUIController <NSAnimationDelegate>
{
    NSPopUpButton *dateRangePopUp;
    NSSegmentedControl *segmentedControl;
    
    NSArray *customRangeItems;
}

@property (readwrite, retain) NSPopUpButton *dateRangePopUp;
@property (readwrite, retain) NSSegmentedControl *segmentedControl;

- (id)initWithPyRef:(PyObject *)aPyRef;

/* Virtual */
- (PyDateRangeSelector *)model;

/* Public */
- (void)animate:(BOOL)forward;

/* Actions */
- (void)segmentClicked;
- (void)selectSavedCustomRange:(id)sender;
@end