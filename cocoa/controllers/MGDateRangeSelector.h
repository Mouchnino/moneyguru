/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "PyDateRangeSelector.h"

@interface MGDateRangeSelector : HSGUIController <NSAnimationDelegate>
{
    IBOutlet NSView *linkedView;
    IBOutlet NSPopUpButton *dateRangePopUp;
    IBOutlet NSSegmentedControl *segmentedControl;
    
    NSArray *customRangeItems;
}
- (id)initWithPyParent:(id)aPyParent;

/* Virtual */
- (PyDateRangeSelector *)py;

/* Public */
- (void)animate:(BOOL)forward;

/* Actions */
- (IBAction)segmentClicked:(id)sender;
- (IBAction)selectMonthRange:(id)sender;
- (IBAction)selectNextDateRange:(id)sender;
- (IBAction)selectPrevDateRange:(id)sender;
- (IBAction)selectTodayDateRange:(id)sender;
- (IBAction)selectQuarterRange:(id)sender;
- (IBAction)selectYearRange:(id)sender;
- (IBAction)selectYearToDateRange:(id)sender;
- (IBAction)selectRunningYearRange:(id)sender;
- (IBAction)selectAllTransactionsRange:(id)sender;
- (IBAction)selectCustomDateRange:(id)sender;
- (IBAction)selectSavedCustomRange:(id)sender;
@end