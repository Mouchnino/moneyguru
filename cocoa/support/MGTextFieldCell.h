#import <Cocoa/Cocoa.h>

@interface MGTextFieldCell : NSTextFieldCell {
    BOOL hasArrow;
    BOOL hasDarkBackground;
    int indent;
    id arrowTarget;
    SEL arrowAction;
    NSString *buttonImageName;
    id buttonTarget;
    SEL buttonAction;
}
- (void)setHasDarkBackground:(BOOL)value;
- (void)setIndent:(int)value;
// If we use the NSCell's target and action, that action is triggered wherever the cell is clicked on Tiger
- (void)setHasArrow:(BOOL)value;
- (void)setArrowTarget:(id)value;
- (void)setArrowAction:(SEL)value;
// the cell's button is a little image showing at the right of the cell (but at the left of the arrow)
// set it to nil to not show anything
- (void)setButtonImageName:(NSString *)aImageName;
- (void)setButtonTarget:(id)value;
- (void)setButtonAction:(SEL)value;
@end
