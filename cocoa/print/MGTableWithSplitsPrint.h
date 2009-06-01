#import <Cocoa/Cocoa.h>
#import "MGTablePrint.h"
#import "PySplitPrint.h"

@interface MGTableWithSplitsPrint : MGTablePrint
{
    NSFont *splitFont;
    NSDictionary *splitAttributes;
    float splitTextHeight;
    float splitHeight;
}

- (PySplitPrint *)py;

- (NSArray *)accountColumnNames;
- (int)splitCountThreshold;
@end