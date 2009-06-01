#import <Cocoa/Cocoa.h>
#import "MGOutline.h"
#import "PyReport.h"


@interface MGReport : MGOutline {

}
- (PyReport *)py;

- (void)add;
- (void)addGroup;
- (void)deleteSelected;
- (IBAction)showSelectedAccount:(id)sender;
- (BOOL)canShowSelectedAccount;
@end
