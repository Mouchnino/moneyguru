ownerclass = 'MGCashculatorView'
ownerimport = 'MGCashculatorView.h'

result = View(None, 550, 340)
titleLabel = Label(result, "Export accounts to Cashculator")
promptLabel = Label(result, "Please read instructions in the Forecast section of the help file.")
accountTable = TableView(result)
accountTable.OBJC_CLASS = 'MGTableView'
exportButton = Button(result, "Export Accounts", action=Action(owner.model, 'exportDB'))
launchButton = Button(result, "Launch Cashculator", action=Action(owner.model, 'launchCC'))

owner.mainResponder = result
owner.accountTableView = accountTable

titleLabel.font = Font("Lucida Grande", 14, [FontTrait.Bold])
accountTable.allowsColumnReordering = False
accountTable.allowsColumnResizing = True
accountTable.allowsColumnSelection = False
accountTable.allowsEmptySelection = True
accountTable.allowsMultipleSelection = False
accountTable.allowsTypeSelect = False
accountTable.alternatingRows = True

launchButton.width = 152
exportButton.width = 132

layout = VHLayout([
    [titleLabel],
    [promptLabel],
    [accountTable],
    [None, exportButton, launchButton],
    ], vfiller=accountTable)
layout.moveTo(Pack.UpperLeft)
layout.fill(Pack.LowerRight)
layout.setAnchor(Pack.Left, growX=True)
