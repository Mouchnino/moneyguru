#import <Cocoa/Cocoa.h>
#import "PyImportTable.h"
#import "PyImportWindow.h"
#import "MGEditableTable.h"

@interface MGImportTable : MGEditableTable {}
- (id)initWithImportWindow:(PyImportWindow *)aWindow;
- (PyImportTable *)py;

- (IBAction)bindLockClick:(id)sender;
@end