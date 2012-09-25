ownerclass = 'MGMainWindowController'
ownerimport = 'MGMainWindowController.h'

result = Window(800, 600, "moneyGuru")
result.OBJC_CLASS = 'MGMainWindow'
tabBar = View(result, 800, 22)
tabBar.OBJC_CLASS = 'PSMTabBarControl'
tabView = TabView(result)
actionSegments = SegmentedControl(result)
visibilitySegments = SegmentedControl(result)
statusLabel = Label(result, NLSTR("Status"))

owner.tabView = tabView
owner.tabBar = tabBar
owner.statusLabel = statusLabel
owner.visibilitySegments = visibilitySegments
tabBar.properties['tabView'] = tabView
tabBar.delegate = owner
tabView.delegate = tabBar

result.minSize = Size(600, 300)
result.autosaveName = 'MainWindow'
tabView.tabViewType = const.NSNoTabsNoBorder
actionSegments.segmentStyle = visibilitySegments.segmentStyle = const.NSSegmentStyleCapsule
actionSegments.trackingMode = const.NSSegmentSwitchTrackingMomentary
visibilitySegments.trackingMode = const.NSSegmentSwitchTrackingSelectAny
actionSegments.action = Action(owner, 'itemSegmentClicked:')
visibilitySegments.action = Action(owner, 'toggleAreaVisibility:')
s = actionSegments.addSegment("", 27)
s.image = 'NSAddTemplate'
s.accessibilityDescription = "New Item"
s = actionSegments.addSegment("", 27)
s.image = 'NSRemoveTemplate'
s.accessibilityDescription = "Delete Selected"
s = actionSegments.addSegment("", 27)
s.image = 'info_gray_12'
s.accessibilityDescription = "Edit Selected"
s = visibilitySegments.addSegment("", 27)
s.image = 'graph_visibility_on_16'
s.accessibilityDescription = "Toggle Graph"
s = visibilitySegments.addSegment("", 27)
s.image = 'piechart_visibility_on_16'
s.accessibilityDescription = "Toggle Pie Chart"
s = visibilitySegments.addSegment("", 27)
s.image = 'columns_16'
s.accessibilityDescription = "Toggle Columns"
statusLabel.alignment = TextAlignment.Center
statusLabel.accessibilityDescription = "Status label"

layout = VHLayout([
    [tabBar],
    [tabView],
    [actionSegments, visibilitySegments, statusLabel],
    ], hfillers={statusLabel, }, vfiller=tabView, vmargin=0)
# The only place where we need a vertical margin is at the bottom. This is why we manually set the
# layout's height. We also need to offset the bottom layout a bit to the right. All of this is a bit
# hacky, but it's still less complicated than doing it without layouts.
bottomLayout = layout.subviews[-1]
bottomLayout.height = 28
layout.fillAll(margin=0)
bottomRect = bottomLayout.rect
bottomRect.x = 7
bottomLayout.moveInsideRect(bottomRect)
layout.setAnchor(Pack.Left, growX=True)
