ownerclass = 'MGAppDelegate'
ownerimport = 'MGAppDelegate.h'

result = Window(442, 193, "moneyGuru Preferences")
autosaveIntervalLabel = Label(result, "Auto-save interval:")
autosaveIntervalField = TextField(result)
autosaveIntervalLabel2 = Label(result, "minute(s) (0 for none)")
fontSizeLabel = Label(result, "Font size:")
fontsizes = [str(i) for i in [11, 12, 13, 14, 18, 24]]
fontSizeCombo = Combobox(result, items=fontsizes)
printFontSizeLabel = Label(result, "Printing font size:")
printFontSizeCombo = Combobox(result, items=fontsizes)
scopeDialogBox = Checkbox(result, "Show scope dialog when modifying a scheduled transaction")
decimalPlacesBox = Checkbox(result, "Automatically place decimals when typing")
updatesBox = Checkbox(result, "Automatically check for updates")
debugBox = Checkbox(result, "Debug mode (restart required)")

owner.autoSaveIntervalField = autosaveIntervalField
owner.autoDecimalPlaceButton = decimalPlacesBox

result.canMinimize = result.canResize = False
defaultFont = Font('Lucida Grande', 12)
for label in [autosaveIntervalLabel, fontSizeLabel, printFontSizeLabel]:
    label.alignment = TextAlignment.Right
    label.width = 175
    label.font = defaultFont
for view in [autosaveIntervalLabel2, scopeDialogBox, decimalPlacesBox, updatesBox, debugBox]:
    view.font = defaultFont
autosaveIntervalField.formatter = NumberFormatter(NumberStyle.Decimal)
autosaveIntervalField.formatter.maximumFractionDigits = 0
fontSizeCombo.bind('value', defaults, 'values.TableFontSize')
printFontSizeCombo.bind('value', defaults, 'values.PrintFontSize')
scopeDialogBox.bind('value', owner, 'model.showScheduleScopeDialog')
updatesBox.bind('value', defaults, 'values.SUEnableAutomaticChecks')
debugBox.bind('value', defaults, 'values.DebugMode')

autosaveIntervalField.width = 43
fontSizeCombo.width = printFontSizeCombo.width = 66

layout = VHLayout([
    [autosaveIntervalLabel, autosaveIntervalField, autosaveIntervalLabel2],
    [fontSizeLabel, fontSizeCombo],
    [printFontSizeLabel, printFontSizeCombo],
    ], vmargin=4, hfillers={autosaveIntervalLabel2, })
layout.moveTo(Pack.UpperLeft)
layout.fill(Pack.Right)
layout2 = VLayout([scopeDialogBox, decimalPlacesBox, updatesBox, debugBox], margin=6)
layout2.moveNextTo(layout, Pack.Below, margin=8)
layout2.fill(Pack.Right)
