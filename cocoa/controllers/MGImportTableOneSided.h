#import <Cocoa/Cocoa.h>
#import "PyImportTable.h"
#import "PyImportWindow.h"
#import "MGEditableTable.h"

@interface MGImportTableOneSided : MGEditableTable {}
- (id)initWithImportWindow:(PyImportWindow *)aWindow;
- (PyImportTable *)py;
@end