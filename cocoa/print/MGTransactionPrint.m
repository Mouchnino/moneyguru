/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTransactionPrint.h"

@implementation MGTransactionPrint
+ (NSString *)pyClassName
{
    return @"PyTransactionPrint";
}

- (PyTransactionPrint *)py
{
    return (PyTransactionPrint *)py;
}

- (NSString *)pageTitle
{
    return [NSString stringWithFormat:@"Transactions from %@ to %@",[py startDate],[py endDate]];
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