#import <Cocoa/Cocoa.h>

@interface MGReconciliationCell : NSButtonCell 
{
    BOOL canReconcile;
    BOOL reconciled;
    BOOL recurrent;
    BOOL isInFuture;
    BOOL isInPast;
}

- (void)setCanReconcile:(BOOL)aCanReconcile;
- (void)setReconciled:(BOOL)aReconciled;
- (void)setReconciliationPending:(BOOL)aReconciliationPending;
- (void)setRecurrent:(BOOL)aRecurrent;
- (void)setIsInFuture:(BOOL)aIsInFuture;
- (void)setIsInPast:(BOOL)aIsInPast;
@end