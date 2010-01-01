/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
