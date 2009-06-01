#import <Cocoa/Cocoa.h>
#import "PyTable.h"
#import "PyImportWindow.h"

@interface PyImportTable : PyTable {}
- (BOOL)canBindRow:(int)source to:(int)dest;
- (void)bindRow:(int)source to:(int)dest;
- (void)unbindRow:(int)row;
@end