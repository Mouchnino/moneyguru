#import <Cocoa/Cocoa.h>

// We don't subclass the PyGUI class because we don't need the whole connect/disconnect/callback
// mechanism of the normal GUI objects (it's a one shot object)
@interface PyPrintView : NSObject {}
- (id)initWithPyParent:(id)pyParent;

- (NSString *)startDate;
- (NSString *)endDate;
@end