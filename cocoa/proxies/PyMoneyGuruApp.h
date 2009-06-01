#import <Cocoa/Cocoa.h>
#import "PyRegistrable.h"

@interface PyMoneyGuruApp : PyRegistrable {}

- (id)initWithCocoa:(id)cocoa;
- (void)free;

/* Preferences */
- (int)firstWeekday; // 0 = monday, 6 = sunday
- (void)setFirstWeekday:(int)weekday;
- (int)aheadMonths;
- (void)setAheadMonths:(int)months;
- (BOOL)dontUnreconcile;
- (void)setDontUnreconcile:(BOOL)flag;
@end