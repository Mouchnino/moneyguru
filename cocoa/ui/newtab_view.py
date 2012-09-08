ownerclass = 'MGEmptyView'
ownerimport = 'MGEmptyView.h'

BUTTONS_DATA = [
    # title, imgname, action
    ("Net Worth", 'balance_sheet_48', 'selectNetWorthView'),
    ("Profit & Loss", 'income_statement_48', 'selectProfitView'),
    ("Transactions", 'transaction_table_48', 'selectTransactionView'),
    ("General Ledger", 'gledger_48', 'selectGeneralLedgerView'),
    ("Schedules", 'schedules_48', 'selectScheduleView'),
    ("Budgets", 'budget_48', 'selectBudgetView'),
    ("Cashculator", 'cashculator_48', 'selectCashculatorView'),
    ("Document Properties", 'gledger_48', 'selectDocPropsView'),
]
BUTTON_LABEL_FONT = Font("Lucida Grande", 24)
BUTTON_FONT = Font("Lucida Grande", 14, [FontTrait.Bold])

result = View(None, 560, 470)
# We need a non-resizable subview inside our main view so that our buttons anchor correctly. Because
# we want to anchor everything in the middle horizontally, we need that. If we were, for example, to
# not use this view and set all views' anchors to Pack.Above, the distance between our views
# wouldn't stay constant and we don't want that.
subview = View(result, result.width, result.height)
promptLabel = Label(subview, "Choose a view for this tab")
buttons = [] # label, button
for index, (title, imgname, action) in enumerate(BUTTONS_DATA, start=1):
    label = Label(subview, NLSTR("{}.".format(index)))
    label.font = BUTTON_LABEL_FONT
    label.width = 26
    label.height = 30
    button = Button(subview, title, action=Action(owner, action))
    button.font = BUTTON_FONT
    button.image = imgname
    button.imagePosition = const.NSImageLeft
    button.bezelStyle = const.NSRegularSquareBezelStyle
    button.shortcut = str(index)
    button.width = 215
    button.height = 53
    buttons.append((label, button))
pluginsLabel = Label(subview, "Plugins (double-click to open)")
pluginsTable = ListView(subview)

owner.mainResponder = result
owner.pluginTableView = pluginsTable

promptLabel.alignment = pluginsLabel.alignment = TextAlignment.Center
pluginsTable.width = 280
pluginsTable.fixedWidth = True

subview.x = subview.y = 0
# We insert a None in the middle to leave a bit more space than default margins. This space doesn't
# grow with the view because our `subview` has a fixed size.
buttonLayout = VHLayout([
    list(buttons[0] + (None, ) + buttons[4]),
    list(buttons[1] + (None, ) + buttons[5]),
    list(buttons[2] + (None, ) + buttons[6]),
    list(buttons[3] + (None, ) + buttons[7]),
    ])
layout = VLayout([promptLabel, buttonLayout, pluginsLabel, pluginsTable], filler=pluginsTable, align=Pack.Middle)
layout.moveTo(Pack.UpperLeft)
layout.fill(Pack.LowerRight)

subview.setAnchor(Pack.Above)
