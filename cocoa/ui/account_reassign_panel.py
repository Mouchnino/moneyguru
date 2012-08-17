ownerclass = 'MGAccountReassignPanel'
ownerimport = 'MGAccountReassignPanel.h'

result = Window(340, 160, "")
promptLabel = Label(result, "You're about to delete a non-empty account. Select an account to "
    "re-assign its transactions to.")
accountPopup = Popup(result, ["No Account"])
cancelButton = Button(result, "Cancel")
continueButton = Button(result, "Continue")

owner.accountSelector = accountPopup

result.canResize = result.canMinimize = False
cancelButton.keyEquivalent = '\\e'
continueButton.keyEquivalent = '\\r'
cancelButton.action = Action(owner, 'cancel:')
continueButton.action = Action(owner, 'save:')

promptLabel.height *= 3 # 3 lines
cancelButton.width = continueButton.width = 85
accountPopup.width = 215

promptLabel.moveTo(Pack.UpperLeft)
promptLabel.fill(Pack.Right)
accountPopup.moveNextTo(promptLabel, Pack.Below)
continueButton.moveNextTo(accountPopup, Pack.Below)
continueButton.moveTo(Pack.Right)
cancelButton.moveNextTo(continueButton, Pack.Left)
