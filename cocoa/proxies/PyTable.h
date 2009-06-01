#import <Cocoa/Cocoa.h>
#import "PyCompletion.h"

@interface PyTable : PyCompletion {}

- (void)add;
- (void)cancelEdits;
- (BOOL)canEditColumn:(NSString *)column atRow:(int)row;
- (void)changeColumns:(NSArray *)columns;
- (void)deleteSelectedRows;
- (int)numberOfRows;
- (void)saveEdits;
- (void)selectRows:(NSArray *)rows;
- (NSArray *)selectedRows;
- (void)setValue:(id)value forColumn:(NSString *)column row:(int)row;
- (id)valueForColumn:(NSString *)column row:(int)row;
@end
