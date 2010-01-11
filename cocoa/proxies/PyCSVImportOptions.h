/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyCSVImportOptions : PyGUI {}
- (NSString *)columnNameAtIndex:(int)index;
- (void)continueImport;
- (void)deleteSelectedLayout;
- (NSString *)fieldSeparator;
- (NSArray *)layoutNames;
- (BOOL)lineIsImported:(int)index;
- (int)numberOfColumns;
- (int)numberOfLines;
- (void)newLayout:(NSString *)name;
- (void)renameSelectedLayout:(NSString *)name;
- (void)rescan;
- (NSString *)selectedLayoutName;
- (int)selectedTargetIndex;
- (void)selectLayout:(NSString *)name;
- (void)setColumn:(int)index fieldForTag:(int)tag;
- (void)setFieldSeparator:(NSString *)fieldSep;
- (void)setSelectedTargetIndex:(int)aIndex;
- (NSArray *)targetAccountNames;
- (void)toggleLineExclusion:(int)index;
- (NSString *)valueForRow:(int)row column:(int)column;
@end