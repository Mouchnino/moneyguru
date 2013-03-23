/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSchedulePrint.h"
#import "MGConst.h"

@implementation MGSchedulePrint
- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"start_date",@"stop_date",@"amount",nil];
}
@end