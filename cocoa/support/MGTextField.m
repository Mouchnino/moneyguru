#import "MGTextField.h"

@implementation MGTextField

- (NSString *)fieldEditor:(MGFieldEditor *)fieldEditor wantsCompletionFor:(NSString *)text
{
    return [[self delegate] autoCompletionForTextField:self partialWord:text];
}

- (NSString *)fieldEditorWantsCurrentValue:(MGFieldEditor *)fieldEditor
{
    return [[self delegate] currentValueForTextField:self];
}

- (NSString *)fieldEditorWantsNextValue:(MGFieldEditor *)fieldEditor
{
    return [[self delegate] nextValueForTextField:self];
}

- (NSString *)fieldEditorWantsPrevValue:(MGFieldEditor *)fieldEditor
{
    return [[self delegate] prevValueForTextField:self];
}

@end
