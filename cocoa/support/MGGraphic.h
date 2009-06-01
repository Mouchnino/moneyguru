
#define SIMPLE_LINE(x1, y1, x2, y2, width)\
{\
NSBezierPath *path = [NSBezierPath bezierPath];\
[path moveToPoint:NSMakePoint(x1, y1)];\
[path lineToPoint:NSMakePoint(x2, y2)];\
[path setLineWidth:width];\
[path stroke];\
}
