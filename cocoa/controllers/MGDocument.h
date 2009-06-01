#import <Cocoa/Cocoa.h>
#import "PyDocument.h"

@interface MGDocument : NSDocument
{
    PyDocument *py;
}

- (PyDocument *)py;

/* Actions */
- (IBAction)import:(id)sender;
- (IBAction)saveToQIF:(id)sender;

/* Private */
- (void)registerDefaults;

/* Misc */
- (void)selectMonthRange;
- (void)selectQuarterRange;
- (void)selectYearRange;
- (void)selectYearToDateRange;
- (void)selectRunningYearRange;
- (void)selectCustomDateRange;
- (void)stopEdition;
- (NSString *)documentDefaultsKey;
- (id)defaultForKey:(NSString *)aKey;
- (void)setDefault:(id)aDefault forKey:(NSString *)aKey;

/* Python -> Cocoa */

- (int)confirmUnreconciliation:(int)affectedSplitCount;
- (BOOL)queryForScheduleScope;
@end
