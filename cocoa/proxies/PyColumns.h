/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTable.h"

@interface PyColumns : PyTable {}
- (NSArray *)columnNamesInOrder;
- (NSInteger)columnWidth:(NSString *)colName;
- (BOOL)columnIsVisible:(NSString *)colName;
- (void)moveColumn:(NSString *)colName toIndex:(NSInteger)index;
- (void)resizeColumn:(NSString *)colName toWidth:(NSInteger)newWidth;
@end
