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

- (int)splitCountThreshold
{
    return 3;
}
@end