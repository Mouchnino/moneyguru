/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGDocPropsView.h"
#import "Utils.h"

@implementation MGDocPropsView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyDocPropsView *m = [[PyDocPropsView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    [NSBundle loadNibNamed:@"DocProps" owner:self];
    currencyComboBox = [[HSComboBox alloc] initWithPyRef:[[self model] currencyList] view:currencyComboBoxView];
    firstWeekdayPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] firstWeekdayList] popupView:firstWeekdayPopUpView];
    aheadMonthsPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] aheadMonthsList] popupView:aheadMonthsPopUpView];
    yearStartMonthPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] yearStartMonthList] popupView:yearStartMonthPopUpView];
    return self;
}
        
- (void)dealloc
{
    [currencyComboBox release];
    [firstWeekdayPopUp release];
    [aheadMonthsPopUp release];
    [yearStartMonthPopUp release];
    [super dealloc];
}

- (PyDocPropsView *)model
{
    return (PyDocPropsView *)model;
}
@end