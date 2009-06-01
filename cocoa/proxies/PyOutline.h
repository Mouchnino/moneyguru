#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyOutline : PyGUI
- (void)cancelEdits;
- (BOOL)canEditProperty:(NSString *)property atPath:(NSArray *)path;
- (void)saveEdits;
- (NSArray *)selectedPath;
- (void)setSelectedPath:(NSArray *)path;
- (id)property:(NSString *)property valueAtPath:(NSArray *)path;
- (void)setProperty:(NSString *)property value:(id)value atPath:(NSArray *)path;
@end
