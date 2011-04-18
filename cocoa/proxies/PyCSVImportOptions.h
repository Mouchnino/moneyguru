/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyCSVImportOptions : PyGUI {}
- (NSString *)columnNameAtIndex:(NSInteger)index;
- (void)continueImport;
- (void)deleteSelectedLayout;
- (NSString *)fieldSeparator;
- (NSArray *)layoutNames;
- (BOOL)lineIsImported:(NSInteger)index;
- (NSInteger)numberOfColumns;
- (NSInteger)numberOfLines;
- (void)newLayout:(NSString *)name;
- (void)renameSelectedLayout:(NSString *)name;
- (void)rescan;
- (NSString *)selectedLayoutName;
- (NSInteger)selectedTargetIndex;
- (void)selectLayout:(NSString *)name;
- (void)setColumn:(NSInteger)index fieldForTag:(NSInteger)tag;
- (void)setEncodingIndex:(NSInteger)aIndex;
- (void)setFieldSeparator:(NSString *)fieldSep;
- (void)setSelectedTargetIndex:(NSInteger)aIndex;
- (NSArray *)supportedEncodings;
- (NSArray *)targetAccountNames;
- (void)toggleLineExclusion:(NSInteger)index;
- (NSString *)valueForRow:(NSInteger)row column:(NSInteger)column;
@end