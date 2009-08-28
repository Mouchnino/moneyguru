/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSchedulePrint.h"

@implementation MGSchedulePrint
+ (NSString *)pyClassName
{
    return @"PyPrintView";
}

- (PyPrintView *)py
{
    return (PyPrintView *)py;
}

- (NSString *)pageTitle
{
    return [NSString stringWithFormat:@"Schedules from %@ to %@",[py startDate],[py endDate]];
}

- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"start_date",@"stop_date",@"amount",nil];
}
@end