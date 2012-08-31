ownerclass = 'MGDocPropsView'
ownerimport = 'MGDocPropsView.h'

result = View(None, 470, 180)
# See newtab_view.py for why we need a subview.
subview = View(result, result.width, result.height)
titleLabel = Label(subview, "Document Properties")
currencyLabel = Label(subview, "Native Currency:")
currencyCombo = Combobox(subview)
dowLabel = Label(subview, "First day of the week:")
dowPopup = Popup(subview)
aheadLabel = Label(subview, "Ahead months in Running Year:")
aheadPopup = Popup(subview)
yearStartLabel = Label(subview, "Year starts in:")
yearStartPopup = Popup(subview)

owner.mainResponder = currencyCombo
owner.currencyComboBoxView = currencyCombo
owner.firstWeekdayPopUpView = dowPopup
owner.aheadMonthsPopUpView = aheadPopup
owner.yearStartMonthPopUpView = yearStartPopup

titleLabel.font = Font("Lucida Grande", 14, [FontTrait.Bold])
titleLabel.alignment = TextAlignment.Center
for label in [currencyLabel, dowLabel, aheadLabel, yearStartLabel]:
    label.alignment = TextAlignment.Right
    label.width = 230

currencyCombo.width = 190
dowPopup.width = yearStartPopup.width = 110
aheadPopup.width = 66

layout = VHLayout([
    [titleLabel],
    [currencyLabel, currencyCombo],
    [dowLabel, dowPopup],
    [aheadLabel, aheadPopup],
    [yearStartLabel, yearStartPopup]
], vmargin=8)
layout.moveTo(Pack.UpperLeft)
layout.fill(Pack.LowerRight)

subview.setAnchor(Pack.Above)
