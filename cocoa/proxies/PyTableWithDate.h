#import <Cocoa/Cocoa.h>
#import "PyTable.h"

@interface PyTableWithDate : PyTable {}

- (BOOL)isEditedRowInTheFuture;
- (BOOL)isEditedRowInThePast;
@end
