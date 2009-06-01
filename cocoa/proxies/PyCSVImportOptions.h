#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyCSVImportOptions : PyGUI {}
- (NSString *)columnNameAtIndex:(int)index;
- (void)continueImport;
- (void)deleteSelectedLayout;
- (NSArray *)layoutNames;
- (BOOL)lineIsImported:(int)index;
- (int)numberOfColumns;
- (int)numberOfLines;
- (void)newLayout:(NSString *)name;
- (void)renameSelectedLayout:(NSString *)name;
- (NSString *)selectedLayoutName;
- (int)selectedTargetIndex;
- (void)selectLayout:(NSString *)name;
- (void)setColumn:(int)index fieldForTag:(int)tag;
- (void)setSelectedTargetIndex:(int)aIndex;
- (NSArray *)targetAccountNames;
- (void)toggleLineExclusion:(int)index;
- (NSString *)valueForRow:(int)row column:(int)column;
@end