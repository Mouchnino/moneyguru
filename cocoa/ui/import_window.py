ownerclass = 'MGImportWindow'
ownerimport = 'MGImportWindow.h'

result = Window(673, 414, "Import")
tabBarControl = View(result, 100, 22)
tabBarControl.OBJC_CLASS = 'PSMTabBarControl'
tabView = TabView(result)
importView = View(None, 622, 413)
targetLabel = Label(importView, "Target Account:")
targetPopup = Popup(importView)
importTable = TableView(importView)
importTable.OBJC_CLASS = 'MGTableView'
importButton = Button(importView, "Import")
swapBox = Box(importView, "Are some fields wrong? Swap them!")
swapPopup = Popup(swapBox, ["Day <--> Month", "Month <--> Year", "Day <--> Year",
    "Description <--> Payee", "Invert Amounts"])
swapAllCheckbox = Checkbox(swapBox, "Apply to all accounts")
swapButton = Button(swapBox, "Swap")

owner.applySwapToAllCheckbox = swapAllCheckbox
owner.importTableView = importTable
owner.mainView = importView
owner.swapButton = swapButton
owner.switchDateFieldsPopup = swapPopup
owner.tabBar = tabBarControl
owner.tabView = tabView
owner.targetAccountsPopup = targetPopup
tabBarControl.properties['tabView'] = tabView
tabBarControl.delegate = owner
tabView.delegate = tabBarControl

targetPopup.action = Action(owner, 'changeTargetAccount')
importButton.action = Action(owner, 'importSelectedPane')
swapPopup.action = Action(owner, 'selectSwapType')
swapButton.action = Action(owner, 'switchDateFields')

tabView.tabViewType = const.NSNoTabsNoBorder
importTable.alternatingRows = True
importTable.allowsColumnSelection = False
importTable.allowsColumnReordering = False
importTable.allowsMultipleSelection = True

swapBox.width = 297
swapBox.height = 78
swapButton.width = 73
targetLabel.width = 100
targetPopup.width = 170
importButton.width = 105

tabBarControl.moveTo(Pack.UpperLeft, margin=0)
tabBarControl.fill(Pack.Right, margin=0)
tabView.moveNextTo(tabBarControl, Pack.Below, margin=0)
tabView.fill(Pack.LowerRight, margin=0)
tabBarControl.setAnchor(Pack.UpperLeft, growX=True)
tabView.setAnchor(Pack.UpperLeft, growX=True, growY=True)

targetLabel.moveTo(Pack.UpperLeft)
targetPopup.moveNextTo(targetLabel, Pack.Right)
swapBox.moveNextTo(targetPopup, Pack.Right, align=Pack.Above)
swapBox.fill(Pack.Right)
importTable.moveNextTo(swapBox, Pack.Below)
importTable.fill(Pack.Left)
importTable.fill(Pack.Right)
importButton.moveNextTo(importTable, Pack.Below, align=Pack.Right, margin=12)
importTable.fill(Pack.Below)
importTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
importButton.setAnchor(Pack.LowerRight)

swapPopup.moveTo(Pack.UpperLeft)
swapPopup.fill(Pack.Right)
# The normal margin for a push button under a popup is way too large to fit in our box
swapButton.moveNextTo(swapPopup, Pack.Below, align=Pack.Right, margin=4)
swapAllCheckbox.moveNextTo(swapButton, Pack.Left)
swapAllCheckbox.fill(Pack.Left)
