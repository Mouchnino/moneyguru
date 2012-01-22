/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyDocPropsView.h"
#import "MGBaseView.h"
#import "HSPopUpList2.h"
#import "HSComboBox2.h"

@interface MGDocPropsView : MGBaseView
{
    IBOutlet NSComboBox *currencyComboBoxView;
    IBOutlet NSPopUpButton *firstWeekdayPopUpView;
    IBOutlet NSPopUpButton *aheadMonthsPopUpView;
    IBOutlet NSPopUpButton *yearStartMonthPopUpView;
    
    HSComboBox2 *currencyComboBox;
    HSPopUpList2 *firstWeekdayPopUp;
    HSPopUpList2 *aheadMonthsPopUp;
    HSPopUpList2 *yearStartMonthPopUp;
}
- (id)initWithPy:(id)aPy;
- (PyDocPropsView *)model;
@end