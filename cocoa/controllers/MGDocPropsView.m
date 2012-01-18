/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGDocPropsView.h"
#import "Utils.h"

@implementation MGDocPropsView
- (id)initWithPy:(id)aPy
{
    self = [super initWithPy:aPy];
    [NSBundle loadNibNamed:@"DocProps" owner:self];
    currencyComboBox = [[HSComboBox alloc] initWithPy:[[self py] currencyList] view:currencyComboBoxView];
    firstWeekdayPopUp = [[HSPopUpList alloc] initWithPy:[[self py] firstWeekdayList] view:firstWeekdayPopUpView];
    aheadMonthsPopUp = [[HSPopUpList alloc] initWithPy:[[self py] aheadMonthsList] view:aheadMonthsPopUpView];
    yearStartMonthPopUp = [[HSPopUpList alloc] initWithPy:[[self py] yearStartMonthList] view:yearStartMonthPopUpView];
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

- (PyDocPropsView *)py
{
    return (PyDocPropsView *)py;
}
@end