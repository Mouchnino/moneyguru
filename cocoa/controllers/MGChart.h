#import <Cocoa/Cocoa.h>
#import "MGGUIController.h"
#import "MGChartView.h"
#import "PyChart.h"

@interface MGChart : MGGUIController {
    MGChartView *view;
}
- (MGChartView *)view;
- (PyChart *)py;

/* Python callbacks */
- (void)refresh;
@end
