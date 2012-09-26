ownerclass = 'MGRecurrenceScopeDialog'
ownerimport = 'MGRecurrenceScopeDialog.h'

result = Window(442, 172, "Modification Scope")
promptLabel = Label(result, "Do you want this change to affect all future occurrences of this "
    "transaction?")
subLabel = Label(result, "You can force global scope (in other words, changing all future "
    "occurences) by holding ⇧ when you perform the change.")
showNextTimeBox = Checkbox(result, "Show this dialog next time")
localScopeButton = Button(result, "Just this one")
globalScopeButton = Button(result, "All future occurences")
cancelButton = Button(result, "Cancel")

result.canClose = result.canResize = result.canMinimize = False
subLabel.controlSize = ControlSize.Small
showNextTimeBox.controlSize = ControlSize.Small
showNextTimeBox.state = const.NSOnState
cancelButton.keyEquivalent = '\\e'
localScopeButton.keyEquivalent = '\\r'
cancelButton.action = Action(owner, 'cancel')
localScopeButton.action = Action(owner, 'chooseLocalScope')
globalScopeButton.action = Action(owner, 'chooseGlobalScope')
showNextTimeBox.bind('value', owner, 'showDialogNextTime')

promptLabel.height *= 2 # 2 lines
subLabel.height *= 2 # 2 lines
cancelButton.width = 83
globalScopeButton.width = 152
localScopeButton.width = 107

mainLayout = VLayout([promptLabel, subLabel, showNextTimeBox])
buttonLayout = HLayout([cancelButton, None, globalScopeButton, localScopeButton])
mainLayout.packToCorner(Pack.UpperLeft)
mainLayout.fill(Pack.Right)
buttonLayout.packRelativeTo(showNextTimeBox, Pack.Below)
buttonLayout.fill(Pack.Right)
