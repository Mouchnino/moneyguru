ownerclass = 'MGDateRangeSelector'
ownerimport = 'MGDateRangeSelector.h'

result = View(None, 275, 22)
segments = SegmentedControl(result)
popup = Popup(result)

owner.dateRangePopUp = popup
owner.segmentedControl = segments

segments.segmentStyle = const.NSSegmentStyleTexturedRounded
segments.trackingMode = const.NSSegmentSwitchTrackingMomentary
s = segments.addSegment("", 25)
s.image = 'NSGoLeftTemplate'
s = segments.addSegment("", 217)
s.accessibilityDescription = "Placeholder for the date range menu"
s = segments.addSegment("", 25)
s.image = 'NSGoRightTemplate'
segments.action = Action(owner, 'segmentClicked')
segments.accessibilityDescription = "Date range buttons"
popup.pullsdown = True
popup.arrowPosition = const.NSPopUpArrowAtBottom
popup.bezelStyle = const.NSShadowlessSquareBezelStyle
popup.bordered = False
popup.alignment = TextAlignment.Center
popup.accessibilityDescription = "Date range type selector"
item = popup.menu.addItem("")
item.hidden = True
popup.menu.addItem("Month", action=Action(owner.model, 'selectMonthRange'))
popup.menu.addItem("Quarter", action=Action(owner.model, 'selectQuarterRange'))
popup.menu.addItem("Year", action=Action(owner.model, 'selectYearRange'))
popup.menu.addItem("Year to date", action=Action(owner.model, 'selectYearToDateRange'))
popup.menu.addItem("Running year", action=Action(owner.model, 'selectRunningYearRange'))
popup.menu.addItem("All transactions", action=Action(owner.model, 'selectAllTransactionsRange'))
popup.menu.addItem("Custom date range...", action=Action(owner.model, 'selectCustomDateRange'))
for i in range(3):
    item = popup.menu.addItem("", action=Action(owner, 'selectSavedCustomRange:'), tag=2000+i)
    item.hidden = True

popup.x = 30
popup.y = 0
popup.width = 212
popup.height = 23
