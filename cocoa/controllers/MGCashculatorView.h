/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyCashculatorView.h"
#import "MGBaseView2.h"
#import "MGCashculatorAccountTable.h"

@interface MGCashculatorView : MGBaseView2
{
    IBOutlet MGTableView *accountTableView;
    
    MGCashculatorAccountTable *accountTable;
}
- (id)initWithPy:(id)aPy;
- (PyCashculatorView *)model;

- (IBAction)exportDB:(id)sender;
- (IBAction)launchCC:(id)sender;
@end