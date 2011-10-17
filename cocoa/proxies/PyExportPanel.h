/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPanel.h"
#import "PyTable.h"

@interface PyExportPanel : PyPanel {}
- (PyTable *)accountTable;
- (BOOL)exportAll;
- (void)setExportAll:(BOOL)value;
- (NSString *)exportPath;
- (void)setExportPath:(NSString *)value;
- (NSInteger)exportFormat;
- (void)setExportFormat:(NSInteger)value;
- (BOOL)currentDateRangeOnly;
- (void)setCurrentDateRangeOnly:(BOOL)value;
@end