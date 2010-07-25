/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTableWithColumns.h"
#import "PyImportWindow.h"

@interface PyImportTable : PyTableWithColumns {}
- (BOOL)canBindRow:(NSInteger)source to:(NSInteger)dest;
- (void)bindRow:(NSInteger)source to:(NSInteger)dest;
- (void)unbindRow:(NSInteger)row;
- (BOOL)isTwoSided;
- (void)toggleImportStatus;
@end