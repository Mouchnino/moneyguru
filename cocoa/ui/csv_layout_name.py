ownerclass = 'MGCSVLayoutNameDialog'
ownerimport = 'MGCSVLayoutNameDialog.h'

result = Window(283, 115, "Layout Name")
promptLabel = Label(result, "Layout Name:")
nameField = TextField(result, "")
cancelButton = Button(result, "Cancel")
okButton = Button(result, "OK")

owner.nameTextField = nameField

result.canResize = result.canMinimize = False
cancelButton.keyEquivalent = '\\e'
okButton.keyEquivalent = '\\r'
cancelButton.action = Action(owner, 'cancel')
okButton.action = Action(owner, 'ok')

cancelButton.width = okButton.width = 85

promptLabel.moveTo(Pack.UpperLeft)
promptLabel.fill(Pack.Right)
nameField.moveNextTo(promptLabel, Pack.Below)
nameField.fill(Pack.Right)
okButton.moveNextTo(nameField, Pack.Below, align=Pack.Right)
cancelButton.moveNextTo(okButton, Pack.Left)
