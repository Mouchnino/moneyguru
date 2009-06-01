#import <Cocoa/Cocoa.h>
#import "PyDateWidget.h"

/* IMPORTANT NOTE

MGDateFieldEditor used to be a separate class, but it turns out that Tiger is very picky about
the field editor you give it. If you don't always give it the same editor for a given control, all
hell breaks loose. When Leopard only is supported, we can break this class in 2 again.

*/
@interface MGFieldEditor : NSTextView
{
    PyDateWidget *pyDate;
    BOOL dateMode;
}
- (void)completeWith:(NSString *)proposition;
- (void)replaceWith:(NSString *)text;
- (void)dateRefresh;

- (BOOL)dateMode;
- (void)setDateMode:(BOOL)aDateMode;
@end

@interface NSObject(MGFieldEditorDelegate)
- (NSString *)fieldEditor:(MGFieldEditor *)fieldEditor wantsCompletionFor:(NSString *)text;
- (NSString *)fieldEditorWantsCurrentValue:(MGFieldEditor *)fieldEditor;
- (NSString *)fieldEditorWantsPrevValue:(MGFieldEditor *)fieldEditor;
- (NSString *)fieldEditorWantsNextValue:(MGFieldEditor *)fieldEditor;
@end
