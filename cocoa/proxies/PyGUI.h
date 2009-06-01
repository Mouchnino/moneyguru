#import <Cocoa/Cocoa.h>

@interface PyGUI : NSObject {}
- (id)initWithCocoa:(id)cocoa pyParent:(id)pyParent;
- (void)connect;
- (void)disconnect;
- (void)free;
@end;