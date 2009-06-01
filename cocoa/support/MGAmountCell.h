#import <Cocoa/Cocoa.h>


@interface MGAmountCell : NSTextFieldCell {
    BOOL total;
    BOOL subtotal;
}
- (void)setTotal:(BOOL)value;
- (void)setSubtotal:(BOOL)value;
@end
