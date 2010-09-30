/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGTransactionPrint.h"
#import "MGConst.h"

@implementation MGTransactionPrint
+ (NSString *)pyClassName
{
    return @"PyTransactionPrint";
}

- (PyTransactionPrint *)py
{
    return (PyTransactionPrint *)py;
}

- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"status",@"date",@"amount",nil];
}

- (NSArray *)accountColumnNames
{
    return [NSArray arrayWithObjects:@"from",@"to",nil];
}

- (NSInteger)splitCountThreshold
{
    return 3;
}
@end